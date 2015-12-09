# -*- coding: utf-8 -*-

import re       # Das für den Mustervergleich erforderliche Modul "regular expressions"

STR_EMPTY_CELL                      = " "
STR_BOTTOM_TOP_LINE                 = "  | A | B | C | D | E | F | G | H |  "
STR_SEPARATOR                       = "-------------------------------------"
MSG_ASK_FOR_PIECE                   = "\nWelche Figur? Gebe die Position an: "
MSG_ASK_FOR_POSITION                = "\nWohin? Gebe die Position an: "
MSG_INVALID_INPUT                   = "Ungültige Eingabe! Probier es noch einmal!\n"

class IFChessboard():
  '''
  Benutzerschnittstelle für das Schachspiel.
  '''
  dic={}                              # Zuordnungen Feldbezeichnungen zu Index
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
    # Die Könige merken, um später zu erkennen, ob sich diese im Schach 
    # befinden

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
  def display_game(self,positions):
    '''
    Displays the game
    '''
    print STR_BOTTOM_TOP_LINE
    print STR_SEPARATOR
    # positions enthält die Feldbelegungen auf den Feldern 11-18, 21-28,...,81-88
    # Außerdem ist dei erste Reihe unten und nicht oben, weshalb (9-i) und nicht i
    # Das Feld wird mit der Nummer der jeweiligen Reihe am linken und rechten
    # Spielfeldrand dargestellt
    rank_list = positions.splitlines()
    rank_list.reverse()
    for i in range(8):
      pos_list = rank_list[i].split(',')
      str_rank=str(8-i)
      for j in range(8):
        s = pos_list[j] if pos_list[j] else STR_EMPTY_CELL
        str_rank+=" | %s" % s
      str_rank+=" | %s" % str(8-i)
      print str_rank
      print STR_SEPARATOR
    print STR_BOTTOM_TOP_LINE
  
  def display_msg(self, msg):
    print msg
  
  def get_move(self):
    '''
    Reads the starting and target cell from commandline input
    thereby validating the plausibility of the input.
    '''
    start, target = '',''
    while not self.is_valid_expression(start.capitalize()):
      start = raw_input(MSG_ASK_FOR_PIECE)
      if not self.is_valid_expression(start.capitalize()):
        print MSG_INVALID_INPUT
    while not self.is_valid_expression(target.capitalize()):
      target = raw_input(MSG_ASK_FOR_POSITION)
      if not self.is_valid_expression(target.capitalize()):
        print MSG_INVALID_INPUT
    # return the numeric start and end position
    return self.get_position(start.capitalize()),self.get_position(target.capitalize())

