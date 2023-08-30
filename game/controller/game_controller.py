import sys
from PyQt6.QtCore import QObject, QTimer

### Provides the primary controller that interacts with the GameModel and GameView ###
class GameController(QObject):

    def __init__(self, game_model, game_view):
        super().__init__()
        self._game_model = game_model
        self._game_view = game_view
        self.init_model()
        self.init_view()
        self.setup_game_loop()

    def init_model(self):

        self._game_model.info_updated.connect(self.handle_info_updated)
        self._game_model.inventory_updated.connect(self.handle_inventory_updated)
        self._game_model.character_say.connect(self.handle_character_say)

    # Connect UI signals to controller methods
    def init_view(self):
     
        self._game_view.verb_button_clicked.connect(self.handle_verb_button_click)
        self._game_view.quit_button.clicked.connect(self.handle_quit_button_click)
        self._game_view.inv_scroll_area.inventory_label_clicked.connect(self.handle_inventory_label_click)
        self._game_view.prop_clicked.connect(self.handle_prop_click)
        self._game_view.prop_entered.connect(self.handle_prop_enter)
        self._game_view.prop_left.connect(self.handle_prop_leave)
        self._game_view.hotspot_clicked.connect(self.handle_hotspot_click)
        self._game_view.hotspot_entered.connect(self.handle_hotspot_enter)
        self._game_view.hotspot_left.connect(self.handle_hotspot_leave)
        # TODO - a lot more to fully enable scene and UI

    def setup_game_loop(self):
        self._timer = QTimer()
        self._timer.timeout.connect(self.game_loop_tick)

        # Define the tick rate in milliseconds
        self._tick_rate = 100  # Adjust as needed

    def start_game_loop(self):
        self._timer.start(self._tick_rate)

    def game_loop_tick(self):
        # Update game based on the elapsed time
        self._game_model.update_model(self._tick_rate / 1000.0)  # Convert to seconds

        # Update UI based on game state changes
        self._game_view.update_view()

    # Update the info label providing active verb + mouseover (prop, hotspot, etc.)
    def handle_info_updated(self, info):
        self._game_view.display_info(info)

    # Update the inventory panel with current inventory items list
    def handle_inventory_updated(self, inventory_list):
        self._game_view.display_inventory(inventory_list)

    # Update the character say text in the scene
    def handle_character_say(self, text):
        self._game_view.display_character_say(text)

    # Update the active verb. Subsequent info change event takes care of view update to streamline changes.
    def handle_verb_button_click(self, verb):
        self._game_model.active_verb = verb
  
    # Exits at system level when quit button clicked. TODO: more specific handeling of save warning, etc.
    def handle_quit_button_click(self):
        sys.exit()

    # Handle click on inventory  
    def handle_inventory_label_click(self, inventory_name):
        self._game_model.handle_inventory_click(inventory_name)

    # Prop interaction handling

    def handle_prop_click(self, prop_name):
        self._game_model.handle_prop_click(prop_name)

    def handle_prop_enter(self, prop_name):
        self._game_model.handle_prop_enter(prop_name)
   
    def handle_prop_leave(self, prop_name):
        self._game_model.handle_prop_leave(prop_name)


    # Hotspot interaction handling
   
    def handle_hotspot_click(self, hotspot_name):
        self._game_model.handle_hotspot_click(hotspot_name)

    def handle_hotspot_enter(self, hotspot_name):
        self._game_model.handle_hotspot_enter(hotspot_name)

    def handle_hotspot_leave(self, hotspot_name):
        self._game_model.handle_hotspot_leave(hotspot_name)
