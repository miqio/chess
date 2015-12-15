#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging  # Um Meldungen auszugeben
import re       # Das für den Mustervergleich erforderliche Modul "regular expressions""
import argparse # Damit beim Programmaufruf Werte übergeben werden können

parser = argparse.ArgumentParser(description="Schachspiel für die Kommandozeile und zwei Spieler")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-p", "--positions", default=None, help="String containing the positions")
args = parser.parse_args()

log_level = logging.DEBUG if args.verbose else logging.WARN
positions = args.positions

logging.basicConfig(level=log_level) # Setze auf logging.DEBUG, damit Meldungen ausgegeben werden
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

CHESSBOARD = None           # Das aktuelle Schachspiel mit seinen Figuren
INTERFACE = None            # Die Benutzerschnittstelle

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

  def __init__(self,pos,color=True):
    self.position = pos
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
      while self.is_allowed_cell(step) and not get_chessboard().get_piece(step):
        log.debug("Appending %i", step)
        admissible_positions.append(step)
        step += direction
      if self.is_allowed_cell(step):
        log.debug("Appending %i, because %s belongs to opponent", step, get_chessboard().get_piece(step).__class__.__name__)
        admissible_positions.append(step)      
    return admissible_positions
    
  #############################################################################
  # Einige Prüffunktionen
  #############################################################################
  
  def is_moving(self):
    '''
    True if piece belongs to the moving player
    '''
    return get_chessboard().is_white == self.is_white
   
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
    if get_chessboard().get_piece(target):
      return self.is_white != get_chessboard().get_piece(target).is_white
      # True if opponent's color, False otherwise
    else:
      return get_chessboard().get_piece(target) is not None 
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
    opposing_pieces = filter( lambda o: self.is_piece_of_opponent(o) ,get_chessboard().positions)
    log.debug("Checking if %s at %i is check given", self.__class__.__name__,pos )
    for piece in opposing_pieces:
      log.debug('Checking if %s at %i attacks',piece.__class__.__name__,pos)
      admissible_positions = piece.get_admissible_positions()
      if admissible_positions and pos in admissible_positions:
        log.debug( "%s at %i attacks at %i!\n" , piece.__class__.__name__,piece.get_position(),pos)
        is_safe_position = False
        break
    return is_safe_position
  
  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i\n",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_admissible_positions()
    if admissible_positions and pos in admissible_positions:
      log.debug("Checking if King is in danger when %s is moved from %i to %i",self.__class__.__name__,self.get_position(),pos)
      # Wenn der eigene König nach Durchführung des geplanten Zugs im Schach stünde... 
      if not Simulator(self.get_position(), pos).is_safe_position_for_king():
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
  
  def __init__(self,pos,color=True):
    super(Pawn,self).__init__( pos, color)
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
    super(King,self).set_position(pos)
    if self.is_check_given:
      log.debug("Releasing 'is_check_given'")
      self.is_check_given = False

  def is_valid_move(self, pos):
    '''
    Prüft, ob die Figur auf die angestrebte Zielposition darf.
    '''
    log.debug("Checking if %s can move from %i to %i",self.__class__.__name__,self.get_position(),pos)
    admissible_positions = self.get_safe_positions()
    if admissible_positions and pos in admissible_positions:
      return True
    else:
      # Wenn der König schachmatt ist...
      if self.is_check_given and not admissible_positions:
        log.debug("No available position found!")
        get_chessboard().has_finnished = True
      return False

  def get_admissible_positions(self):
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
    if self.has_never_been_moved:
      rooks = get_chessboard().white_rooks if self.is_white else get_chessboard().black_rooks
      for r in rooks:
        if r.has_never_been_moved:
          pos_r = r.get_position()
          pos_k = self.get_position()
          if pos_r < pos_k:
            fields = get_chessboard().positions[pos_r+1:pos_k]
            if not filter(lambda p: isinstance(p,Piece),fields):
              is_safe_position = True
              for pos in range(pos_r+1,pos_k):
                if not self.is_safe_position(pos):
                  is_safe_position = False
              if is_safe_position:
                log.debug("Der %se König kann nach links rochieren.",self.get_color())          
                admissible_positions.append(position - 2)
          else:
            fields = get_chessboard().positions[pos_k+1:pos_r]
            if not filter(lambda p: isinstance(p,Piece),fields):
              is_safe_position = True
              for pos in range(pos_k+1,pos_r):
                if not self.is_safe_position(pos):
                  is_safe_position = False
              if is_safe_position:
                log.debug("Der %se König kann nach rechts rochieren.",self.get_color())          
                admissible_positions.append(position + 2)
    return admissible_positions         
    
  def get_safe_positions(self):
    admissible_positions = self.get_admissible_positions()
    for pos in list(admissible_positions):
      log.debug("Checking position %i\n", pos)
      if not self.is_safe_position(pos):
        log.debug("Position %i is not safe!\n", pos)
        admissible_positions.remove(pos)
    return admissible_positions

class Simulator:
  '''
  Um einen Zug zu simulieren. Merkt sich im Wesentlichen den Ursprungszustand,
  um dahin wieder zurückkehren zu können
  '''
  chessboard=None

  def __init__(self, start_pos, target_pos):
    piece = self.get_piece(start_pos)
    self.set_piece(piece,target_pos)
  
  def get_chessboard(self):
    if not self.chessboard:
      self.chessboard = newchessboard(str(get_chessboard()))
      self.chessboard.is_white=get_chessboard().is_white
    return self.chessboard
  
  def get_piece(self,pos):
    return self.get_chessboard().get_piece(pos)
  
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
    self.get_chessboard().set_piece(piece,target_pos)
    return self
  
  def is_safe_position_for_king(self):
    '''
    Prüft, ob der eigene König durch den geplanten Zug in Bedrängnis gerät
    '''  
    return self.chessboard().get_king_of_moving_player().is_safe_position()

class Chessboard():
  '''
  Container für Spielfeldbelegungen
  '''
  has_finnished = False         # Für die Abbruchbedingung
  is_white      = True          # True, wenn weiß am Zug ist
  history       =[]             # Um sich die Spielzüge zu merken
  positions     =[]             # Spielfeld mit Belegungen
  white_king    = None
  black_king    = None
  white_rooks   = []
  black_rooks   = []
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
    # Positionen der Türme merken für eventuelle Rochaden
    rooks = filter(lambda p: isinstance(p,Rook),self.positions)
    for r in rooks:
      if r.is_white:
        self.white_rooks.append(r)
      else:
        self.black_rooks.append(r)
    # Positionen der Könige merken um Schach feststellen zu können
    kings = filter(lambda p: isinstance(p,King),self.positions)
    for k in kings:
      if k.is_white:
        self.white_king = k
      else:
        self.black_king = k
    
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
    pos. Can also perform a castling
    '''
    start_pos = piece.get_position()
    self.positions[pos] = piece
    if start_pos != pos:
      self.positions[start_pos] = ''
      piece.set_position(pos)
    # Wenn es eine Rochade sein soll
    if isinstance(piece,King):
      if pos-start_pos == 2:
        self.set_piece(self.get_piece(pos + 1),start_pos+1)
      if pos-start_pos == -2:
        self.set_piece(self.get_piece(pos - 2),start_pos-1)
    
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
    # Wenn pawn gerade erst um zwei Felder gezogen wurde und tatsächlich ein Bauer
    # ist
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
    for i in range(8):
      str_rank=str(8-i)
      pos_list = rank_list[7-i].split(',')
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
    
    
#################################################################
# Main functions
#################################################################  
def start():
  '''
  Main Loop
  '''
  while not get_chessboard().has_finnished:
    get_interface().display_game(str(get_chessboard()))
    get_interface().display_msg( MSG_ROUND % get_chessboard().get_color() )
    perform_move()
  get_interface().display_msg( MSG_WINNER % get_chessboard().get_king_of_opponent().get_color() )

def perform_move():
  '''
  Performs a move
  '''
  is_valid_move=False
  while not is_valid_move:
    # Zunächst prüfen, ob der ziehende Spieler im Schach steht
    if get_chessboard().is_check_given():
      get_interface().display_msg( MSG_CHECK_GIVEN )
    move = get_interface().get_move()
    is_valid_move = get_chessboard().move_piece(move)
    if get_chessboard().has_finnished:  # Will occur when a player is given chess mate
      break
    if not is_valid_move: 
      get_interface().display_msg( MSG_INVALID_MOVE )
      continue 
  # Switch from white to black or vice versa to indicate the
  # currently moving player
  get_chessboard().append_history(move)
  get_chessboard().switch_color()
    
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

def newchessboard(positions=None):
  if isinstance(positions,str):
    positions=positions.splitlines()
  return Chessboard(positions)

def get_chessboard(positions=None):
  '''
  Das Spielbrett einschließlich der Figuren.
  Wird beim ersten Aufruf initialisiert. Bei
  danach folgenden Aufrufen wird die Variable
  positions nicht mehr verarbeitet. 
  '''
  if not CHESSBOARD:
    log.debug('Instantiating chessboard')
    globals()['CHESSBOARD'] = newchessboard(positions)
  return CHESSBOARD
  
def get_interface():
  '''
  Die Benutzerschnittstelle
  '''
  if not globals()['INTERFACE']:
    globals()['INTERFACE'] = IFChessboard()
  return INTERFACE

if __name__ == "__main__":
  start()
