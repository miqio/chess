# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
from Piece import Piece
from utils import Simulator, get_chessboard 

log = logging.getLogger(__name__)

class King(Piece):

  directions = (-11,-10,-9,-1,1,9,10,11)
  is_check_given = False

  def __str__(self):
    if self.is_white:
      return 'K'
    else:
      return 'k'
  
  def is_king_of_moving_player(self):
    '''
    True if self is king and belongs to the moving player
    '''
    return self.is_moving()

  def set_position(self,pos):
    '''
    Falls der König im Schach stand und sich nich bewegen kann, dann wohl 
    nur auf eine unbedrohte Position
    '''
    log.debug("Setting Position of King at %s to %i",str(self.get_position()), pos)
    self.position=pos
    if self.is_check_given:
      log.debug("Releasing 'is_check_given'")
      self.is_check_given = False

  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions(True)
    if admissible_positions and pos in admissible_positions:
      return True
    else:
      # Wenn der König schachmatt ist...
      if self.is_check_given and not admissible_positions:
        log.debug("No available position found!")
        get_chessboard().has_finnished = True
      return False

  def get_admissible_positions(self):
    '''
    Erlaubt sind alle Züge. Solche, die auf eine eigene Figur verweisen oder 
    aus dem Spielfeld heraus führen, werden schon durch chess.is_allowed_move() 
    gefiltert. Damit innerhalb eines Spielzugs nicht durch rekursives Aufrufen 
    von is_safe_position und get_admissible_positions endlos iteriert wird, 
    wird die is_safe_position für den eigenen König nicht durchgeführt.
    '''
    position = self.get_position()
    positions = [position+d for d in self.directions]
    log.debug("Going to check King at %i...", position)
    admissible_positions = filter(lambda pos: self.is_allowed_cell(pos),positions)
    if self.has_never_been_moved:
      if get_chessboard().get_piece(position+3)\
          and get_chessboard().get_piece(position+3).has_never_been_moved\
          and position+1 in admissible_positions\
          and filter(lambda o:isinstance(o,Piece),\
            get_chessboard().get_position()[position+1:position+2]) \
          and self.is_safe_position(Simulator(self.get_position(),position+2)):
        log.debug("Der %se König kann nach rechts rochieren.")          
        admissible_positions.append(position + 2)
      if get_chessboard().get_piece(position-4)\
          and get_chessboard().get_piece(position-4).has_never_been_moved\
          and position-1 in admissible_positions\
          and filter(lambda o:isinstance(o,Piece),\
            get_chessboard().get_position()[position-3:position-1]) \
          and self.is_safe_position(Simulator(self.get_position(),position-2)):
        log.debug("Der %se König kann nach links rochieren.")          
        admissible_positions.append(position - 2)
    log.debug("Can reach %s", admissible_positions)
    return admissible_positions

  def get_safe_positions(self):
    '''
    Erlaubte Positionen, auf denen der König nicht angegriffen wird
    '''
    admissible_positions = self.get_admissible_positions()
    for pos in list(admissible_positions):
      log.debug("Checking position %i\n", pos)
      if not self.is_safe_position(Simulator(self.get_position(),pos)):
        log.debug("Position %i is not safe!\n", pos)
        admissible_positions.remove(pos)
    return admissible_positions         
    

