
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from game.model import GameModel
from game.view import GameView
from game.controller import GameController

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game_logic_model = GameModel()
    game_view = GameView()
    game_view.showFullScreen()
    game_controller = GameController(game_logic_model, game_view)
    game_controller.start_game_loop()  # Start the game loop
    sys.exit(app.exec())