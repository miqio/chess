# -*- coding: utf-8 -*-
import logging  # Um Meldungen auszugeben

from utils import get_chessboard, Simulator

log = logging.getLogger(__name__)

STR_WHITE                           = "Weiß"
STR_BLACK                           = "Schwarz"

class Piece(object):
  '''
  Oberklasse für alle Spielfiguren. Hat eine Position auf dem Spielfeld
  und eine Farbe. In Unterklassen muss die Funktion is_valid_move()
  implementiert werden, die die Spielfigur-spezifischen Zugvarianten
  kennt. Die Oberklasse enthält eine Implementierung, die für Läufer,
  Turm und Dame gültig ist. Die jeweiligen Unterklassenenthalten jeweils
  nur die möglichen Schrittrichtungen. Insofern wären für diese Figuren
  die Unterklassen nicht erforderlich, da ja auch die Oberklasse mit den
  erlaubten Schrittrichtungen initialisiert werden könnte.
  '''
  position = None
  has_never_been_moved = True

  def __init__(self,pos,color=True):
    self.set_position(pos)
    self.is_white=color
    log.debug("%s initialized with color %s at position %i",\
      self.__class__.__name__,self.get_color(),self.get_position())
    
  def get_position(self):
    return self.position
  
  def set_position(self,pos):
    log.debug("Setting Position of %s at %s to %i",\
      self.__class__.__name__,str(self.get_position()), pos)
    self.position = pos
    self.has_never_been_moved = False
    
  #############################################################################
  # Einige Hilfsfunktionen
  #############################################################################
  
  def get_color(self):
    '''
    Returns the string white or black
    '''
    return STR_WHITE if self.is_white else STR_BLACK
    
  def get_admissible_positions(self):
    '''
    Gibt eine Liste der erlaubten Zielpositionen der Figur.
    
    Dazu wird iterativ für jede Richtung geprüft, ob ein Feld erreichbar ist.
    Sobald ein Feld besetzt ist, bricht die Iteration für die jeweilige 
    Richtung ab. Wenn das Feld durch eine gegnerische Figur besetzt ist, gilt
    auch dieses Feld als erlaubt.
    
    Die erlaubten Richtungen sind Eigenschaften der jeweiligen Spielfiguren.
    '''
    admissible_positions=[]
    directions = list(self.directions)
    log.debug("Possible directions for %s at %i are %s", self.__class__.__name__, self.get_position(),str(directions))
    for direction in directions:
      pos = self.get_position()
      step = pos + direction
      log.debug("Checking position %i for %s at %i", step, self.__class__.__name__, self.get_position())
      while self.is_allowed_cell(step) and not get_chessboard().get_piece(step):
        log.debug("Appending %i", step)
        admissible_positions.append(step)
        step += direction
      if self.is_allowed_cell(step):
        log.debug("Appending %i, because %s belongs to opponent", step, get_chessboard().get_piece(step).__class__.__name__)
        admissible_positions.append(step)      
    return admissible_positions
    
  #############################################################################
  # Einige Prüffunktionen
  #############################################################################
  
  def is_moving(self):
    '''
    True if piece belongs to the moving player
    '''
    return get_chessboard().is_white == self.is_white
   
  def is_king_of_moving_player(self):
    '''
    True if self is king and belongs to the moving player
    '''
    return False

  def is_allowed_cell(self,target):
    '''
    True, if cell is empty or piece on cell is opposing.
    cell_occupation is either of type Piece or None or the empty string.
    Beachte, das an Stellen, wo python einen Wahrheitswert erwartet,
    ein Ausdruck im zweifel zu einem solchen verwandelt wird. Dabei erhält
    die Null, die leere Menge, der leere String immer den Wahrheitswert False,
    wohingegen alles andere automatisch True ist. Die Umwandlung geschieht
    automatisch mit der eingebauten Funktion (builtin) bool(). 
    '''
    if target < 0 or target > 99:
      return False
    if get_chessboard().get_piece(target):
      return self.is_white != get_chessboard().get_piece(target).is_white
      # True if opponent's color, False otherwise
    else:
      return get_chessboard().get_piece(target) is not None 
      # True if empty string, i.e a valid but un-occupied position

  def is_piece_of_opponent(self, o):
    '''
    Testet, ob o vom Typ Piece ist und die gegnerische Farbe hat
    '''
    return isinstance(o,Piece) and o.is_white != self.is_white
    
  def is_safe_position(self, simulator=None):
    '''
    simulator simuliert einen Spielzug einer beliebigen Figur,
    die auch die Figur selbst sein kann. Dann wird geprüft, ob die Figur selbst
    auf der Zielposition angegriffen wird, indem geprüft wird, ob irgendeine
    der gegnerischen Figuren die Zielposition auch erreichen kann.
    
    Das builtin filter(Filterfunktion, Liste) filtert Werte aus einer Liste
    anhand einer Filterfunktion, die eine Filterbedingung definiert. filter(lambda x:Funktion(x),Liste) 
    ist eine spezielle Kurzschreibweise und äquivalent zu:
                
                    for x in Liste:
                      if not Funktion(x):
                        Liste.remove(x)
                    return Liste 
    '''
    is_safe_position = True
    opposing_pieces = filter( lambda o: self.is_piece_of_opponent(o) ,get_chessboard().positions)
    pos = self.get_position()
    log.debug("Checking if %s at %i is check given", self.__class__.__name__,pos )
    for piece in opposing_pieces:
      log.debug('Checking if %s at %i attacks',piece.__class__.__name__,piece.get_position())
      admissible_positions = piece.get_admissible_positions()
      if admissible_positions and pos in admissible_positions:
        log.debug( "%s at %i attacks at %i!\n" , piece.__class__.__name__,piece.get_position(),pos)
        is_safe_position = False
        break
    # Nicht vergessen, alles wieder auf Anfang zu setzen:
    if simulator:
      simulator.undo_set_piece()
    return is_safe_position
  
  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i\n",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions()
    if admissible_positions and pos in admissible_positions:
      king = get_chessboard().get_king_of_moving_player()
      log.debug("Checking if King at %i is in danger when %s is moved from %i to %i",king.get_position(),self.__class__.__name__,self.get_position(),pos)
      # Wenn der eigene König nach Durchführung des geplanten Zugs im Schach stünde... 
      if not king.is_safe_position(Simulator(self.get_position(), pos)):
        return False
      return True
    else:
      return False
      

