#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import pieces
from board import Chessboard
from interface import IFChessboard 

log = logging.getLogger(__name__)

#######################################################################
# Verschiedene Text-Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
STR_WHITE                           = "Weiß"
STR_BLACK                           = "Schwarz"
MSG_ROUND                           = "\n%s ist am Zug.\n"
MSG_MOVING                          = "Ziehe %s %s von %i nach %i\n"
STR_EMPTY_CELL                      = " "
STR_BOTTOM_TOP_LINE                 = "  | A | B | C | D | E | F | G | H |  "
STR_SEPARATOR                       = "-------------------------------------"
MSG_ASK_FOR_PIECE                   = "\nWelche Figur? Gebe die Position an: "
MSG_ASK_FOR_POSITION                = "\nWohin? Gebe die Position an: "
MSG_INVALID_MOVE                    = "Ungültiger Zug! Probier es noch einmal!\n"
MSG_INVALID_INPUT                   = "Ungültige Eingabe! Probier es noch einmal!\n"
MSG_WINNER                          = "Schachmatt! %s hat gewonnen!\nDas Spiel ist beendet.\n"
MSG_CHECK_GIVEN                     = "Schach!\n"

CHESSBOARD = None           # Das aktuelle Schachspiel mit seinen Figuren
INTERFACE = None            # Die Benutzerschnittstelle

class Simulator:
  '''
  Um einen Zug zu simulieren. Ein neues Schachspiel mit den
  aktuellen Stellungen verändert um den zu simulierenden Zug
  wird erzeugt, um die Bedrohung für den König der ziehenden
  Partei zu analysieren.
  '''
  chessboard=None

  def __init__(self, start_pos, target_pos):
    piece = self.get_piece(start_pos)
    self.set_piece(piece,target_pos)
  
  def get_chessboard(self):
    '''
    Lazy initialization of a new game from the current game
    '''
    if not self.chessboard:
      self.chessboard = newchessboard(str(get_chessboard()))
      self.chessboard.is_white=get_chessboard().is_white
    return self.chessboard
  
  def get_piece(self,pos):
    return self.get_chessboard().get_piece(pos)
  
  def set_piece(self, piece, target_pos):
    '''
    Kapselt chessboard.set_piece
    ''' 
    log.debug("Simulating a move...")
    self.get_chessboard().set_piece(piece,target_pos)
    return self
  
  def is_safe_position_for_king(self):
    '''
    Prüft, ob der eigene König durch den geplanten Zug in Bedrängnis gerät
    '''  
    return self.get_chessboard().get_king_of_moving_player().is_safe_position()

###############################################################################
# Diverse Getter
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

def newchessboard(positions=None):
  '''
  Instantiates a new game from postions given as a string or 
  list of strings describing the ranks.
  '''
  if isinstance(positions,str):
    positions=positions.splitlines()
  return Chessboard(positions)

def get_chessboard(positions=None):
  '''
  Das Spielbrett einschließlich der Figuren.
  Wird beim ersten Aufruf initialisiert. Bei
  danach folgenden Aufrufen wird die Variable
  positions nicht mehr verarbeitet. 
  '''
  if not CHESSBOARD:
    log.debug('Instantiating chessboard')
    globals()['CHESSBOARD'] = newchessboard(positions)
  return CHESSBOARD
  
def get_interface():
  '''
  Die Benutzerschnittstelle
  '''
  if not globals()['INTERFACE']:
    globals()['INTERFACE'] = IFChessboard()
  return INTERFACE
  
def simulate_move(start_pos,target_pos):
  '''
  Erzeugt eine Kopie der aktuellen Stellungen und führt einen
  Zug aus
  '''
  return Simulator(start_pos,target_pos)
  
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
    is_valid_move = get_chessboard().move_piece(move)
    if get_chessboard().has_finnished:  # Will occur when a player is given chess mate
      break
    if not is_valid_move: 
      get_interface().display_msg( MSG_INVALID_MOVE )
      continue 
  # Switch from white to black or vice versa to indicate the
  # currently moving player
  get_chessboard().append_history(move)
  get_chessboard().switch_color()


