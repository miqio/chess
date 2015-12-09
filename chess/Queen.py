from Piece import Piece

class Queen(Piece):

  directions = (-11,-10,-9,-1,1,9,10,11)

  def __str__(self):
    if self.is_white:
      return 'D'
    else:
      return 'd'
    

