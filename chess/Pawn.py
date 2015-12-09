# -*- coding: utf-8 -*-
import logging  # Um Meldungen auszugeben
from Piece import Piece
from utils import get_chessboard, Simulator

log = logging.getLogger(__name__)


class Pawn(Piece):
  '''
  Der Bauer kann am wenigsten, hat aber die kompliziertesten Regeln. Vor allem für die Regel 
  "Schlagen en passant"-Regel (vgl. Art 3.7 d der offiziellen Regeln des Weltschachverbands (FIDE), 
  braucht es ein Gedächtnis, ob ein Bauer gerade um zwei Felder nach vorne gerückt ist.
  Der weiße Bauer immer eine vorwärts (+10) und am Anfang zwei vorwärts (+20). Geschlagen wird dann
  immer eins nach schräg links (+9) oder eins nach schräg rechts (+11). Für den schwarzen Bauern gilt
  das negative Vorzeichen.
  '''
  
  def __init__(self,pos,color=True):
    super(Pawn,self).__init__(pos, color)
    self.directions = (-1,1,9,10,11) if self.is_white else (1,-1,-9,-10,-11)
    
  def __str__(self):
    if self.is_white:
      return 'B'
    else:
      return 'b'

  def is_allowed_cell(self,target, direction = None):
    '''
    Bei Bauern ist es richtungsabhängig, ob sie auf besetzte Felder können. 
    '''
    if abs(direction) in [9,11] and super(Pawn,self).is_allowed_cell(target):
      is_occupied = bool(get_chessboard().get_piece(target))       
      return is_occupied 
    elif abs(direction) == 1 and get_chessboard().can_be_hit_en_passant(get_chessboard().get_piece(target)):
      return True
    else:
      return get_chessboard().get_piece(target) == ''
      
  def get_max_steps(self,direction):
    '''
    Bauern können nur aus der Startreihe zwei Schritte gehen
    '''
    pos = self.get_position()
    if pos/20 == 1 or pos/70 ==1 and not abs(direction) in [9,11]:
      return 2
    else:
      return 1

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
      count = 0
      log.debug("Checking position %i for %s at %i", step, self.__class__.__name__, self.get_position())
      while count < self.get_max_steps(direction) and self.is_allowed_cell(step,direction):
        log.debug("Appending %i", step)
        admissible_positions.append(step)
        step += direction
        count += 1
    return admissible_positions


