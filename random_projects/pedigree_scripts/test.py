#!/usr/bin/env python3


import sys


try:
    depth = int(sys.argv[1])
except:
    depth = 3


def inverse(state):
    for c in state:
        if c == "\\":
            yield "/"
        elif c == "/":
            yield "\\"
        else:
            yield c


def pedigree_structure(row, depth):
    """
    Returns a pedigree drawing skeleton.

    It takes full advantage of the fractal nature of the pedigree drawing structure.

    row: row, where 0 should be the center. It should be inbetween ]2**depth, 2**depth[
    depth: how deep the pedigree goes.
    """
    def inverse(state):
        """
        Inversed the upward and downward bends.
        """
        for c in state:
            if c == "\\":
                yield "/"
            elif c == "/":
                yield "\\"
            else:
                yield c
            
    if row == 0:
        for i in range(1, depth):
            yield " "
        yield "+"
        return
    if row > 0:
        # The main mirror is at row 0.
        # Positive rows are just the inverse of the negative ones
        yield from inverse(pedigree_structure(-row, depth))
        return
    # The negative rows indexed as if from 1, depends on the depth.
    row_from_1 = 2**depth + row
    # Check of the row_from_1 makes sense.
    if row_from_1 < 0 or row_from_1 > 2**depth:
        raise ValueError(f"Row {row} doesn't exists for depth {depth}.")
    # The first row is always a \
    if row_from_1 == 1:
        yield "\\"
        return
    # The pivot where the mirror is for the row.
    pivot = 2**(int.bit_length(row_from_1)-1)
    if pivot == row_from_1:
        # Add empties for each zero bit
        for i in range(2, int.bit_length(row_from_1)):
            yield " "
        yield "+"
        yield "\\"
        return
    # The row at the lower side of the mirror.
    mirror_row = 2*pivot - row_from_1
    # So we inverse the state of that mirror row (in the original counting)
    yield from inverse(pedigree_structure(mirror_row - 2**depth, depth))
    # Add empties for each zero bit
    for i in range(1, int.bit_length(row_from_1) - int.bit_length(mirror_row)):
        yield " "
    # And since we cut of the highest bit by using the mirror row, here we need a |
    yield "|"

test_str = "\\\\////"
print(test_str, "".join(inverse(test_str)))

print("---")
max = 2**depth - 1
for row in range(-max, max+1):
    print((" "*(row==0) + "+"*(row>0) + str(row)).ljust(4) + "".join(pedigree_structure(row, depth)))
print("---")

int.to_bytes