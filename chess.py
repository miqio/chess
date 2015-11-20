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
MSG_MOVE                            = "Ziehe %s %s von %i nach %i"
STR_EMPTY_CELL                      = " "
MSG_POSITIONS

class Chess():
  has_finnished=False
  is_white=True
  dic={}
  positions=[]
  pattern=re.compile('[A-H][1-8]')
  
  def __init__(self):
    # Initialize map
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

  '''
  Hilfsfunktionen
  '''    
  def get_position(self,pos):
    # Returns numeric position, pos is the string describing the position
    return self.dic[pos]
    
  def get_color(self):
    return STR_WHITE if self.is_white else STR_BLACK
    
  def get_piece(self,pos):
    # Returns piece on position pos or zero
    ret = self.positions[pos]
    return  ret if ret else 
    
  def set_piece(self,piece,pos):
    # sets piece on position position and adjusts the position attribute of piece. Also the cell at start position is reset
    startPos = piece.get_position()
    print MSG_MOVE % (str(piece), piece.get_color(),startPos, pos)
    self.positions[pos] = piece
    self.positions[startPos] = ''
    piece.set_position(pos)
    
  def is_opponent(self,piece):
    return self.is_white != piece.is_white
    
  def print_positions(self):
    print MSG_MOVE & self.get_color()
    print "  | A | B | C | D | E | F | G | H |  "
    print "-------------------------------------"
    for i in range(1,9):
      print "%i | %s | %s | %s | %s | %s | %s | %s | %s | %i " %  (i,str(self.get_piece((i-1)*8)),str(self.get_piece((i-1)*8+1)),str(self.get_piece((i-1)*8+2)),str(self.get_piece((i-1)*8+3)),str(self.get_piece((i-1)*8+4)),str(self.get_piece((i-1)*8+5)),str(self.get_piece((i-1)*8+6)),str(self.get_piece((i-1)*8+7)),i)   
      print "-------------------------------------"
    print "  | A | B | C | D | E | F | G | H |  "
  
  def is_valid_expression(self,pos):
    # Plausibility check for positions entered with raw_input
    if len(pos)!=2:
      return False
    if self.pattern.match(pos):
      return True
    else:
      return False
      
  '''
  Hauptfunktionen
  '''  
  def start(self):
    while not self.has_finnished:
      self.perform_move()
    print MSG_GAME_FINNISHED
  
  def perform_move(self):
    self.print_positions()
    is_wrong_move=True
    while is_wrong_move:
      move = self.get_move()
      is_wrong_move = self.move_piece(move)
    # Switch from white to black or vice versa to indicate the player
    self.is_white = not self.is_white
      
  def get_move(self):
    start, end = '',''
    while not self.is_valid_expression(start):
      start = raw_input("Welche Figur? Gebe die Position an: ")
      if not self.is_valid_expression(start):
        print "Ungültige Eingabe! Versuch es noch mal..."
    while not self.is_valid_expression(end):
      end = raw_input("Wohin? Gebe die Position an: ")
      if not self.is_valid_expression(end):
        print "Ungültige Eingabe! Versuch es noch mal..."
    # return the numeric start and end position
    return self.get_position(start),self.get_position(end)
    
  def move_piece(self,move):
    startPos, endPos = move
    piece_to_be_moved = self.get_piece(startPos)
    piece_on_end_position = self.get_piece(endPos)
    if piece_to_be_moved and self.is_white == piece_to_be_moved.is_white and (not piece_on_end_position or self.is_opponent(piece_on_end_position)) and piece_to_be_moved.is_valid_move(endPos):
      self.set_piece(piece_to_be_moved,endPos)
      if isinstance(piece_on_end_position,King):
        if self.is_white: print "Weiß hat gewonnen!"
        else: print "Schwarz hat gewonnen!"
        self.has_finnished = True
      return False
    else:
      print "Ungültiger Zug. Probier es noch mal."
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
