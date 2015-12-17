#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging  # Um Meldungen auszugeben
import re       # Das für den Mustervergleich erforderliche Modul "regular expressions""
import manager  # chess.manager hält die Textkonstanten

class IFChessboard():
  '''
  Benutzerschnittstelle für das Schachspiel.
  '''
  # Zuordnungen Feldbezeichnungen zu Indizes
  dic = {
    'A1': 11, 'A2': 21, 'A3': 31, 'A4': 41, 'A5': 51, 'A6': 61, 'A7': 71, 'A8': 81, 
    'B1': 12, 'B2': 22, 'B3': 32, 'B4': 42, 'B5': 52, 'B6': 62, 'B7': 72, 'B8': 82, 
    'C1': 13, 'C2': 23, 'C3': 33, 'C4': 43, 'C5': 53, 'C6': 63, 'C7': 73, 'C8': 83, 
    'D1': 14, 'D2': 24, 'D3': 34, 'D4': 44, 'D5': 54, 'D6': 64, 'D7': 74, 'D8': 84, 
    'E1': 15, 'E2': 25, 'E3': 35, 'E4': 45, 'E5': 55, 'E6': 65, 'E7': 75, 'E8': 85, 
    'F1': 16, 'F2': 26, 'F3': 36, 'F4': 46, 'F5': 56, 'F6': 66, 'F7': 76, 'F8': 86, 
    'G1': 17, 'G2': 27, 'G3': 37, 'G4': 47, 'G5': 57, 'G6': 67, 'G7': 77, 'G8': 87, 
    'H1': 18, 'H2': 28, 'H3': 38, 'H4': 48, 'H5': 58, 'H6': 68, 'H7': 78, 'H8': 88
  }
  pattern=re.compile('[A-H][1-8]$')   # Für den Mustervergleich bei der Eingabe
  
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
    print manager.STR_BOTTOM_TOP_LINE
    print manager.STR_SEPARATOR
    # positions enthält die Feldbelegungen auf den Feldern 11-18, 21-28,...,81-88
    # Außerdem ist dei erste Reihe unten und nicht oben, weshalb (9-i) und nicht i
    # Das Feld wird mit der Nummer der jeweiligen Reihe am linken und rechten
    # Spielfeldrand dargestellt
    rank_list = positions.splitlines()
    for i in range(8):
      str_rank=str(8-i)
      pos_list = rank_list[7-i].split(',')
      for j in range(8):
        s = pos_list[j] if pos_list[j] else manager.STR_EMPTY_CELL
        str_rank+=" | %s" % s
      str_rank+=" | %s" % str(8-i)
      print str_rank
      print manager.STR_SEPARATOR
    print manager.STR_BOTTOM_TOP_LINE
  
  def display_msg(self, msg):
    print msg
  
  def get_move(self):
    '''
    Reads the starting and target cell from commandline input
    thereby validating the plausibility of the input.
    '''
    start, target = '',''
    while not self.is_valid_expression(start.capitalize()):
      start = raw_input(manager.MSG_ASK_FOR_PIECE)
      if not self.is_valid_expression(start.capitalize()):
        print manager.MSG_INVALID_INPUT
    while not self.is_valid_expression(target.capitalize()):
      target = raw_input(manager.MSG_ASK_FOR_POSITION)
      if not self.is_valid_expression(target.capitalize()):
        print manager.MSG_INVALID_INPUT
    # return the numeric start and end position
    return self.get_position(start.capitalize()),self.get_position(target.capitalize())
    
  def get_piece(self):
    '''
    Reads the starting and target cell from commandline input
    thereby validating the plausibility of the input.
    '''
    piece = ''
    if manager.is_white_moving():
      while not piece in ['L','T','S','D']:
        piece = raw_input(manager.MSG_ASK_FOR_NEW_PIECE)
        if not piece in ['L','T','S','D']:
          print manager.MSG_INVALID_INPUT
    else:
      while not piece in ['l','t','s','d']:
        piece = raw_input(manager.MSG_ASK_FOR_NEW_PIECE)
        if not piece in ['l','t','s','d']:
          print manager.MSG_INVALID_INPUT
    # return the piece name
    return piece
    

