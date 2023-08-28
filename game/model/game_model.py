from PyQt6.QtCore import QObject, pyqtSignal

### Provides the primary model for game state and logic ###
class GameModel(QObject):
    info_updated = pyqtSignal(str)
    inventory_updated = pyqtSignal(list)
    character_say = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._active_verb = ""
        self._active_mouseover = ""
        self._inventory_list = []
        self._got_bucket = False
        self._talked_to_pirate = False

    @property
    def active_verb(self):
        return self._active_verb

    @active_verb.setter
    def active_verb(self, verb):
        if self._active_verb != verb:
            self._active_verb = verb
            self.update_info()

    @property
    def active_mouseover(self):
        return self._active_mouseover

    @active_mouseover.setter
    def active_mouseover(self, mouseover):
        if self._active_mouseover != mouseover:
            self._active_mouseover = mouseover
            self.update_info()

    def update_info(self):
        info = f"{self.active_verb} {self.active_mouseover}"
        self.info_updated.emit(info)

    def reset_info(self):
        self._active_verb = ""
        self._active_mouseover = ""
        self.update_info()

    def add_inventory(self, name):
        self._inventory_list.append(name)
        self.inventory_updated.emit(self._inventory_list)

    def say_character(self, text):
        self.character_say.emit(text)

    def update_model(self, elapsed_time):
        pass

    def handle_inventory_click(self, inventory_name):
        if(inventory_name == "bucket"):
            self.say_character("It's a nice bucket.")

    def handle_prop_click(self, prop_name):
        print("reached 2")
        if(prop_name == "bucket"):
            if self.active_verb == "Pick up":
                self.add_inventory(prop_name)
                self.say_character("Yeah! A bucket!")
                self._got_bucket = True
            elif self.active_verb == "Look at":
                self.say_character("I want it!")
            else:
                self.say_character("That doesn't seem to work.")
        self.reset_info()

    def handle_prop_enter(self, prop_name):
        self.active_mouseover = prop_name
        self.update_info()

    def handle_prop_leave(self, prop_name):
        self.active_mouseover = ""
        self.update_info()

    def handle_hotspot_click(self, hotspot_name):
        if hotspot_name == "Pirate":
            if self.active_verb == "Talk to":
                self.say_character("I'm Guybrush Threpwood, mighty pirate!")
                self._talked_to_pirate = True
            elif self.active_verb == "Look at":
                self.say_character("He's mighty. But not as mighty as me.")
            else:
                self.say_character("He doesn't seem interested.")
        self.reset_info()

    def handle_hotspot_enter(self, hotspot_name):
        self.active_mouseover = hotspot_name
        self.update_info()

    def handle_hotspot_leave(self, hotspot_name):
        self.active_mouseover = ""
        self.update_info()