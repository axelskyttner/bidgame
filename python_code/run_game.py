#!/usr/bin/env python
from BidGame import BidGame

game = BidGame('molnhatt.se')
for i in range(10):

    stats = game.run()
    # game.visualize(stats)
