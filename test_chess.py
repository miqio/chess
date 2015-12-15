#!/usr/bin/python
# -*- coding: utf-8 -*-
import chess
import unittest

class TestChessPieces(unittest.TestCase):

    def test_chessboard(self):
        cb = chess.get_chessboard()
        self.assertFalse(cb.can_be_hit_en_passant(cb.get_piece(31)), "Auf 31 ist nichts zu schlagen")        

    def test_pawn(self):
        cb = chess.get_chessboard()
        p = cb.get_piece(23)
        self.assertEqual(p.get_admissible_positions(), [33,43],"Bauer kann auf unerlaubte Positionen")
        piece = cb.get_piece(71)
        cb.set_piece(piece,32)
        self.assertEqual(p.get_admissible_positions(), [32,33,43],"Bauer kann auf %s" % p.get_admissible_positions())
        self.assertTrue(piece.is_allowed_cell(21,-11),"Bauer kann auf 21, wird aber nicht erkannt")
        self.assertTrue(piece.is_allowed_cell(23,-9),"Bauer kann auf 23, wird aber nicht erkannt")
        self.assertFalse(piece.is_allowed_cell(22,-10),"Bauer kann angeblich auf 22, das Feld ist aber besetzt")
        self.assertFalse(piece.is_allowed_cell(31,-1),"Bauer kann angeblich auf 31, en passant ist aber kein Bauer zu schlagen")
        self.assertFalse(piece.is_allowed_cell(33,+1),"Bauer kann angeblich auf 33, en passant ist aber kein Bauer zu schlagen")
        self.assertEqual(piece.get_admissible_positions(), [23,21],"%s kann auf %s" % (str(piece),str(piece.get_admissible_positions())))
        self.assertFalse(piece.is_safe_position(), "Bauer ist aber bedroht")


if __name__ == '__main__':
    unittest.main()


    

