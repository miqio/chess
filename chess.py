#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import re       # Das für den Mustervergleich erforderliche Modul "regular expressions""
import argparse # Damit beim Programmaufruf Werte übergeben werden können
import chess    # Das Schachspiel mit Benutzerschnittstelle

parser = argparse.ArgumentParser(description="Schachspiel für die Kommandozeile und zwei Spieler")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-p", "--positions", default=None, help="String containing the positions")
args = parser.parse_args()

log_level = logging.DEBUG if args.verbose else logging.WARN
positions = args.positions

logging.basicConfig(level=log_level) # Setze auf logging.DEBUG, damit Meldungen ausgegeben werden
log = logging.getLogger(__name__)

#######################################################################
# Verschiedene Text-Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
MSG_ROUND                           = "\n%s ist am Zug.\n"
MSG_MOVING                          = "Ziehe %s %s von %i nach %i\n"
MSG_INVALID_MOVE                    = "Ungültiger Zug! Probier es noch einmal!\n"
MSG_WINNER                          = "Schachmatt! %s hat gewonnen!\nDas Spiel ist beendet.\n"
MSG_CHECK_GIVEN                     = "Schach!\n"

def start():
  '''
  Main Loop
  '''
  while not chess.get_chessboard().has_finnished:
    chess.get_interface().display_game(str(chess.get_chessboard(positions)))
    chess.get_interface().display_msg( MSG_ROUND % chess.get_chessboard().get_color() )
    perform_move()
  chess.get_interface().display_msg( MSG_WINNER % chess.get_chessboard().get_king_of_opponent().get_color() )

def perform_move():
  '''
  Performs a move
  '''
  is_valid_move=False
  while not is_valid_move:
    # Zunächst prüfen, ob der ziehende Spieler im Schach steht
    if chess.get_chessboard().is_check_given():
      chess.get_interface().display_msg( MSG_CHECK_GIVEN )
    move = chess.get_interface().get_move()
    is_valid_move = chess.get_chessboard().move_piece(move)
    if chess.get_chessboard().has_finnished:  # Will occur when a player is given chess mate
      break
    if not is_valid_move: 
      chess.get_interface().display_msg( MSG_INVALID_MOVE )
  # Switch from white to black or vice versa to indicate the
  # currently moving player
  chess.get_chessboard().append_history(move)
  chess.get_chessboard().switch_color()
    
  
if __name__ == "__main__":
  start()
