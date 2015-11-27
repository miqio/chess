#!/usr/bin/python
# -*- coding: utf-8 -*-

import re   # Das für den Mustervergleich erforderliche Modul "regular expressions""

#######################################################################
# Verschiedene Text-Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
MSG_GAME_FINNISHED                  = "Das Spiel ist beendet.\n"
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
MSG_WINNER                          = "Schachmatt! %s hat gewonnen!\n"
MSG_CHECK_GIVEN                     = "Schach!\n"

class Chess():
  '''
  Simple game for two players that parses move from command line
  and displays them, if they could be validated
  '''
  has_finnished = False
  is_white = True
  is_not_check_given = True
  dic={}
  positions=[]
  pattern=re.compile('[A-H][1-8]$')   # Für den Mustervergleich bei der Eingabe
  
  def __init__(self):
    # Initialize dic. 
    # 
    # Die üblichen Feldbezeichnungen werden den entsprechenden 
    # Indizes in positions (s.u.) zugeordnet. Spieler können ihre Züge
    # damit auf die gewohnte Weise eingeben, etwa B2 nach B3. 
    ind=10
    letters=('A','B','C','D','E','F','G','H')
    numbers=(1,2,3,4,5,6,7,8)
    for number in numbers:
      ind+=1
      for letter in letters:
        self.dic[letter+str(number)] = ind
        ind+=1
      ind+=1
    # Initialize positions
    #
    # Es werden Reihen à 10 genommen, um bei diagonalen Bewegungn
    # der Figuren den Rand leichter bestimmern zu können. Außerdem
    # oben und unten je eine Reihe mit -1 
    #
    # Die obere Randreihe
    for i in range(10):
      self.positions.append(-1)
    # Die 1. Reihe
    self.positions.extend( \
     [-1,Rook(self,11),Knight(self,12),Bishop(self,13),King(self,14), \
       Queen(self,15),Bishop(self,16),Knight(self,17),Rook(self,18),-1] )
    # Die 2. Reihe
    self.positions.append(-1)
    for i in range(21,29):
      self.positions.append(Pawn(self,i))
    self.positions.append(-1)
    # Die 3. - 6. Reihe
    for i in range(3,7):
      self.positions.append(-1)
      for j in range(i*10 +1,i*10+9):
        self.positions.append('')
      self.positions.append(-1)
    # Die 7. Reihe
    self.positions.append(-1)
    for i in range(71,79):
      self.positions.append(Pawn(self,i,False))
    self.positions.append(-1)
    # Die 8. Reihe
    self.positions.extend( \
      [-1,Rook(self,81,False),Knight(self,82,False),Bishop(self,83,False), \
        King(self,84,False),Queen(self,85,False),Bishop(self,86,False), \
        Knight(self,87,False),Rook(self,88,False),-1] )
    # Die untere Randreihe
    for i in range(10):
      self.positions.append(-1)
    # Die Könige merken, um später zu erkennen, ob sich diese im Schach 
    # befinden
    self.white_king = self.get_piece(14)
    self.black_king = self.get_piece(84)

  #####################################################################
  # Hilfsfunktionen
  #####################################################################
  def get_position(self,pos):
    '''
    Returns numeric position, pos is the string describing the position,
    e.g. pos = 'F6'
    
    Durch die Testfunktion is_valid_expression() werden schon mit der 
    Eingabe falsche Feldbezeichnungen ausgeschlossen, weshalb eine 
    Fehlerbehandlung an dieser Stelle nicht erforderlich ist.
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
  
  def get_king_of_opponent(self):
    '''
    Return the king of the opponent
    '''
    if not self.is_white:
      return self.white_king
    else:
      return self.black_king

  def get_king_of_current_player(self):    
    '''
    Return the king of the current player
    '''
    if self.is_white:
      return self.white_king
    else:
      return self.black_king

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
    
  def is_admissible_piece(self, cell_occupation):
    '''
    True if cell is not empty and piece is of admissible color.
    If check is given, piece must be the attacked king
    '''
    if cell_occupation and self.is_not_check_given:
      return self.is_white == cell_occupation.is_white
    elif not self.is_not_check_given:
      return cell_occupation == self.get_king_of_current_player()
    else:
      return False
  
  def is_allowed_cell(self,cell_occupation):
    '''
    True, if cell is empty or piece on cell is opposing.
    cell_occupation is either of type Piece or None
    '''
    return self.is_white != cell_occupation.is_white if cell_occupation else True
    
  def is_allowed_move(self,move):
    '''
    True if piece and target cell are admissible and piece can reach target cell
    '''
    start, target = move
    piece, cell_occupation = self.get_piece(start), self.get_piece(target)
    return self.is_admissible_piece(piece) and self.is_allowed_cell(cell_occupation) and piece.is_valid_move(target)
  
  def is_valid_expression(self,pos):
    '''
    Plausibility check a position entered with raw_input
    Allowed is only a combination of a capital letter from A to H and a number between 
    1 and 8, e.g. F6
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
    print STR_BOTTOM_TOP_LINE
    print STR_SEPARATOR
    for i in range(1,9):
      str_rank=str(i)
      for j in range(1,9):
        str_rank+=" | %s" % self.print_position(i*10+j)
      str_rank+=" | %i" % i
      print str_rank
      print STR_SEPARATOR
    print STR_BOTTOM_TOP_LINE
    print MSG_ROUND % self.get_color()
  
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
    start, target = '',''
    while not self.is_valid_expression(start):
      start = raw_input(MSG_ASK_FOR_PIECE)
      if not self.is_valid_expression(start):
        print MSG_INVALID_INPUT
    while not self.is_valid_expression(target):
      target = raw_input(MSG_ASK_FOR_POSITION)
      if not self.is_valid_expression(target):
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
    if self.is_allowed_move(move):
      self.set_piece(piece_to_be_moved,target_pos)
      # Check, if the opposing king is reachable after the move
      # and set self.is_not_check_given to False
      opposing_king = self.get_king_of_opponent()
      pos_king = opposing_king.get_position()
      # Wenn durch den Zug der gegnerische König in Schach gestellt wird:
      if pos_king in piece_to_be_moved.get_admissible_positions():
        print MSG_CHECK_GIVEN
        self.is_not_check_given = False
      # Wenn der gegnerische König schachmatt ist...
      if not self.is_not_check_given and\
       not opposing_king.get_admissible_positions() and\
       not piece_to_be_moved.is_safe_position(target_pos):
        print MSG_WINNER % self.get_color()
        self.has_finnished = True
      if isinstance(piece_to_be_moved,King) and not self.is_not_check_given:
        self.is_not_check_given = True
      return False
    else:
      print MSG_INVALID_MOVE
      return True
    
#######################################################################
# Die Spielfiguren
#######################################################################

class Piece:

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

  def __init__(self,game,pos,color=True):
    self.game=game
    self.set_position(pos)
    self.is_white=color
    
  def get_position(self):
    return self.position
    
  def set_position(self,pos):
    self.position=pos
    
  def get_color(self):
    return STR_WHITE if self.is_white else STR_BLACK
    
  def get_sign(self):
    '''
    Returns +1 if self.is_white and -1 otherwise
    '''
    return (2*int(self.is_white)-1)

  def is_safe_position(self, pos):
    '''
    Return True, if not in reach of opposing pieces
    '''
    opposing_pieces = filter(lambda o: isinstance(o,Piece) and\
     o.is_white != self.is_white, self.game.positions)
    for piece in opposing_pieces:
      if isinstance(piece,King):
        pos_king = piece.get_position()
        admissible_positions = [pos_king+p for p in piece.directions]
      elif isinstance(piece,Pawn):
        pos_pawn = piece.get_position()
        sign_pawn = piece.get_sign()
        admissible_positions = [pos_pawn+sign_pawn*9,pos_pawn+sign_pawn*11]
      else:
        admissible_positions = piece.get_admissible_positions()
      if pos in admissible_positions:
        return False
    return True
  
  def get_admissible_positions(self):
    admissible_positions=[]
    directions = list(self.directions)
    while directions:
      pos = self.get_position()
      direction = directions.pop()
      step = pos + direction
      while not self.game.get_piece(step):
        admissible_positions.append(step)
        step += direction
      admissible_positions.append(step)
    return admissible_positions
    
  def is_valid_move(self, pos):
    admissible_positions = self.get_admissible_positions()
    if pos in admissible_positions:
      return True
    else:
      return False
      
class Pawn(Piece):
  '''
  Darf immer eine vorwärts (+10) und am Anfang zwei vorwärts (+20). Geschlagen wird dann
  immer eins nach schräg links (+9) oder eins nach schräg rechts (+11)
  '''
  
  def __str__(self):
    if self.is_white:
      return 'B'
    else:
      return 'b'

  def get_admissible_positions(self):
    '''
    Bauern haben je nach Position und Position gegnerischer Figuren unterschiedliche
    Schrittrichtungen
    '''
    self_pos = self.get_position()
    sign_self = self.get_sign()
    # Ein Schritt nach vorne geht immer (wenn nicht, wird das schon durch 
    # chess.is_allowed_move() erkannt), deshalb:
    if not self.game.get_piece(self_pos+10*sign_self):
      admissible_positions = [self_pos+10*sign_self]
      # Zwei Schritte nach vorne sind möglich, wenn keiner im Weg steht und
      # die Bauern aus der Startreihe bewegt werden sollen, also:
      if not self.game.get_piece(self_pos+20*sign_self) and (self_pos/20 == 1 or self_pos/70 == 1):
        admissible_positions.append(self_pos+20*sign_self)   
    # Wenn einer im Weg steht, geht es nicht nach vorne:
    else:
      admissible_positions =[]
    # Wenn eine Figur schräg links oder rechts mit einem Schritt erreicht werden
    # kann, ist auch das eine erlaubte Position. Folglich:                     
    for p in [sign_self*9,sign_self*11]:        
      if self.game.get_piece(self_pos+p):      
        admissible_positions.append(self_pos+p)
    return admissible_positions
    
class Rook(Piece):
  
  directions = (-10,-1,1,10)

  def __str__(self):
    if self.is_white:
      return 'T'
    else:
      return 't'
    
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
    Erlaubt sind alle Züge. Solche, die auf eine eigene Figur Verweise oder aus dem
    Spielfeld heraus führen, werden schon durch chess.is_allowed_move() gefiltert.
    '''
    pos = self.get_position()
    return [pos+p for p in self.directions] 
    
class Bishop(Piece):

  directions = (-11,-9,9,11)

  def __str__(self):
    if self.is_white:
      return 'L'
    else:
      return 'l'
    
class Queen(Piece):

  directions = (-11,-10,-9,-1,1,9,10,11)

  def __str__(self):
    if self.is_white:
      return 'D'
    else:
      return 'd'
    
class King(Piece):

  directions = (-11,-10,-9,-1,1,9,10,11)

  def __str__(self):
    if self.is_white:
      return 'K'
    else:
      return 'k'
  
  def get_admissible_positions(self):
    '''
    Erlaubt sind alle Züge. Solche, die auf eine eigene Figur verweisen oder aus dem
    Spielfeld heraus führen, werden schon durch chess.is_allowed_move() gefiltert.
    '''
    position = self.get_position()
    admissible_positions = [position+p for p in self.directions] 
    print "Prüfe König %s auf %i" % (str(self),position)
    for pos in admissible_positions:
      if not self.is_safe_position(pos):
        admissible_positions.remove(pos)
    return admissible_positions
