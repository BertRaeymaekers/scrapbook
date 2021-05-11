#!/usr/bin/env python3


from collections import OrderedDict


PEDIGREE_FILE = "/home/bert/Documents/budgerigars/BR23/repo/budgerigar/full.ped"


class Pedigree:
    def __init__(self, pedigree=None, keepInverse=False):
        """
        Creates a pedigree object.

        Pass as pedigree an other Pedigree object (it will do a deep copy) or a dict of mapping individuals to a list of parents.

        If keepInverse is True then the reverse mapping from individuals to childeren is also.
        Set this if you think you need to call find_childeren() regularly.
        If you are not planning to call find_childeren(), set keepInverse to False to avoid the overhead.
        With keepInverse False calling find_childeren() is *very* slow.
        If you've set keepInverse to False, the fist call to find_childeren() will set keepInverse to True.
        This is done because find_childeren() will in this case has to go through the entire pedigree anyway, so there isn't a lot of overhead added to build up the inverse parent to childeren mapping.
        You can if you want specify keepInverse=False on your calls to find_childeren().
        But once keepInverse has been set to True, it will never be unset and keepInverse=False is just ignored.
        """
        self.childeren = None
        if pedigree is None:
            self.pedigree = OrderedDict()
        elif isinstance(pedigree, Pedigree):
            self.pedigree = pedigree.pedigree.deepcopy()
        else:
            self.pedigree = OrderedDict()
            if isinstance(pedigree, dict):
                for key,value in pedigree.items():
                    self.pedigree[key] =  list(value)
            else:
                raise ValueError("Must be a Pedigree object or a dict of a list of parents (or something the list constructor accepts).")
        if keepInverse:
            self._map_childeren()

    def add_parent(self, id, parent):
        """
        Add a link between an individual and a parent.
        """
        if id in self.pedigree:
            self.pedigree[id].append(parent)
        else:
            self.pedigree[id] = [parent]
        if self.childeren is not None:
            self._map_child(id, parent)

    def set_parents(self, id, *parents):
        """
        Set the parents of an individual
        """
        self.pedigree[id] = list(parents)
        if self.childeren is not None:
            for parent in parents:
                self._map_child(id, parent)

    def get_parents(self, id):
        return self.pedigree.get(id)

    def remove(self, id):
        """
        Remove an individual
        """
        parents = []
        if self.childeren is not None:
            parents = self.pedigree[id]
        del self.pedigree[id]
        for parent in parents:
            self.childeren.get(parent, set()).remove(id)

    def cascade_delete(self, id):
        """
        Remove an individual and all who reference it
        """
        map(self.cascade_delete, self.find_childeren(id))
        self.remove(id)

    def _map_child(self, id, parent):
        """
        Add a link from a parent to a child
        """
        if parent in self.childeren:
            self.childeren[parent].add(id)
        else:
            self.childeren[parent] = {id}

    def _map_childeren(self):
        """
        Calculates the inverse mapping of all the childeren of individuals.

        This is called during initial
        """
        self.childeren = dict()
        for id, parents in self.pedigree.items():
            for parent in parents:
                self._map_child(id, parent)

    def find_childeren(self, id, keepInverse=True):
        """
        Returns a set of all the childeren.

        Works best if keepInverse is set to True when the class is initialized.
        Will set keepInverse to True unless explicitely set to False
        With keepInverse Tru it will first calculate the parent to childeren mappings for all and cache them.
        """
        if keepInverse:
            if self.childeren is None:
                self._map_childeren()
            return self.childeren.get(id, set())
        else:
            childeren = set()
            for child, parents in self.pedigree.items():
                for parent in parents:
                    if parent == id:
                        childeren.add(child)
            return childeren

    def as_dict(self):
        """
        Return the pedigree as a dict of lists
        """
        return self.pedigree

    def clear(keepInverse=False):
        """
        Clear the pedigree.

        If keepInverse is True then adding a link also keeps a record of the
        inverse operation so that looking up childeren goes fast.
        """
        if keepInverse:
            self.childeren = dict()
        else:
            self.childeren = None
        self.pedigree = OrderedDict()


def read_pedigree(pedigree_file=None, keepInverse=True):
    """
    Reading the pedigree file and dumping it in a ordered dictionary.
    Generates a dictionary with individual: [parent1, parent2]
    """
    if not pedigree_file:
        pedigree_file = PEDIGREE_FILE
    pedigree = None
    with open(pedigree_file, 'r') as sped:
        pedigree = Pedigree(keepInverse=keepInverse)
        for line in sped:
            sline = line.rstrip()
            if sline != '':
                if (sline[0] != '!') and (sline[0] != '#') and (sline[0] != ' ') and (sline[0] != '@'):
                    elements = sline.split()
                    if len(elements) > 0:
                        #pedigree[elements[0]] = []
                        pedigree.set_parents(elements[0])
                    if len(elements) > 1:
                        if (elements[1][0] != '?') and (elements[1][0] != 'x'):
                            #pedigree[elements[0]].append(elements[1])
                            pedigree.add_parent(elements[0], elements[1])
                    if len(elements) > 2:
                        if (elements[2][0] != '?') and (elements[2][0] != 'x'):
                            #pedigree[elements[0]].append(elements[2])
                            pedigree.add_parent(elements[0], elements[2])
    return pedigree


if __name__ == "__main__":
    pedigree = read_pedigree()
    import json
    print(json.dumps(pedigree.as_dict(), indent=4))

