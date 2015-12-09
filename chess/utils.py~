# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben

log = logging.getLogger(__name__)


class Simulator:
  '''
  Um einen Zug zu simulieren. Merkt sich im Wesentlichen den Ursprungszustand,
  um dahin wieder zurückkehren zu können
  '''

  def __init__(self, start_pos,target_pos):
    '''
    Initialisiere den Simulator, indem die Figur auf start_pos
    nach target_pos gezogen wird
    '''
    piece = self.get_piece(start_pos)
    self.set_piece(piece, target_pos)
    
  def get_piece(self,pos):
    return get_chessboard().get_piece(pos)
  
  def set_piece(self, piece, target_pos):
    '''
    Wie chess.set_piece, aber mit der Zusatzfunktion, den Ursprungszustand zu
    memorieren.
    ''' 
    log.debug("Simulating a move...")
    self.piece_to_be_moved = piece
    self.target_piece = self.get_piece(target_pos)
    self.start_pos = piece.get_position()
    self.target_pos = target_pos
    self.has_never_been_moved = piece.has_never_been_moved
    self.is_check_given = piece.is_check_given if piece.__class__.__name__ == 'King' else None
    get_chessboard().set_piece(piece,target_pos)

  def undo_set_piece(self):
    '''
    Rekonstruiert die Ursprungsstellung
    ''' 
    get_chessboard().set_piece(self.piece_to_be_moved, self.start_pos)
    if self.target_piece:
      get_chessboard().set_piece(self.target_piece,self.target_pos)
    if self.is_check_given:
      log.debug('Restoring is_check_given')
      self.piece_to_be_moved.is_check_given = self.is_check_given
    if self.has_never_been_moved:
      log.debug('Restoring has_never_been_moved')
      self.piece_to_be_moved.has_never_been_moved = self.has_never_been_moved
    log.debug('Simulation finnished')

def get_chessboard(positions=None):
  '''
  Das Spielbrett einschließlich der Figuren.
  Wird beim ersten Aufruf initialisiert. Bei
  danach folgenden Aufrufen wird die Variable
  positions nicht mehr verarbeitet. 
  '''
  if not globals().has_key('chessboard'):
    log.debug('Instantiating chessboard')
    from Chessboard import Chessboard
    globals()['chessboard'] = Chessboard(positions)
  return globals()['chessboard']
  
def get_interface():
  '''
  Die Benutzerschnittstelle
  '''
  if not globals().has_key('interface'):
    from IFChessboard import IFChessboard
    globals()['interface'] = IFChessboard()
  return globals()['interface']
    

