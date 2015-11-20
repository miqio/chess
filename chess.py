#!/usr/bin/python
# -*- coding: utf-8 -*-

import re # Das für den Mustervergleich erforderliche Modul

#######################################################################
# Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
MSG_GAME_FINNISHED                  = "Das Spiel ist beendet.\n"
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
MSG_WINNER                          = "%s hat gewonnen!\n"

class Chess():
  '''
  Simple game for two players that parses move from command line
  and displays them, if they could be validated
  '''
  has_finnished=False
  is_white=True
  dic={}
  positions=[]
  pattern=re.compile('[A-H][1-8]$')
  
  def __init__(self):
    # Initialize dic
    ind=0
    letters=('A','B','C','D','E','F','G','H')
    numbers=(1,2,3,4,5,6,7,8)
    for number in numbers:
      for letter in letters:
        self.dic[letter+str(number)] = ind
        ind+=1
    # Initialize positions
    self.positions.extend( [Rook(0),Knight(1),Bishop(2),King(3),Queen(4),Bishop(5),Knight(6),Rook(7)] )
    for i in range(8,16):
      self.positions.append(Pawn(i))
    for i in range(16,48):
      self.positions.append('')
    for i in range(48,56):
      self.positions.append(Pawn(i,False))
    self.positions.extend( [Rook(56,False),Knight(57,False),Bishop(58,False),King(59,False),Queen(60,False),Bishop(61,False),Knight(62,False),Rook(63,False)] )

  #####################################################################
  # Hilfsfunktionen
  #####################################################################
  def get_position(self,pos):
    '''
    Returns numeric position, pos is the string describing the position
    '''
    return self.dic[pos]
    
  def get_color(self):
    '''
    Return the color of the current move
    '''
    return STR_WHITE if self.is_white else STR_BLACK
    
  def get_piece(self,pos):
    '''
    Returns piece on position pos or None
    '''
    return  self.positions[pos] 
    
  def print_position(self,pos):
    '''
    Returns a string representing a position
    '''
    res = self.positions[pos] 
    return str(res) if res else STR_EMPTY_CELL
    
  def set_piece(self,piece,pos):
    '''
    Sets piece on position position and adjusts the position attribute of piece. 
    Also the cell at start position is reset
    '''
    startPos = piece.get_position()
    print MSG_MOVING % (str(piece), piece.get_color(),startPos, pos)
    self.positions[pos] = piece
    self.positions[startPos] = ''
    piece.set_position(pos)
  
  ################################################################################
  # Some test functions
  ################################################################################
    
  def is_allowed_cell(self,cell_occuption):
    '''
    True, if cell is empty or piece on cell is opposing.
    cell_occupation is either of type Piece or None
    '''
    return self.is_white != cell_occuption.is_white if cell_occuption else True
  
  def is_admissible_piece(self, cell_occupation):
    '''
    True if cell is not empty and piece is of admissible color
    '''
    return self.is_white == cell_occuption.is_white if cell_occuption else False
  
  def is_allowed_move(self,piece,target_cell_occupation):
    '''
    True if piece and target cell are admissible
    '''
    return self.is_admissible_piece(piece) and self.is_allowed_cell(target_cell_occupation)
  
  def is_valid_expression(self,pos):
    '''
    Plausibility check a position entered with raw_input
    '''
    if self.pattern.match(pos):
      return True
    else:
      return False
      
  ##################################################################################
  # Display functions
  ##################################################################################
  def print_positions(self):
    '''
    Displays the positions
    '''
    print MSG_ROUND & self.get_color()
    print STR_BOTTOM_TOP_LINE
    print STR_SEPARATOR
    for i in range(1,9):
      str_rank=str(i)
      for j in range(0,8):
        str_rank+="|%s" % self.print_position((i-1)*8+j)
      str_rank+="|%i" % i
      print str_rank
      print STR_SEPARATOR
    print STR_BOTTOM_TOP_LINE
  
  #################################################################
  # Main functions
  #################################################################  
  def start(self):
    while not self.has_finnished:
      self.perform_move()
    print MSG_GAME_FINNISHED
  
  def perform_move(self):
    '''
    Performs a move
    '''
    self.print_positions()
    is_wrong_move=True
    while is_wrong_move:
      move = self.get_move()
      is_wrong_move = self.move_piece(move)
    # Switch from white to black or vice versa to indicate the
    # currently allowed player
    self.is_white = not self.is_white
      
  def get_move(self):
    '''
    Reads the starting end ending cell from commandline input
    thereby validating the plausibility of the input.
    This also toggles the indicator of the color moving
    '''
    start, end = '',''
    while not self.is_valid_expression(start):
      start = raw_input(MSG_ASK_FOR_PIECE)
      if not self.is_valid_expression(start):
        print MSG_INVALID_INPUT
    while not self.is_valid_expression(end):
      target = raw_input(MSG_ASK_FOR_POSITION)
      if not self.is_valid_expression(end):
        print MSG_INVALID_INPUT
    # return the numeric start and end position
    return self.get_position(start),self.get_position(target)
    
  def move_piece(self,move):
    '''
    Performs the move
    '''
    start_pos, target_pos = move
    piece_to_be_moved = self.get_piece(start_pos)
    piece_on_end_position = self.get_piece(target_pos)
    if self.is_allowed_move(piece_to_be_moved,piece_on_end_position):
      self.set_piece(piece_to_be_moved,target_pos)
      if isinstance(piece_on_end_position,King):
        print MSG_WINNER % self.get_color()
        self.has_finnished = True
      return False
    else:
      print MSG_INVALID_MOVE
      return True
      
class Piece:

  def __init__(self,pos,color=True):
    self.set_position(pos)
    self.is_white=color
    
  def get_position(self):
    return self.position
    
  def set_position(self,pos):
    self.position=pos
    
class Pawn(Piece):
  def __str__(self):
    if self.is_white:
      return 'B'
    else:
      return 'b'
  
  def get_color(self):
    return STR_WHITE if self.is_white else STR_BLACK

  def is_valid_move(self, pos):
    # TO BE DONE
    return True
    
class Rook(Piece):
  def __str__(self):
    if self.is_white:
      return 'T'
    else:
      return 't'
  
  def is_valid_move(self, pos):
    # TO BE DONE
    return True
    
class Knight(Piece):
  def __str__(self):
    if self.is_white:
      return 'S'
    else:
      return 's'
  
  def is_valid_move(self, pos):
    # TO BE DONE
    return True
    
class Bishop(Piece):
  def __str__(self):
    if self.is_white:
      return 'L'
    else:
      return 'l'
  
  def is_valid_move(self, pos):
    # TO BE DONE
    return True
    
class Queen(Piece):
  def __str__(self):
    if self.is_white:
      return 'D'
    else:
      return 'd'
  
  def is_valid_move(self, pos):
    # TO BE DONE
    return True
    
class King(Piece):
  def __str__(self):
    if self.is_white:
      return 'K'
    else:
      return 'k'
  
  def is_valid_move(self, pos):
    # TO BE DONE
    return True
