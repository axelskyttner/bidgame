#!/usr/bin/env python
from BidGame import BidGame


game = BidGame()
stats = game.run()

game.visualize(stats)
