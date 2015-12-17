#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Das Spiel ist nach dem Model-View-Controller-Entwurfsmuster konzipiert. 
# Das Modul manager.py ist der Controller, der View und Model miteinander
# verbindet. Den View repräsentiert das Modul interface mit der Klasse
# IFInterface, das Modell ist mehrteilig und besteht zum einen aus 
# Chessboard im Modul board und zum anderen aus der Klasse Piece und
# seinen Unterklassen im Modul pieces. Der Ablauf eines Spiels wird im
# Modul manager gesteuert.   

import logging  # Um Meldungen auszugeben
import pieces
from board import Chessboard, Simulator
from interface import IFChessboard 

log = logging.getLogger(__name__)

#######################################################################
# Verschiedene Text-Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
STR_WHITE                           = "Weiß"
STR_BLACK                           = "Schwarz"
MSG_ROUND                           = "%s ist am Zug.\n"
MSG_MOVING                          = "Ziehe %s %s von %i nach %i\n"
STR_EMPTY_CELL                      = " "
STR_BOTTOM_TOP_LINE                 = "  | A | B | C | D | E | F | G | H |  "
STR_SEPARATOR                       = "-------------------------------------"
MSG_ASK_FOR_PIECE                   = "Welche Figur? Gebe die Position an: "
MSG_ASK_FOR_POSITION                = "Wohin? Gebe die Position an: "
MSG_INVALID_MOVE                    = "Ungültiger Zug! Probier es noch einmal!\n"
MSG_INVALID_INPUT                   = "Ungültige Eingabe! Probier es noch einmal!\n"
MSG_WINNER                          = "Schachmatt! %s hat gewonnen!\nDas Spiel ist beendet.\n"
MSG_CHECK_GIVEN                     = "Schach!\n"
MSG_PAWN_PROMOTION                  = "Der Bauer kann verwandelt werden!\n\n"
MSG_ASK_FOR_NEW_PIECE               = "Wähle (D|d)ame, (T|t)urm, (L|l)äufer oder (S|s)pringer\n"
CHESSBOARD = None           # Das aktuelle Schachspiel mit seinen Figuren
INTERFACE = None            # Die Benutzerschnittstelle

###############################################################################
# Figuren erzeugen
###############################################################################

def newinstance(name,pos):
  '''
  Instantiates a new piece of type name at position p
  '''
  if name == 'B':
    return pieces.Pawn(pos)
  if name == 'b':
    return pieces.Pawn(pos,False)
  if name == 'T':
    return pieces.Rook(pos)
  if name == 't':
    return pieces.Rook(pos,False)
  if name == 'L':
    return pieces.Bishop(pos)
  if name == 'l':
    return pieces.Bishop(pos,False)
  if name == 'S':
    return pieces.Knight(pos)
  if name == 's':
    return pieces.Knight(pos,False)
  if name == 'D':
    return pieces.Queen(pos)
  if name == 'd':
    return pieces.Queen(pos,False)
  if name == 'K':
    return pieces.King(pos)
  if name == 'k':
    return pieces.King(pos,False)
  else:
    return ''

###############################################################################
# Auf das Schachbrett zugreifen...
###############################################################################

def get_chessboard(positions=None):
  '''
  Das Spielbrett einschließlich der Figuren.
  Wird beim ersten Aufruf initialisiert. Bei
  danach folgenden Aufrufen wird die Variable
  positions nicht mehr verarbeitet. 
  '''
  if not CHESSBOARD:
    log.debug('Instantiating chessboard')
    globals()['CHESSBOARD'] = Chessboard(positions)
  return CHESSBOARD
  
def get_piece(pos):
  '''
  Die Figur auf Position pos
  '''
  return get_chessboard().get_piece(pos)

def get_positions():
  '''
  Die aktuelle Spielfeldbelegung.
  Rückgabewert: eine Liste, auf den Indizes 11-18, 21-28,...,81-88 das 
  eigentliche Spielfeld, sonst None zur Kennzeichnung des Spelfeldrands
  '''
  return get_chessboard().positions

def get_white_rooks():
  '''
  Die weißen Türme
  '''
  return get_chessboard().white_rooks

def get_black_rooks():
  '''
  Die schwarzen Türme
  '''
  return get_chessboard().black_rooks

def get_last_move():
  '''
  Der letzte Zug.
  Rückgabewert: (start_pos, target_pos,piece) oder (0,0,-1)
  '''
  return get_chessboard().get_last_move()
  
def is_white_moving():
  '''
  Return True if white is moving
  '''
  return get_chessboard().is_white

def finnish_game():
  '''
  Setzt den Trigger zu Beendigung des Spiels
  '''
  get_chessboard().has_finnished = True 

def get_interface():
  '''
  Die Benutzerschnittstelle
  '''
  if not globals()['INTERFACE']:
    globals()['INTERFACE'] = IFChessboard()
  return INTERFACE
  
###############################################################################
# Die Spieldurchführung
###############################################################################

def start():
  '''
  Main Loop
  '''
  while not get_chessboard().has_finnished:
    get_interface().display_game(str(get_chessboard()))
    get_interface().display_msg( MSG_ROUND % get_chessboard().get_color() )
    perform_move()
  get_interface().display_msg( MSG_WINNER % get_chessboard().get_king_of_opponent().get_color() )

def perform_move():
  '''
  Performs a move
  '''
  is_valid_move=False
  while not is_valid_move:
    # Zunächst prüfen, ob der ziehende Spieler im Schach steht
    if get_chessboard().is_check_given():
      get_interface().display_msg( MSG_CHECK_GIVEN )
    move = get_interface().get_move()
    start_pos, target_pos = move
    is_valid_move = get_chessboard().move_piece(move)
    if get_chessboard().has_finnished:  # Will occur when a player is given chess mate
      break
    if not is_valid_move: 
      get_interface().display_msg( MSG_INVALID_MOVE )
      continue
    elif get_piece(target_pos).can_be_promoted():
      get_interface().display_msg( MSG_PAWN_PROMOTION )
      piece_name = get_interface().get_piece()
      get_positions()[ target_pos] = newinstance( piece_name, target_pos )
    get_chessboard().append_history(move)
    get_chessboard().switch_color()
  
def is_safe_position_for_king(start_pos,target_pos):
  '''
  Erzeugt eine Kopie des aktuellen Spielstands, zieht von start_pos nach
  target_pos und prüft, ob dadurch der König des ziehenden Spielers in
  Bedrändnis gerät.
  '''
  return Simulator(start_pos,target_pos).is_safe_position_for_king()
  
