#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import re       # Das für den Mustervergleich erforderliche Modul "regular expressions""

logging.basicConfig(level=logging.DEBUG) # Setze auf logging.DEBUG, damit Meldungen ausgegeben werden
log = logging.getLogger(__name__)
#######################################################################
# Verschiedene Text-Konstanten, damit man sie alle am gleichen Platz hat
#######################################################################
MSG_GAME_STARTED                    = "Das Spiel hat begonnen!\n"
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
MSG_WINNER                          = "Schachmatt! %s hat gewonnen!\nDas Spiel ist beendet.\n"
MSG_CHECK_GIVEN                     = "Schach!\n"

class Chess():
  '''
  Schachspiel für zwei Spieler für die Kommandozeile.
  Die Gültigkeit von Zügen wird überprüft.
  '''
  has_finnished = False               # Für die Abbruchbedingung
  is_white = True                     # True, wenn weiß am Zug ist
  dic={}                              # Zuordnungen Feldbezeichnungen zu Index
  positions=[]                        # Spielfeld mit Belegungen
  history=[]                          # Um sich die Spielzüge zu merken
  pattern=re.compile('[A-H][1-8]$')   # Für den Mustervergleich bei der Eingabe
  
  def __init__(self):
    # Initialize positions
    #
    # Es werden Reihen à 10 genommen, um bei diagonalen Bewegungn
    # der Figuren den Rand leichter bestimmen zu können. Außerdem
    # oben und unten je eine Reihe mit -1 
    #
    # Die obere Randreihe
    for i in range(10):
      self.positions.append(None)
    # Die 1. Reihe
    self.positions.extend( \
     [None,Rook(self,11),Knight(self,12),Bishop(self,13),Queen(self,14), \
       King(self,15),Bishop(self,16),Knight(self,17),Rook(self,18),None] )
    # Die 2. Reihe
    self.positions.append(None)
    for i in range(21,29):
      self.positions.append(Pawn(self,i))
    self.positions.append(None)
    # Die 3. - 6. Reihe
    for i in range(3,7):
      self.positions.append(None)
      for j in range(i*10 +1,i*10+9):
        self.positions.append('')
      self.positions.append(None)
    # Die 7. Reihe
    self.positions.append(None)
    for i in range(71,79):
      self.positions.append(Pawn(self,i,False))
    self.positions.append(None)
    # Die 8. Reihe
    self.positions.extend( \
      [None,Rook(self,81,False),Knight(self,82,False),Bishop(self,83,False), \
        Queen(self,84,False),King(self,85,False),Bishop(self,86,False), \
        Knight(self,87,False),Rook(self,88,False),None] )
    # Die untere Randreihe
    for i in range(10):
      self.positions.append(None)
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
    self.white_king = self.get_piece(15)
    self.black_king = self.get_piece(85)

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

  def print_position(self,pos):
    '''
    Gibt für die Anzeige des Spiels die Belegung eines Spielfelds zurück
    '''
    res = self.positions[pos] 
    return str(res) if res else STR_EMPTY_CELL
    
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
    Displays the game
    '''
    print STR_BOTTOM_TOP_LINE
    print STR_SEPARATOR
    # positions enthält die Feldbelegungen auf den Feldern 11-18, 21-28,...,81-88
    # Außerdem ist dei erste Reihe unten und nicht oben, weshalb (9-i) und nicht i
    # Das Feld wird mit der Nummer der jeweiligen Reihe am linken und rechten
    # Spielfeldrand dargestellt
    for i in range(1,9):
      str_rank=str(9-i)
      for j in range(1,9):
        str_rank+=" | %s" % self.print_position((9-i)*10+j)
      str_rank+=" | %s" % str(9-i)
      print str_rank
      print STR_SEPARATOR
    print STR_BOTTOM_TOP_LINE
  
  #################################################################
  # Main functions
  #################################################################  
  def start(self):
    '''
    Main Loop
    '''
    while not self.has_finnished:
      self.print_positions()
      print MSG_ROUND % self.get_color()
      self.perform_move()
    print MSG_WINNER % self.get_king_of_opponent().get_color()
  
  def perform_move(self):
    '''
    Performs a move
    '''
    is_valid_move=False
    while not is_valid_move:
      # Zunächst prüfen, ob der ziehende Spieler im Schach steht
      if self.is_check_given():
        print MSG_CHECK_GIVEN
      move = self.get_move()
      is_valid_move = self.move_piece(move)
      if self.has_finnished:  # Will occur when a player is given chess mate
        break
      if not is_valid_move: 
        print MSG_INVALID_MOVE
        continue 
    # Switch from white to black or vice versa to indicate the
    # currently moving player
    self.append_history(move)
    self.switch_color()
      
  def get_move(self):
    '''
    Reads the starting and target cell from commandline input
    thereby validating the plausibility of the input.
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
    if self.is_valid_move(move):
      self.set_piece(piece_to_be_moved,target_pos)
      # Wenn durch den Zug der gegnerische König in Schach gestellt wird:
      opposing_king = self.get_king_of_opponent()
      if not opposing_king.is_safe_position():
        opposing_king.is_check_given = True
        # Wenn der gegnerische König nicht mehr ausweichen kann:
        if not opposing_king.get_admissible_positions(True):
          self.has_finnished = True
      return True
    else:
      return False
    
#######################################################################
# Die Spielfiguren
#######################################################################

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
  position = None
  has_never_been_moved = True

  def __init__(self,game,pos,color=True):
    self.game=game
    self.set_position(pos)
    self.is_white=color
    log.debug("%s initialized with color %s at position %i",\
      self.__class__.__name__,self.get_color(),self.get_position())
    
  def get_position(self):
    return self.position
  
  def set_position(self,pos):
    log.debug("Setting Position of %s at %s to %i",\
      self.__class__.__name__,str(self.get_position()), pos)
    self.position = pos
    self.has_never_been_moved = False
    
  #############################################################################
  # Einige Hilfsfunktionen
  #############################################################################
  
  def get_color(self):
    '''
    Returns the string white or black
    '''
    return STR_WHITE if self.is_white else STR_BLACK
    
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
      while self.is_allowed_cell(step) and not self.game.get_piece(step):
        log.debug("Appending %i", step)
        admissible_positions.append(step)
        step += direction
      if self.is_allowed_cell(step):
        log.debug("Appending %i, because %s belongs to opponent", step, self.game.get_piece(step).__class__.__name__)
        admissible_positions.append(step)      
    return admissible_positions
    
  #############################################################################
  # Einige Prüffunktionen
  #############################################################################
  
  def is_moving(self):
    '''
    True if piece belongs to the moving player
    '''
    return self.game.is_white == self.is_white
   
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
    if target < 0 or target > 99:
      return False
    if self.game.get_piece(target):
      return self.is_white != self.game.get_piece(target).is_white
      # True if opponent's color, False otherwise
    else:
      return self.game.get_piece(target) is not None 
      # True if empty string, i.e a valid but un-occupied position

  def is_piece_of_opponent(self, o):
    '''
    Testet, ob o vom Typ Piece ist und die gegnerische Farbe hat
    '''
    return isinstance(o,Piece) and o.is_white != self.is_white
    
  def is_safe_position(self, simulator=None):
    '''
    simulator simuliert einen Spielzug einer beliebigen Figur,
    die auch die Figur selbst sein kann. Dann wird geprüft, ob die Figur selbst
    auf der Zielposition angegriffen wird, indem geprüft wird, ob irgendeine
    der gegnerischen Figuren die Zielposition auch erreichen kann.
    
    Das builtin filter(Filterfunktion, Liste) filtert Werte aus einer Liste
    anhand einer Filterfunktion, die eine Filterbedingung definiert. filter(lambda x:Funktion(x),Liste) 
    ist eine spezielle Kurzschreibweise und äquivalent zu:
                
                    for x in Liste:
                      if not Funktion(x):
                        Liste.remove(x)
                    return Liste 
    '''
    is_safe_position = True
    opposing_pieces = filter( lambda o: self.is_piece_of_opponent(o) ,self.game.positions)
    pos = self.get_position()
    log.debug("Checking if %s at %i is check given", self.__class__.__name__,pos )
    for piece in opposing_pieces:
      log.debug('Checking if %s at %i attacks',piece.__class__.__name__,piece.get_position())
      admissible_positions = piece.get_admissible_positions()
      if admissible_positions and pos in admissible_positions:
        log.debug( "%s at %i attacks at %i!\n" , piece.__class__.__name__,piece.get_position(),pos)
        is_safe_position = False
        break
    # Nicht vergessen, alles wieder auf Anfang zu setzen:
    if simulator:
      simulator.undo_set_piece()
    return is_safe_position
  
  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i\n",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions()
    if admissible_positions and pos in admissible_positions:
      king = self.game.get_king_of_moving_player()
      log.debug("Checking if King at %i is in danger when %s is moved from %i to %i",king.get_position(),self.__class__.__name__,self.get_position(),pos)
      # Wenn der eigene König nach Durchführung des geplanten Zugs im Schach stünde... 
      if not king.is_safe_position(Simulator(self.game).set_piece(self, pos)):
        return False
      return True
    else:
      return False
      
class Pawn(Piece):
  '''
  Der Bauer kann am wenigsten, hat aber die kompliziertesten Regeln. Vor allem für die Regel 
  "Schlagen en passant"-Regel (vgl. Art 3.7 d der offiziellen Regeln des Weltschachverbands (FIDE), 
  braucht es ein Gedächtnis, ob ein Bauer gerade um zwei Felder nach vorne gerückt ist.
  Der weiße Bauer immer eine vorwärts (+10) und am Anfang zwei vorwärts (+20). Geschlagen wird dann
  immer eins nach schräg links (+9) oder eins nach schräg rechts (+11). Für den schwarzen Bauern gilt
  das negative Vorzeichen.
  '''
  
  def __init__(self,game,pos,color=True):
    super(Pawn,self).__init__(game, pos, color)
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
      is_occupied = bool(self.game.get_piece(target))       
      return is_occupied 
    elif abs(direction) == 1 and self.game.can_be_hit_en_passant(self.game.get_piece(target)):
      return True
    else:
      return self.game.get_piece(target) == ''
      
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
    Erlaubt sind alle Züge, die erlaubt sind.
    '''
    pos = self.get_position()
    log.debug("Going to check Knight at %i...", pos)
    directions = [pos+d for d in self.directions]
    admissible_positions = filter( lambda p : self.is_allowed_cell(p),directions )
    log.debug("Can reach %s",str(admissible_positions))
    return admissible_positions
    
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
    log.debug("Setting Position of King at %s to %i",str(self.get_position()), pos)
    self.position=pos
    if self.is_check_given:
      log.debug("Releasing 'is_check_given'")
      self.is_check_given = False

  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions(True)
    if admissible_positions and pos in admissible_positions:
      return True
    else:
      # Wenn der König schachmatt ist...
      if self.is_check_given and not admissible_positions:
        log.debug("No available position found!")
        self.game.has_finnished = True
      return False

  def get_admissible_positions(self,check_if_attacked=False):
    '''
    Erlaubt sind alle Züge. Solche, die auf eine eigene Figur verweisen oder 
    aus dem Spielfeld heraus führen, werden schon durch chess.is_allowed_move() 
    gefiltert. Damit innerhalb eines Spielzugs nicht durch rekursives Aufrufen 
    von is_safe_position und get_admissible_positions endlos iteriert wird, 
    wird die is_safe_position für den eigenen König nicht durchgeführt.
    '''
    position = self.get_position()
    positions = [position+d for d in self.directions]
    log.debug("Going to check King at %i...", position)
    admissible_positions = filter(lambda pos: self.is_allowed_cell(pos),positions)
    log.debug("Can reach %s", admissible_positions)
    if check_if_attacked:  # Prüfung nur wenn gefordert
      for pos in list(admissible_positions):
        log.debug("Checking position %i\n", pos)
        if not self.is_safe_position(Simulator(self.game).set_piece(self,pos)):
          log.debug("Position %i is not safe!\n", pos)
          admissible_positions.remove(pos)
      if self.has_never_been_moved:
        if self.game.get_piece(position+3).has_never_been_moved\
            and position+1 in admissible_positions\
            and filter(lambda o:isinstance(o,Piece),\
              self.game.get_position()[position+1:position+2]) \
            and self.is_safe_position(Simulator(self.game).set_piece(self,position+2)):
          log.debug("Der %se König kann nach rechts rochieren.")          
          admissible_positions.append(position + 2)
        if self.game.get_piece(position-4).has_never_been_moved\
            and position-1 in admissible_positions\
            and filter(lambda o:isinstance(o,Piece),\
              self.game.get_position()[position-3:position-1]) \
            and self.is_safe_position(Simulator(self.game).set_piece(self,position-2)):
          log.debug("Der %se König kann nach links rochieren.")          
          admissible_positions.append(position - 2)
          
    return admissible_positions
    
class Simulator:
  '''
  Um einen Zug zu simulieren. Merkt sich im Wesentlichen den Ursprungszustand,
  um dahin wieder zurückkehren zu können
  '''

  def __init__(self, game):
    self.game = game
  
  def get_piece(self,pos):
    return self.game.get_piece(pos)
  
  def set_piece(self, piece, target_pos):
    '''
    Wie chess.set_piece, aber mit der Zusatzfunktion, den Ursprungszustand zu
    memorieren.
    
    Gibt den Simulator zurück, um verketten zu können.
    ''' 
    log.debug("Simulating a move...")
    self.piece_to_be_moved = piece
    self.target_piece = self.get_piece(target_pos)
    self.start_pos = piece.get_position()
    self.target_pos = target_pos
    self.has_never_been_moved = piece.has_never_been_moved
    self.is_check_given = piece.is_check_given if isinstance(piece, King) else None
    self.game.set_piece(piece,target_pos)
    return self

  def undo_set_piece(self):
    '''
    Rekonstruiert die Ursprungsstellung
    ''' 
    self.game.set_piece(self.piece_to_be_moved, self.start_pos)
    if self.target_piece:
      self.game.set_piece(self.target_piece,self.target_pos)
    if self.is_check_given:
      log.debug('Restoring is_check_given')
      self.piece_to_be_moved.is_check_given = self.is_check_given
    if self.has_never_been_moved:
      log.debug('Restoring has_never_been_moved')
      self.piece_to_be_moved.has_never_been_moved = self.has_never_been_moved
    log.debug('Simulation finnished')
    return self
    
if __name__ == "__main__":
  game = Chess()
  game.start()
