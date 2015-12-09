from Piece import Piece

class Bishop(Piece):

  directions = (-11,-9,9,11)

  def __str__(self):
    if self.is_white:
      return 'L'
    else:
      return 'l'
    

