# -*- coding: utf-8 -*-

from Piece import Piece
from Pawn import Pawn
from Rook import Rook
from Knight import Knight
from Bishop import Bishop
from Queen import Queen
from King import King

STR_WHITE                           = "Weiß"
STR_BLACK                           = "Schwarz"


class Chessboard():
  '''
  Container für Spielfeldbelegungen
  '''
  has_finnished = False               # Für die Abbruchbedingung
  is_white = True                     # True, wenn weiß am Zug ist
  history=[]                          # Um sich die Spielzüge zu merken
  positions=[]                        # Spielfeld mit Belegungen
  initial_positions = [
    "T,S,L,D,K,L,S,T",
    "B,B,B,B,B,B,B,B",
    ",,,,,,,",
    ",,,,,,,",
    ",,,,,,,",
    ",,,,,,,",
    "b,b,b,b,b,b,b,b",
    "t,s,l,d,k,l,s,t"
  ]

  def __init__(self,positions=None):
    # Initialize positions
    #
    # Es werden Reihen à 10 genommen, um bei diagonalen Bewegungn
    # der Figuren den Rand leichter bestimmen zu können. Außerdem
    # oben und unten je eine Reihe mit nix 
    positions = positions if positions else self.initial_positions
    for i in range(10):
      self.positions.append(None)     # Eine Reihe nix
    for i in range(8):
      self.positions.append(None)     # Nix am linken Rand
      rank = positions[i].split(',')  # Der String mit den Belegungen
      for j in range(8):              
        self.positions.append(newinstance(rank[j],len(self.positions)))
      self.positions.append(None)     # Nix am rechten Rand
    for i in range(10):
      self.positions.append(None)
    self.white_king = self.get_piece(15)
    self.black_king = self.get_piece(85)
    
  def __str__(self):
    out = ''
    for i in range(1,9):
      for j in range(1,8):
        s = str(self.get_piece(10*i+j))
        out+="%s," % s
      s = str(self.get_piece(10*i+8))
      out+="%s\n" % s
    return out.strip()
  
  def get_color(self):
    '''
    Return the color of the current move
    '''
    return STR_WHITE if self.is_white else STR_BLACK
    
  def get_piece(self,pos):
    '''
    Returns piece on position pos or None or -1
    '''
    return  self.positions[pos]
  
  def get_king_of_opponent(self):
    '''
    Return the king of the opponent
    '''
    if not self.is_white:
      return self.white_king
    else:
      return self.black_king

  def get_king_of_moving_player(self):    
    '''
    Return the king of the current player
    '''
    if self.is_white:
      return self.white_king
    else:
      return self.black_king
   
  def set_piece(self,piece,pos):
    '''
    Sets piece on position pos and adjusts the position attribute of piece. 
    Also the cell at start position is reset, if start position is not equal
    pos. Can also perform a rochade
    '''
    start_pos = piece.get_position()
    self.positions[pos] = piece
    if start_pos != pos:
      self.positions[start_pos] = ''
      piece.set_position(pos)
    # Wenn es eine Rochade sein soll
    if isinstance(piece,King):
      if pos-start_pos == 2:
        self.set_piece(self.get_piece(pos + 1),start_pos)
      if pos-start_pos == -2:
        self.set_piece(self.get_piece(pos - 2),start_pos)
    
  def switch_color(self):
    '''
    Schaltet die Farbe um, um die Farbe des ziehenden Spielers zu bestimmen
    '''
    self.is_white = not self.is_white
    
  def append_history(self, move):
    '''
    Addiert einen Spielzug zur history
    '''
    start, target = move
    piece = self.get_piece(target)
    self.history.append((start,target,piece))
    
  def get_last_move(self):
    '''
    gibt den letzten Zug zurück
    '''
    return self.history[-1] if self.history else (0, 0, -1)
    
  def get_last_moved_piece(self):
    '''
    Gibt die zuletzt bewegte Figur zurück
    '''
    start, target, piece = self.get_last_move()
    return piece
    
  ################################################################################
  # Some test functions
  ################################################################################
    
  def can_be_hit_en_passant(self,pawn):
    '''
    Zur Bedienung der "Schlagen en passant"-Regel.
    '''
    start, target, piece = self.get_last_move()
    if piece == pawn and abs(target-start) == 20 and isinstance(piece,Pawn):
      return True
    return False
  
  def is_check_given(self):
    '''
    Return True, if check is given to one of the players
    '''
    return self.get_king_of_moving_player().is_check_given \
        or self.get_king_of_opponent().is_check_given
  
  
  def is_admissible_piece(self, cell_occupation):
    '''
    True if cell is not empty and piece is of admissible color.
    If check is given, piece must be the attacked king
    '''
    if cell_occupation:
      if self.is_check_given():
        return cell_occupation.is_king_of_moving_player()
      else:
        return cell_occupation.is_moving()
    else:
      return False
  
  def is_valid_move(self,move):
    '''
    True if piece is admissible and piece can reach target cell
    '''
    start, target = move
    piece = self.get_piece(start)
    return self.is_admissible_piece(piece) and piece.is_valid_move(target)

  def move_piece(self,move):
    '''
    Performs the move
    '''
    start_pos, target_pos = move
    piece_to_be_moved = self.get_piece(start_pos)
    if self.is_valid_move(move):
      self.set_piece(piece_to_be_moved,target_pos)
      # Wenn durch den Zug der gegnerische König in Schach gestellt wird:
      opposing_king = self.get_king_of_opponent()
      if not opposing_king.is_safe_position():
        opposing_king.is_check_given = True
        # Wenn der gegnerische König nicht mehr ausweichen kann:
        if not opposing_king.get_safe_positions():
          self.has_finnished = True
      return True
    else:
      return False
      
def newinstance(name,pos):
  '''
  Instantiates a new piece of type name at position p
  '''
  if name == 'B':
    return Pawn(pos)
  if name == 'b':
    return Pawn(pos,False)
  if name == 'T':
    return Rook(pos)
  if name == 't':
    return Rook(pos,False)
  if name == 'L':
    return Bishop(pos)
  if name == 'l':
    return Bishop(pos,False)
  if name == 'S':
    return Knight(pos)
  if name == 's':
    return Knight(pos,False)
  if name == 'D':
    return Queen(pos)
  if name == 'd':
    return Queen(pos,False)
  if name == 'K':
    return King(pos)
  if name == 'k':
    return King(pos,False)
  else:
    return ''


