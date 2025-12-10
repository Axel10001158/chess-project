import chess.pgn
import logging

logger = logging.getLogger(__name__)

def load_games_from_pgn(file_path: str, max_games: int = 1000):
    """
    Load up to max_games from a regular .pgn file.
    """
    logger.info(f"Loading PGN games from {file_path}")

    games = []
    count = 0

    with open(file_path, "r", encoding="utf-8") as pgn_file:
        while count < max_games:
            game = chess.pgn.read_game(pgn_file)
            if game is None:
                break
            games.append(game)
            count += 1
            if count % 100 == 0:
                logger.info(f"Loaded {count} games...")

    logger.info(f"✅ Finished loading {len(games)} PGN games")
    return games
