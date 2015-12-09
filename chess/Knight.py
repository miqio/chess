# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
from Piece import Piece

log = logging.getLogger(__name__)

class Knight(Piece):
  '''
  Darf nach scharf links (+6,-10), leicht links (+15,-17), leicht rechts (-15,+17) 
  und scharf rechts (-6,+10)
  '''
  
  directions = (-21,-19,-12,-8,8,12,19,21)
  
  def __str__(self):
    if self.is_white:
      return 'S'
    else:
      return 's'
  
  def get_admissible_positions(self):
    '''
    Erlaubt sind alle Züge, die erlaubt sind.
    '''
    pos = self.get_position()
    log.debug("Going to check Knight at %i...", pos)
    directions = [pos+d for d in self.directions]
    admissible_positions = filter( lambda p : self.is_allowed_cell(p),directions )
    log.debug("Can reach %s",str(admissible_positions))
    return admissible_positions
    

