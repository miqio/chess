#!/usr/bin/python
# -*- coding: utf-8 -*-
import chess.manager, chess.pieces, chess.board
import unittest

class TestChessPieces(unittest.TestCase):

    def test_pawn(self):
        cb = chess.manager.get_chessboard()
        p = cb.get_piece(23)
        self.assertEqual(p.get_admissible_positions(), [33,43],"Bauer kann auf unerlaubte Positionen")
        piece = cb.get_piece(71)
        cb.set_piece(piece,32)
        self.assertEqual(p.get_admissible_positions(), [32,33,43],"Bauer kann auf %s" % p.get_admissible_positions())
        self.assertTrue(piece.is_allowed_cell(21,-11),"Bauer kann auf 21, wird aber nicht erkannt")
        self.assertTrue(piece.is_allowed_cell(23,-9),"Bauer kann auf 23, wird aber nicht erkannt")
        self.assertFalse(piece.is_allowed_cell(22,-10),"Bauer kann angeblich auf 22, das Feld ist aber besetzt")
        self.assertEqual(piece.get_admissible_positions(), [23,21],"%s kann auf %s" % (str(piece),str(piece.get_admissible_positions())))
        self.assertFalse(piece.is_safe_position(), "Bauer ist aber bedroht")
        cb.set_piece(piece,42)
        pawn=cb.get_piece(23)
        cb.set_piece(pawn,43)
        cb.append_history((23,43))
        self.assertTrue(piece.is_allowed_cell(33,-9),"Bauer kann angeblich nicht auf 33, en passant ist aber ein Bauer zu schlagen")
        self.assertFalse(piece.is_allowed_cell(31,-11),"Bauer kann angeblich auf 33, en passant ist aber kein Bauer zu schlagen")
        
    def test_chessboard(self):
        cb=chess.manager.get_chessboard()
        piece = cb.get_piece(71)
        cb.set_piece(piece,42)
        pawn=cb.get_piece(23)
        cb.set_piece(pawn,43)
        cb.append_history((23,43))
        self.assertTrue(cb.move_piece((42,33)),"Bauer kann en passant schlagen, wird aber nicht erkannt")
        self.assertFalse(cb.move_piece((42,31)),"Bauer kann nicht auf 31, weil dort nichts zu sachlagen ist")
        self.assertFalse(cb.get_piece(43),"Der BAuer auf 42 hätte geschlagen werden müssen, ist aber immer noch da")


if __name__ == '__main__':
    unittest.main()


    

