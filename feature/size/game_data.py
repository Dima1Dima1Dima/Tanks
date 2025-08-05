import json

DATA_FILE = "game_data.json"

# Функции для загрузки и сохранения данных
def load_game_data():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {
            'total_rounds': 0,
            'score_tank1': 0,
            'score_tank2': 0,
            'coins_1': 0,
            'coins_2': 0,
            'poins_1': 0,
            'poins_2': 0,
            'win_1': 0,
            'win_2': 0,
            'por_1': 0,
            'por_2': 0,
            'shot_1_shot': 0,
            'shot_2_shot': 0,
            'struck_1_1': 0,
            'struck_2_2': 0,
            'current_volume': 0.5,  # Значение громкости по умолчанию
            'is_sound_on': True,     # Звук включен по умолчанию
            'button_sound': 0.5,  # Значение громкости по умолчанию
            'is_button_on': True  # Звук включен по умолчанию
        }

def save_game_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)