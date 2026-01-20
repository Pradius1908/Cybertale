import json
import os
from player import Player
from weapon import Weapon

SAVE_FILE = "savegame.json"

class SaveManager:
    @staticmethod
    def save_game(player, current_level_index):
        data = {
            "player": player.to_dict(),
            "level_index": current_level_index
        }
        try:
            with open(SAVE_FILE, "w") as f:
                json.dump(data, f, indent=4)
            print("Game Saved.")
        except Exception as e:
            print(f"Error saving game: {e}")

    @staticmethod
    def load_game():
        if not os.path.exists(SAVE_FILE):
            return None
        
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
