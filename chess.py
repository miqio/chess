#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import argparse # Damit beim Programmaufruf Werte übergeben werden können
import chess.manager as manager # Controller zur Durchführung des Schachspiels

parser = argparse.ArgumentParser(description="Schachspiel für die Kommandozeile und zwei Spieler")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-p", "--positions", default=None, help="String containing the positions")
args = parser.parse_args()

log_level = logging.DEBUG if args.verbose else logging.WARN
positions = args.positions

logging.basicConfig(level=log_level) # Setze auf logging.DEBUG, damit Meldungen ausgegeben werden
log = logging.getLogger(__name__)

    
if __name__ == "__main__":
  if positions:
    # Initialisiert das Brett mit ggf. übergebenen Stellungen, sonst die 
    # übliche Startaufstellung
    manager.get_chessboard(positions)
  manager.start()
