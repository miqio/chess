#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging  # Um Meldungen auszugeben
import chess.manager, chess.pieces, chess.board
import unittest

logging.basicConfig(level=logging.DEBUG) # Setze auf logging.DEBUG, damit Meldungen ausgegeben werden
log = logging.getLogger(__name__)

class TestChessPieces(unittest.TestCase):

    def setUp(self):
        self.cb = chess.manager.get_chessboard()
        self.white_pawn = self.cb.get_piece(23)
        self.black_pawn = self.cb.get_piece(71)

    def test_pawn(self):
        self.assertEqual(self.white_pawn.get_admissible_positions(), [33,43],
                    "Bauer kann auf unerlaubte Positionen")
        self.cb.set_piece(self.black_pawn,32)
        self.assertEqual(self.white_pawn.get_admissible_positions(), [32,33,43],
                    "Bauer kann auf %s" % self.black_pawn.get_admissible_positions())
        self.assertTrue(self.black_pawn.is_allowed_cell(21,-11),
                    "Bauer kann auf 21, wird aber nicht erkannt")
        self.assertTrue(self.black_pawn.is_allowed_cell(23,-9),
                    "Bauer kann auf 23, wird aber nicht erkannt")
        self.assertFalse(self.black_pawn.is_allowed_cell(22,-10),
                    "Bauer kann angeblich auf 22, das Feld ist aber besetzt")
        self.assertEqual(self.black_pawn.get_admissible_positions(), [23,21],
                    "Der schwarze bauer kann auf %s" % self.black_pawn.get_admissible_positions())
        self.assertFalse(self.black_pawn.is_safe_position(), 
                    "Bauer auf 32 wird angegriffen, wird aber nicht erkannt")
        self.cb.set_piece(self.black_pawn,42)
        self.cb.set_piece(self.white_pawn,43)
        self.cb.append_history((23,43))
        self.assertTrue(self.white_pawn.can_be_hit_en_passant(),
                    "Der Bauer auf 43 kann en passant geschlagen werden, wird aber nicht erkannt")
        self.assertTrue(self.black_pawn.is_allowed_cell(33,-9),
                    "Bauer kann angeblich nicht auf 33, en passant ist aber ein Bauer zu schlagen")
        self.assertFalse(self.black_pawn.is_allowed_cell(31,-11),
                    "Bauer kann angeblich auf 33, en passant ist aber kein Bauer zu schlagen")
        self.assertEqual(self.black_pawn.get_admissible_positions(), [33,32],
                    "Der schwarze bauer kann auf %s" % self.black_pawn.get_admissible_positions())
        self.assertTrue(self.black_pawn.is_valid_move(33),
                    "Der schwarze Bauer kann auf 32, is_valid_move ist aber False")
        self.cb.switch_color()
        self.assertTrue(self.cb.is_valid_move((42,33)),
                    "Der schwarze Bauer kann auf 32, is_valid_move ist aber False")
        self.assertTrue(self.cb.move_piece((42,33)),
                    "der schwarze Bauer kann en passant schlagen, move_piece gibt aber False zurück")
        self.assertFalse(self.cb.move_piece((42,31)),
                    "Bauer kann nicht auf 31, weil dort nichts zu schlagen ist")
        self.assertFalse(self.cb.get_piece(43),
                    "Der Bauer auf 42 hätte geschlagen werden müssen, ist aber immer noch da")
        
    def test_castling(self):
        chess.manager.discard_chessboard()
        cb = chess.manager.get_chessboard('')
        cb.white_king=chess.manager.newinstance('K',15)
        cb.black_king=chess.manager.newinstance('k',85)
        wr1=chess.manager.newinstance('T',11)
        wr2=chess.manager.newinstance('T',18)
        cb.white_rooks.append(wr1)
        cb.white_rooks.append(wr2)
        br=chess.manager.newinstance('t',86)
        cb.black_rooks.append(br)
        cb.black_king=chess.manager.newinstance('k',85)
        cb.black_king=chess.manager.newinstance('k',85)
        chess.manager.get_positions()[11] = wr1
        chess.manager.get_positions()[15] = cb.white_king
        chess.manager.get_positions()[18] = wr2
        chess.manager.get_positions()[85] = cb.black_king
        chess.manager.get_positions()[86] = br
        self.assertFalse(cb.move_piece((15,17)),
                    "Die kleine Rochade geht nicht, aber Zug wird ausgeführt")
        self.assertTrue(cb.get_piece(18),
                    "Der Turm sollte noch da stehen")
        ap = cb.get_king_of_moving_player().get_admissible_positions()
        self.assertEqual(ap,[1],
                    "Der König erreicht %s" % ap)
        self.assertTrue(cb.move_piece((15,13)),
                    "Die große Rochade sollte gehen, aber Zug wird nicht ausgeführt")
        self.assertTrue(isinstance(cb.get_piece(13),chess.pieces.King)\
                    and isinstance(cb.get_piece(14),chess.pieces.Rook),
                    "Die große Rochade sollte durchgeführt sein, aber die Figuren stehen falsch")
        
        
if __name__ == '__main__':
    unittest.main()


    

