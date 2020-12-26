#!/usr/bin/python3

from collections import OrderedDict
import os
import sys

def help(rc: int=0):
    print("The pedtodot.py script transforms a pedigree file into a dot file that Graphiz can use to create a graph.")
    print("")
    print("\t-h:                         This help message.")
    print("\t-f --file:                  The pedigree file to read [default: /home/bert/Documents/DropBox/banded.txt]")
    print("\t-o --output:                The output file [default: the pedigree file with the .dot extention instead]")
    print("\t-a --ancestor <ancestor>:   Limit to individuals with this ancestor.")
    print("\t-p --pedigree <individual>: Limit to the pedigree of this individual.")
    print("\t-c --center <individual>:   Combine -a and -p: both offspring and pedigree.")
    print("")
    sys.exit(rc)

def write_dot(filename: str, pedigree: dict):
    with open(filename, 'w') as dot:
        dot.write("digraph PEDIGREE {\n")
        dot.write("  rankdir=LR;\n")
        for individual, parents in pedigree.items():
            for parent in parents:
                dot.write("  \"%s\" -> \"%s\"\n" % (parent, individual))
        dot.write("}\n")

def _filter_ancestor(ancestor, pedigree: dict):
    filtered = OrderedDict()
    # This one (if exists in the pedigree)
    try:
        filtered.update({ancestor: pedigree[ancestor]})
    except KeyError:
        pass
    # Looking for offspring: looking for all individuals with this as parent
    for individual, parents in pedigree.items():
        if ancestor in parents:
            # Doing this so the order is ancestor first
            new_filtered = _filter_ancestor(individual, pedigree)
            new_filtered.update(filtered)
            filtered = new_filtered
    return filtered

def filter_ancestor(ancestor, pedigree: dict):
    filtered = _filter_ancestor(ancestor, pedigree)
    # Removing the ancestor pointing to its parents.
    try:
        del filtered[ancestor]
    except KeyError:
        pass
    return filtered

def filter_pedigree_of(individual, pedigree: dict):
    parents = []
    # This one
    try:
        parents = pedigree[individual]
    except KeyError:
        pass
    filtered = OrderedDict({individual: parents})
    # Add the pedigree of the parents
    for parent in parents:
        filtered.update(filter_pedigree_of(parent, pedigree))
    return filtered

def read_pedigree(filename: str) -> dict:
    with open(filename, 'r') as sped:
        pedigree = OrderedDict()
        for line in sped:
            sline = line.rstrip()
            if sline != '':
                if (sline[0] != '!') and (sline[0] != '#') and (sline[0] != ' ') and (sline[0] != '@'):
                    elements = sline.split()
                    if len(elements) > 0:
                        pedigree[elements[0]] = []
                    if len(elements) > 1:
                        if (elements[1][0] != '?') and (elements[1][0] != 'x'):
                            pedigree[elements[0]].append(elements[1])
                    if len(elements) > 2:
                        if (elements[2][0] != '?') and (elements[2][0] != 'x'):
                            pedigree[elements[0]].append(elements[2])
        return pedigree


if __name__ == '__main__':
    in_filename = '/home/bert/Documents/Dropbox/banded.txt'
    out_filename = None
    ancestor = None
    pedigree_of = None
    argument_mode = ""
    print("Arguments passed: %s" % (sys.argv[1:]))
    for argument in sys.argv[1:]:
        if argument_mode != "--" and argument.startswith("-"):
            if argument == "--":
                argument_mode = "--"
            elif argument.lower() in ["-h", "--help"]:
                help()
            elif argument.lower() in ["-f", "--file"]:
                argument_mode = "file"
            elif argument.lower() in ["-o", "--out"]:
                argument_mode = "out"
            elif argument.lower() in ["-c", "--center"]:
                argument_mode = "center"
            elif argument.lower() in ["-a", "--ancestor"]:
                argument_mode = "ancestor"
            elif argument.lower() in ["-p", "--pedigree", "--pedigree-of"]:
                argument_mode = "pedigree-of"
            else:
                help(1)
        else:
            if not argument_mode or argument_mode == "--":
                in_filename = argument
            elif argument_mode == "file":
                in_filename = argument
            elif argument_mode == "out":
                out_filename = argument
            elif argument_mode == "center":
                ancestor = argument
                pedigree_of = argument
            elif argument_mode == "ancestor":
                ancestor = argument
            elif argument_mode == "pedigree-of": 
                pedigree_of = argument
            # Undo the argument mode, unless mode "--"
            if argument_mode != "--":
                argument_mode == ""
    if not out_filename:
        out_filename = "%s.dot" % (in_filename.rsplit('.', 1)[0])

    print('Tranforming pedigree file %s to dot file %s' % (in_filename, out_filename))
    print(ancestor)
    print(pedigree_of)

    # Reading pedigree and filtering
    pedigree = None
    full_pedigree = read_pedigree(in_filename)
    if pedigree_of:
        pedigree = filter_pedigree_of(pedigree_of, full_pedigree)
        print('Filtered out the pedigree of %s (#%s) from the full pedigree (#%s).' % (pedigree_of, len(pedigree), len(full_pedigree)))
    if ancestor:
        if pedigree:
            pedigree.update(filter_ancestor(ancestor, full_pedigree))
            print('Added the offsprings of ancestor %s as well (#%s).' % (ancestor, len(pedigree)))
        else:
            pedigree = filter_ancestor(ancestor, full_pedigree)
            print('Filtered out the offsprings of ancestor %s (#%s) from the full pedigree (#%s).' % (ancestor, len(pedigree), len(full_pedigree)))
    if not pedigree:
        pedigree = full_pedigree
    # Writing the dot file
    write_dot(out_filename, pedigree)

    print("To generate a png from the dotfile, you could do:")
    print("\tdot -O -Tpng %s" % (out_filename))
