import random
from qwirkle import *


with Table() as table:
    player1 = RandomRobot(name="RandomRobot 1", table=table)
    player2 = BestForRandomTileRobot(name="BestForRandomTileRobot 2", table=table)
    i = j = 0
    while True:
        try:
            #picks = table.pick(1)
            #print("I picked %s" % (picks))
            #for tile in picks:
            #    table.place(i, j, tile)
            #    which = random.choice([0, 1])
            #    i += which
            #    j += 1 - which
            player1.do_turn()
            #print(table._content())
            print(table)
            player2.do_turn()
            #print(table._content())
            print(table)
        except EmptyBag:
            break
    if table.bag.is_empty():
        print("The bag is empty!")
    print("Scores:")
    print("\t%s: %s" % (player1, player1.score))
    print("\t%s: %s" % (player2, player2.score))
