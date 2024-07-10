class Player():

    SIMPLE_RULES = 1
    DEFAULT_RULES = 0

    def __init__(self, name, table, rules=None):
        self.name = name
        self.table = table
        if rules:
            self.rules = rules
        else:
            self.rules = Player.DEFAULT_RULES
        self.reset()

    def reset(self):
        self.tiles = []
        self.score = 0

    def play(self, row, column, tile):
        tile_instance = self.tiles[tile]
        #print("%s is playing %s,%s: %s,%s" % (self.name, row, column, *tile_instance))
        points = self.table.play(row, column, tile_instance)
        del self.tiles[tile]
        print("%s played %s,%s: %s,%s => %s pnt" % (self.name, row, column, *tile_instance, points))
        self.score += points
        return points

    def do_turn(self):
        raise NotImplemented("You need to subclass Player and implement the turn method.")

    def __str__(self):
        return self.name
