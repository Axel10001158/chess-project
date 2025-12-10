import chess
import chess.pgn
import pickle
import logging

logging.basicConfig(level=logging.INFO)

MAX_GAMES = 20000  
book = {}
count = 0

print("Loading games and building opening book...")

with open("games/all_2016.pgn", "r", encoding="utf-8") as pgn:
    while count < MAX_GAMES:
        game = chess.pgn.read_game(pgn)
        if not game:
            break

        board = chess.Board()
        node = game

        # only first 10 plies (5 moves each side)
        depth = 0

        while not node.is_end() and depth < 10:
            next_node = node.variations[0]
            move = next_node.move

            fen = board.fen()
            san = board.san(move)

            if fen not in book:
                book[fen] = {}

            book[fen][san] = book[fen].get(san, 0) + 1

            board.push(move)
            node = next_node
            depth += 1

        count += 1
        if count % 1000 == 0:
            print(f"{count} games processed...")

print("Saving opening book...")
with open("opening_book.pkl", "wb") as f:
    pickle.dump(book, f)

print("✅ Opening book created with", len(book), "positions!")
