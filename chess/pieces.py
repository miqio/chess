#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import manager  # Für Zugriff auf Schachbrettfunktionen

log = logging.getLogger(__name__)

class Piece(object):
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
  chessboard = None
  position = None
  has_never_been_moved = True

  def __init__(self,pos,color=True):
    self.set_position(pos)
    self.is_white=color
    log.debug("%s initialized with color %s at position %i",\
      self.__class__.__name__,self.get_color(),self.get_position())
    
  def get_position(self):
    return self.position
  
  def get_chessboard(self):
    if not self.chessboard:
      self.chessboard = manager.get_chessboard()
    return self.chessboard

  def set_position(self,pos):
    log.debug("Setting Position of %s at %s to %i",\
      self.__class__.__name__,str(self.get_position()), pos)
    self.position = pos
    
  #############################################################################
  # Einige Hilfsfunktionen
  #############################################################################
  
  def get_color(self):
    '''
    Returns the string white or black
    '''
    return manager.STR_WHITE if self.is_white else manager.STR_BLACK
    
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
      log.debug("Checking position %i for %s at %i", step, self.__class__.__name__, self.get_position())
      while self.is_allowed_cell(step) and not manager.get_piece(step):
        log.debug("Appending %i", step)
        admissible_positions.append(step)
        step += direction
      if self.is_allowed_cell(step):
        log.debug("Appending %i, because %s belongs to opponent", step, manager.get_piece(step).__class__.__name__)
        admissible_positions.append(step)      
    return admissible_positions
    
  #############################################################################
  # Einige Prüffunktionen
  #############################################################################
  
  def can_be_hit_en_passant(self):
    '''
    Zur Bedienung der "Schlagen en passant"-Regel.
    '''
    return False
    
  def can_be_promoted(self):
    '''
    Zur Bedienung der pawn promotion rule
    '''
    return False
    
  def is_moving(self):
    '''
    True if piece belongs to the moving player
    '''
    return manager.is_white_moving() == self.is_white
   
  def is_king_of_moving_player(self):
    '''
    True if self is king and belongs to the moving player
    '''
    return False

  def is_allowed_cell(self,target):
    '''
    True, if cell is empty or piece on cell is opposing.
    cell_occupation is either of type Piece or None or the empty string.
    Beachte, das an Stellen, wo python einen Wahrheitswert erwartet,
    ein Ausdruck im zweifel zu einem solchen verwandelt wird. Dabei erhält
    die Null, die leere Menge, der leere String immer den Wahrheitswert False,
    wohingegen alles andere automatisch True ist. Die Umwandlung geschieht
    automatisch mit der eingebauten Funktion (builtin) bool(). 
    '''
    if target < 11 or target > 88:
      return False
    elif manager.get_piece(target):
      return self.is_white != manager.get_piece(target).is_white
      # True if opponent's color, False otherwise
    else:
      return manager.get_piece(target) is not None 
      # True if empty string, i.e a valid but un-occupied position

  def is_piece_of_opponent(self, o):
    '''
    Testet, ob o vom Typ Piece ist und die gegnerische Farbe hat
    '''
    return isinstance(o,Piece) and o.is_white != self.is_white
    
  def is_safe_position(self, target_pos=None):
    '''
    Prüft, ob die Figur auf der angegebenen Position in Bedrängnis gerät
    '''
    is_safe_position = True
    pos = target_pos if target_pos else self.get_position()
    opposing_pieces = filter( lambda o: self.is_piece_of_opponent(o) ,manager.get_positions())
    log.debug("Checking if %s at %i is check given", self.__class__.__name__,pos )
    for piece in opposing_pieces:
      log.debug('Checking if %s at %i attacks',piece.__class__.__name__,piece.get_position())
      admissible_positions = piece.get_admissible_positions()
      if admissible_positions and pos in admissible_positions:
        log.debug( "%s at %i attacks at %i!\n" , piece.__class__.__name__,piece.get_position(),pos)
        is_safe_position = False
        break
    return is_safe_position
  
  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    
    Der eigene König darf durch den Zug nicht in Schach geraten.
    '''
    log.debug("Checking if %s can move from %i to %i\n",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions()
    if admissible_positions and pos in admissible_positions:
      log.debug("Checking if King is in danger when %s is moved from %i to %i",self.__class__.__name__,self.get_position(),pos)
      # Wenn der eigene König nach Durchführung des geplanten Zugs im Schach stünde... 
      if not manager.is_safe_position_for_king(self.get_position(), pos):
        return False
      return True
    else:
      return False
      
###############################################################################
# Der Bauer
###############################################################################
      
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
    super(Pawn,self).__init__( pos, color)
    self.directions = (9,10,11) if self.is_white else (-9,-10,-11)
    
  def __str__(self):
    if self.is_white:
      return 'B'
    else:
      return 'b'

  def can_be_hit_en_passant(self):
    '''
    Zur Bedienung der "Schlagen en passant"-Regel.
    '''
    start, target, piece = manager.get_last_move()
    # Wenn pawn gerade erst um zwei Felder gezogen wurde und tatsächlich ein Bauer
    # ist
    if piece == self and abs(target-start) == 20:
      return True
    return False
  
  def can_be_promoted(self):
    '''
    Falls der Bauerin der letzten Reihe angekommen ist...
    '''
    if self.is_white and self.get_position()/80 ==1:
      return True
    elif not self.is_white and self.get_position()/10 ==1:
      return True
    else:
      return False
      
  def is_allowed_cell(self,target, direction = None):
    '''
    Bei Bauern ist es richtungsabhängig, ob sie auf besetzte Felder können. 
    '''
    # Für diagonale Richtungen muss das benachbarte Feld mit einem Gegner besetzt sein...
    is_occupied = bool(manager.get_piece(target))
    if abs(direction) == 9:
      pos_en_passant = target + direction + direction/abs(direction)
    elif abs(direction) == 11:
      pos_en_passant = target + direction - direction/abs(direction)
    else:
      pos_en_passant = 10
    p = manager.get_piece(pos_en_passant)
    is_occupied_en_passant = bool(p)
    if abs(direction) in [9,11]:
      if super(Pawn,self).is_allowed_cell(target):
        if is_occupied:
          return True
        elif is_occupied_en_passant and p.can_be_hit_en_passant():
          return True
        else:
          return False
      else:
        return False
    # Ansonsten geht es nur für unbesetzte Felder
    else:
      return manager.get_piece(target) == ''
      
  def get_max_steps(self,direction):
    '''
    Bauern können nur aus der Startreihe zwei Schritte gehen
    '''
    pos = self.get_position()
    if self.is_white:
      if pos/20 == 1 and direction == 10:
        return 2
      else:
        return 1
    else:
      if pos/70 == 1 and direction == -10:
        return 2
      else:
        return 1

  def get_admissible_positions(self):
    '''
    Berechnet eine Liste der erlaubten Zielpositionen des Bauern.
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

###############################################################################
# Der Turm
###############################################################################
      
class Rook(Piece):
  
  directions = (-10,-1,1,10)

  def __str__(self):
    if self.is_white:
      return 'T'
    else:
      return 't'
    
###############################################################################
# Der Springer
###############################################################################
      
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
    
###############################################################################
# Der Läufer
###############################################################################
      
class Bishop(Piece):

  directions = (-11,-9,9,11)

  def __str__(self):
    if self.is_white:
      return 'L'
    else:
      return 'l'
    
###############################################################################
# Die Dame
###############################################################################
      
class Queen(Piece):

  directions = (-11,-10,-9,-1,1,9,10,11)

  def __str__(self):
    if self.is_white:
      return 'D'
    else:
      return 'd'
    
###############################################################################
# Der König
###############################################################################
      
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
    super(King,self).set_position(pos)
    if self.is_check_given:
      log.debug("Releasing 'is_check_given'")
      self.is_check_given = False

  def is_valid_move(self, pos):
    '''
    Prüft, ob der König auf die angestrebte Zielposition darf.
    
    Der König darf nicht im Schach stehen.
    '''
    log.debug("Checking if %s can move from %i to %i",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_safe_positions()
    if admissible_positions and pos in admissible_positions:
      return True
    else:
      # Wenn der König schachmatt ist...
      if self.is_check_given and not admissible_positions:
        log.debug("No available position found!")
        manager.finnish_game()
      return False

  def get_admissible_positions(self):
    '''
    Berechnet die grundsätzlich für den König erreichbaren Felder
    '''
    position = self.get_position()
    positions = [position+d for d in self.directions]
    log.debug("Going to check King at %i...", position)
    admissible_positions = filter(lambda pos: self.is_allowed_cell(pos),positions)
    log.debug("Can reach %s", admissible_positions)
    # Hinzu kommen noch die Felder, auf die der König durch rochieren gelangen 
    # könnte
    if self.has_never_been_moved:
      if self.is_white:
        rooks = manager.get_white_rooks()  
      else: 
        rooks = manager.get_black_rooks()
      for r in rooks:
        if r.has_never_been_moved:
          pos_r = r.get_position()
          pos_k = self.get_position()
          # Zunächst die Prüfung für die große Rochade...
          if pos_r < pos_k:
            # Keine Figur darf zwischen Turm und König stehen...
            fields = manager.get_positions()[pos_r+1:pos_k]
            if not filter(lambda p: isinstance(p,Piece),fields):
              is_safe_position = True
              # ...und der König auf seinem Weg auch nirgends im Schach stehen...
              for pos in range(pos_r+2,pos_k):
                if not self.is_safe_position(pos):
                  is_safe_position = False
              if is_safe_position:
                log.debug("Die große Rochade ist für %s möglich.",self.get_color())          
                admissible_positions.append(position - 2)
          # ...dann die für die kleine Rochade...
          else:
            fields = manager.get_positions()[pos_k+1:pos_r]
            if not filter(lambda p: isinstance(p,Piece),fields):
              is_safe_position = True
              for pos in range(pos_k+1,pos_r-1):
                if not self.is_safe_position(pos):
                  is_safe_position = False
              if is_safe_position:
                log.debug("Die kleine Rochade ist für %s möglich.",self.get_color())          
                admissible_positions.append(position + 2)
    return admissible_positions         
    
  def get_safe_positions(self):
    '''
    Löscht aus den erlaubten Positionen diejenigen, auf denen der König im
    Schach stehen würde 
    '''
    admissible_positions = self.get_admissible_positions()
    for pos in list(admissible_positions):
      log.debug("Checking position %i\n", pos)
      if not self.is_safe_position(pos):
        log.debug("Position %i is not safe!\n", pos)
        admissible_positions.remove(pos)
    return admissible_positions

