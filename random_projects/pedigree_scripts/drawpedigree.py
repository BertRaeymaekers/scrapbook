#!/usr/bin/env python3


from collections import OrderedDict, defaultdict
import sys
from pedigree import read_pedigree


DRAW_CHARACTERS = {
    " ": " ",
    "\\": "┐",
    "/": "┘",
    ">": "├",
    "<": "┤",
    "|": "│",
    "-": "─"
}


def ancestors(pedigree, id):
    result = {}
    depth = -1
    parents = pedigree.get_parents(id)
    if parents:
        for parent in parents:
            (result[parent], parent_depth) = ancestors(pedigree, parent)
            depth = max(depth, parent_depth)
    return (result, depth+1)

def descendents(pedigree, id):
    result = {}
    depth = 0
    childeren = pedigree.find_childeren(id)
    for child in childeren:
        (result[child], child_depth) = descendents(pedigree, child)
        depth = max(depth, child_depth)
    return (result, depth+1)

def matrix_fill_ans(matrix, ans, row=0, col=0):
    col -= 1
    for i, id in enumerate(ans):
        matrix[row+i][col] = id
        matrix_fill_ans(matrix, ans[id], (row+i)*2, col)

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
        yield ">"
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
        yield ">"
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

def bin_end_zeros(i):
    if i == 0:
        sys.exit()
    if i & 1:
        return 0
    else:
        return 1 + bin_end_zeros(i>>1)

def draw(ans, ans_depth, id, des, des_depth, *, col_width=None, full=False):
    if not col_width:
        col_width = 16
    matrix = defaultdict(dict)
    matrix[0][0] = id
    matrix_fill_ans(matrix, ans)

    spread_rows = {}
    top = -(2**ans_depth)
    for row in sorted(matrix):
        for col in sorted(matrix[row]):
            half_diff = 2**(ans_depth - abs(col))
            new_row = top + (2*row + 1) * half_diff
            spread_rows[new_row] = matrix[row][col]

    max_depth = max(ans_depth, 0) # des_depth
    max_range = 2**max_depth - 1
    if full:
        printing_rows = range(-max_range, max_range + 1)
    else:
        printing_rows = sorted(spread_rows)
    for row in printing_rows:
        line = []
        for col in pedigree_structure(row, ans_depth):
            if col in ">|":
                end_char = DRAW_CHARACTERS[col]
                if col in "><" and not full:
                    # If there is no parent in the printing rows, the > doesn't make sense.
                    diff_with_parents = 2**(bin_end_zeros(2**(ans_depth) + row) - 1)
                    if (row - diff_with_parents) not in printing_rows and (row + diff_with_parents) not in printing_rows:
                        end_char = " "
                line.append(" "*(col_width-1) + end_char)
            elif col in "\\/":
                label = spread_rows[row] if row in spread_rows else ""
                line.append(label[:col_width-2].ljust(col_width-1, DRAW_CHARACTERS["-"]) + DRAW_CHARACTERS[col])
            else:
                line.append(col*col_width)
        if row == 0:
            line.append(spread_rows[row][:col_width-1].ljust(col_width, DRAW_CHARACTERS["-"]))
        print("".join(line))


if __name__ == "__main__":
    pedigree = read_pedigree()
    center_bird = sys.argv[1]

    (ans, ans_depth) = ancestors(pedigree, center_bird)
    (des, des_depth) = descendents(pedigree, center_bird)
    print(ans, ans_depth)
    print(des, des_depth)

    draw(ans, ans_depth, center_bird, des, des_depth)
