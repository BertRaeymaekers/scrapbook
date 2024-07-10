import random
from collections import defaultdict

from qwirkle.exceptions import *
from qwirkle.player import Player
from qwirkle.ai import *


__all__ = ["Bag", "Table", "EmptyBag", "IllegalMove", "Player", "RandomRobot", "BestForRandomTileRobot"]


class Bag():
    """
    A bag as used by qwirkle.
    """

    colours = ["red", "blue", "orange", "green", "yellow", "white"]
    symbols = ["square", "diamond", "circle", "blink", "triangle", "leaf"]
    repeat = 3

    def __init__(self, colours=None, symbols=None, repeat=None):
        """
        Creates the bag, filled with tiles ready for play.

        A tile is a tuple of (symbol, colour)
        """
        self.reset(colours=colours, symbols=symbols, repeat=repeat)

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def reset(self, colours=None, symbols=None, repeat=None):
        """
        Makes the bag full again, ready for a new game.

        You can specify a list of colours and/or symbols. If not specified
        the default from the Bag class are used. There have to be the same
        number of symbols and colours.
        You can also specify how many times all possible colour/symbol
        combinations are in the bag. Do this by setting repeat. It defaults
        to 3.
        """
        if colours:
            self.colours = colours
        else:
            self.colours = Bag.colours
        if symbols:
            self.symbols = symbols
        else:
            self.symbols = Bag.symbols
        if repeat:
            self.repeat = repeat
        else:
            self.repeat = Bag.repeat
        self.tiles = []
        if len(self.symbols) != len(self.colours):
            raise ValueException("The number of symbols and colours has to match.")
        for colour in self.colours:
            for symbol in self.symbols:
                for i in range(self.repeat):
                    self.tiles.append((symbol, colour))

    def is_empty(self):
        return len(self.tiles) == 0

    def pick(self, count = None):
        """
        Picks random tiles from the bag. Returns a list of tiles picked.

        By default it returns one, but you can specify the count.
        """
        result = []
        if not count:
            count = 1
        count = min(count, len(self.tiles))
        if count == 0:
            raise EmptyBag("The bag is empty.")
        for i in range(count):
            pick = random.randint(0, len(self.tiles) - 1)
            result.append(self.tiles[pick])
            del self.tiles[pick]
        return result


class Table():
    """
    Table represents the table on which you're playing.
    """

    def __init__(self, bag=None, max_height=None, max_width=None):
        """
        Initiate the table

        You can set maximum dimensions to your table.
        """
        if bag:
            self.bag = bag
        else:
            self.bag = Bag()
        self.max_width = max_width
        self.max_height = max_height
        self.tabletop = defaultdict(dict)

    def reset(self):
        self.bag.reset()

    def pick(self, count = None):
        return self.bag.pick(count)

    def __enter__(self):
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): 
        pass

    def is_empty(self):
        return len(self.tabletop) == 0

    def get_center(self):
        if self.max_width:
            column = self.max_width // 2
        else:
            column = 0
        if self.max_height:
            row = self.max_height // 2
        else:
            row = 0
        return (row, column)

    def get_empty_adjecent_fields(self):
        """
        Finds the empty fields adjecent to tiles.
        """
        if self.is_empty():
            return set([self.get_center()])
        result = set()
        for row_nr, row in self.tabletop.items():
            for column_nr, tile in row.items():
                # Check the 4 adjacent ones to see if they are empty.
                if not column_nr - 1 in row:
                    result.add((row_nr, column_nr - 1))
                if not column_nr + 1 in row:
                    result.add((row_nr, column_nr + 1))
                if not row_nr - 1 in self.tabletop:
                    result.add((row_nr - 1, column_nr))
                elif not column_nr in self.tabletop[row_nr - 1]:
                    result.add((row_nr - 1, column_nr))
                if not row_nr + 1 in self.tabletop:
                    result.add((row_nr + 1, column_nr))
                elif not column_nr in self.tabletop[row_nr + 1]:
                    result.add((row_nr + 1, column_nr))
        return result

    def _check_line(self, line):
        """
        Checks if a line is valid.
        """
        found_colours = set()
        found_symbols = set()
        for symbol, colour in line:
            found_colours.add(colour)
            found_symbols.add(symbol)
        if len(found_colours) > 1:
            if len(found_symbols) > 1:
                raise IllegalMove("You can't have multiple colours and multiple symbols on the same line.")
            if len(found_colours) != len(line):
                raise IllegalMove("You can't have repeating colours in a line of the same symbols.")
        elif len(found_symbols) != len(line):
            raise IllegalMove("You can't have repeating symbols in a line of the same colours.")
        # Double points for a full line.
        if len(line) == len(self.bag.symbols):
            return 2 * len(line)
        # No points for a solo line.
        if len(line) == 1:
            return 0
        # Otherwise one point per tile.
        return len(line)

    def _trymove(self, row, column, tile):
        """
        Internal function that checks if this is a legal move.

        Trows an IllegalMove exception if it finds issues.
          - If there is a limit to the table, if it fits on the table.
          - Check if it matches horizontal and vertical with the touching
            tiles.
        """
        # Within the table limits (if set)?
        if self.max_height:
            if row > self.max_height:
                raise IllegalMove("Row %s is off the table. The table is only %s high.", row, self.max_height)
        if self.max_width:
            if column > self.max_width:
                raise IllegalMove("Column %s is off the table. The table is only %s wide.", column, self.max_width)
        if column in self.tabletop[row]:
            raise IllegalMove("There is already a tile on (%s,%s): %s", row, column, self.tabletop[row][column])
        # Start with 0 points
        points = 0
        # Check the horizontally touching tiles
        line = [tile]
        i = column - 1
        try:
            while self.tabletop[row][i]:
                line.insert(0, self.tabletop[row][i])
                i -= 1
        except KeyError:
            pass
        i = column + 1
        try:
            while self.tabletop[row][i]:
                line.append(self.tabletop[row][i])
                i += 1
        except KeyError:
            pass
        points += self._check_line(line)
        # Check the vertically touching tiles
        line = [tile]
        i = row - 1
        try:
            while self.tabletop[i][column]:
                line.insert(0, self.tabletop[i][column])
                i -= 1
        except KeyError:
            pass
        i = row + 1
        try:
            while self.tabletop[i][column]:
                line.append(self.tabletop[i][column])
                i += 1
        except KeyError:
            pass
        points += self._check_line(line)
        return points

    def virtual_play(self, row, column, tile):
        """
        Check if this is a valid, legal move and how much it would yield.
        """
        return self._trymove(row, column, tile)

    def play(self, row, column, tile):
        """
        Play a certain tile on the table and return the points won.

        It will first check if it is a legal move.
        """
        points = self._trymove(row, column, tile)
        self.tabletop[row][column] = tile
        return points


    def _content(self):
        result = []
        for row_nr, row in self.tabletop.items():
            for column_nr, tile in row.items():
                result.append("%s,%s: %s" % (row_nr, column_nr, tile))
        return "\n".join(result)

    @staticmethod
    def tile_to_short_str(tile):
        return tile[0][0].upper() + tile[1][0].upper()

    def __str__(self):
        rows = defaultdict(dict)
        min_row = 0
        max_row = 0
        min_column = 0
        max_column = 0
        for row_nr, row in self.tabletop.items():
            max_row = max(max_row, row_nr + 1)
            min_row = min(min_row, row_nr)
            row_str = defaultdict(lambda: "    ")
            for column_nr, tile in row.items():
                max_column = max(max_column, column_nr + 1)
                min_column = min(min_column, column_nr)
                row_str[column_nr] = "[" + Table.tile_to_short_str(tile) + "]"
            rows[row_nr] = row_str
        result = []
        for i in range(min_row, max_row):
            line = []
            for j in range(min_column, max_column):
                line.append(rows[i][j])
            result.append("".join(line))
        return "\n".join(result)

