"""
Smart Homemade Chess Bot
Uses Lichess opening data + simple alpha-beta search (depth 3)
"""

import chess
from chess.engine import PlayResult, Limit
import random
from lib.engine_wrapper import MinimalEngine
from lib.lichess_types import MOVE
import logging
import pickle

logger = logging.getLogger(__name__)

# ====== OPENING BOOK ======
try:
    with open("opening_book.pkl", "rb") as f:
        OPENING_BOOK = pickle.load(f)
    logger.info(f"✅ Opening book loaded with {len(OPENING_BOOK)} positions")
except Exception as e:
    logger.warning(f"No opening book found: {e}")
    OPENING_BOOK = {}

# ====== PIECE VALUES ======
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

CENTER_SQUARES = {chess.D4, chess.D5, chess.E4, chess.E5}

# ====== ENGINE ======

class ExampleEngine(MinimalEngine):
    pass


class GamesEngine(ExampleEngine):
    """Engine that plays using opening book + alpha-beta search."""

    def search(self,
               board: chess.Board,
               time_limit: Limit,
               ponder: bool,
               draw_offered: bool,
               root_moves: MOVE) -> PlayResult:

        fen = board.fen()

        # 1️⃣ Opening Book Move
        if fen in OPENING_BOOK:
            san = max(OPENING_BOOK[fen], key=OPENING_BOOK[fen].get)
            move = board.parse_san(san)
            logger.info(f"Opening book move: {san}")
            return PlayResult(move, None)

        # 2️⃣ Avoid checkmate immediately (defense)
        for move in board.legal_moves:
            board.push(move)
            if board.is_checkmate():
                board.pop()
                logger.info("Avoiding checkmate with defensive move")
                return PlayResult(move, None)
            board.pop()

        # 3️⃣ Run Alpha-Beta Search
        best_score, best_move = self.alphabeta(board, 3, -10**9, 10**9)
        if not best_move:
            best_move = random.choice(list(board.legal_moves))
        logger.info(f"Best move found: {best_move} (score {best_score})")
        return PlayResult(best_move, None)

    # ====== CORE ALGORITHMS ======

    def evaluate(self, board: chess.Board) -> int:
        """Evaluate board by material + mobility + center control + king safety."""
        score = 0

        for sq, piece in board.piece_map().items():
            value = PIECE_VALUES.get(piece.piece_type, 0)
            score += value if piece.color else -value

            # small bonus for controlling the center
            if sq in CENTER_SQUARES:
                score += 15 if piece.color else -15

        # Mobility
        my_moves = len(list(board.legal_moves))
        board.push(chess.Move.null())
        opp_moves = len(list(board.legal_moves))
        board.pop()
        score += (my_moves - opp_moves) * 2

        # Penalize if in check
        if board.is_check():
            score -= 30

        return score if board.turn else -score

    def alphabeta(self, board: chess.Board, depth: int, alpha: int, beta: int):
        """Mini alpha-beta pruning (depth 3)"""
        if depth == 0 or board.is_game_over():
            return self.evaluate(board), None

        best_move = None
        if board.turn:  # Maximizing player (White)
            value = -10**9
            for move in self.sorted_moves(board):
                board.push(move)
                score, _ = self.alphabeta(board, depth - 1, alpha, beta)
                board.pop()
                if score > value:
                    value, best_move = score, move
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, best_move
        else:  # Minimizing player (Black)
            value = 10**9
            for move in self.sorted_moves(board):
                board.push(move)
                score, _ = self.alphabeta(board, depth - 1, alpha, beta)
                board.pop()
                if score < value:
                    value, best_move = score, move
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, best_move

    def sorted_moves(self, board):
        """Order moves (captures first)."""
        captures, quiets = [], []
        for m in board.legal_moves:
            if board.is_capture(m):
                captures.append(m)
            else:
                quiets.append(m)
        return captures + quiets
