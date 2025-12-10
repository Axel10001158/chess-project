import os

INPUT_FOLDER = "games"
OUTPUT_FILE = "games/all_2016.pgn"

with open(OUTPUT_FILE, "w", encoding="utf-8") as outfile:
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".pgn"):
            print(f"Merging: {filename}")
            with open(os.path.join(INPUT_FOLDER, filename), "r", encoding="utf-8") as infile:
                outfile.write(infile.read())

print("✅ All PGN files merged into:", OUTPUT_FILE)
