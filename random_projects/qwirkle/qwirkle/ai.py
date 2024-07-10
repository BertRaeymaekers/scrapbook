import random

from qwirkle import *


class RandomRobot(Player):
    def do_turn(self):
        self.tiles.extend(self.table.pick(6 - len(self.tiles)))
        # if self.rules == Player.SIMPLE_RULES
        # SIMPLE_RULES = play all tiles.
        tiles = self.tiles.copy()
        while len(tiles) > 0:
            # Pic a tile.
            i = random.randint(0, len(tiles) - 1)
            tile = self.tiles[i]
            suggested_positions = list(self.table.get_empty_adjecent_fields())
            while len(suggested_positions) > 0:
                # Pick a position and try if it goes.
                position = random.choice(suggested_positions)
                try:
                    points = self.play(*position, i)
                    tiles = self.tiles.copy()
                    break
                except IllegalMove:
                    # Bad move, try another.
                    suggested_positions.remove(position)
            else:
                # Suggested position = 0 and we haven't broken so not played.
                del tiles[i]


class BestForRandomTileRobot(Player):
    def do_turn(self):
        self.tiles.extend(self.table.pick(6 - len(self.tiles)))
        # if self.rules == Player.SIMPLE_RULES
        # SIMPLE_RULES = play all tiles.
        tiles = self.tiles.copy()
        while len(tiles) > 0:
            # Pic a tile.
            i = random.randint(0, len(tiles) - 1)
            tile = self.tiles[i]
            suggested_positions = list(self.table.get_empty_adjecent_fields())
            pos_points = {}
            for position in suggested_positions:
                try:
                    points = self.table.virtual_play(*position, tile)
                    pos_points[position] = points
                except IllegalMove:
                    # Bad one
                    pass
            #print(tile, pos_points)
            if len(pos_points) == 0:
                # Bad tile: no place for it.
                del tiles[i]
            else:
                winner = max(pos_points, key=pos_points.get)
                self.play(*winner, i)
                tiles = self.tiles.copy()
