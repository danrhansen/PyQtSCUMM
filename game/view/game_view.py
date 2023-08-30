from PyQt6.QtCore import pyqtProperty, pyqtSignal, Qt, QPointF
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGraphicsView, QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap, QCursor 
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtCore import QUrl

from .game_view_helpers import GameScene, SayTextItem, InfoLabel, StyledButton, InventoryScrollArea, Hotspot, Prop
from .game_view_utils import get_file_path

class GameView(QMainWindow):  

    # Custom signals to streamline controller mappings
    verb_button_clicked = pyqtSignal(str)
    prop_clicked = pyqtSignal(str)
    prop_entered = pyqtSignal(str) 
    prop_left = pyqtSignal(str) 
    hotspot_entered = pyqtSignal(str) 
    hotspot_left = pyqtSignal(str) 
    hotspot_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_view()

    def init_view(self):
        # Initialize the main UI elements and layouts
        self.setWindowTitle("PyQtSCUMM: The Secret of Monkey Island")
        self.setStyleSheet("background-color: black;")

        # Create media player for music
        self._player = QMediaPlayer()
        self._audio_output = QAudioOutput()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(50)

        # Setup screen layout
        self.setup_scene()
        self.setup_widgets()
        screen_layout = self.setup_layout()
        
        # Set the main widget and show the window
        widget = QWidget()
        widget.setLayout(screen_layout)
        self.setCentralWidget(widget)
       
        # TODO: should be part of the scene load
        self.play_audio("scumm_bar.mp3")


    # Update UI components based on game tick
    def update_view(self):
        
        # Set cursor to crosshair if over the view. 
        # TODO: Probably could have been done with hover event but proves game tick is working...
        # TODO: Event trigger to controller to update active verb. Other changes needed to support Walk.
        if self.is_cursor_over_view():
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
    
        else:
            self.unsetCursor()

    # Setup the scene
    # TODO: load and refresh from game state
    def setup_scene(self):

        self._scene = GameScene()

        # Load example background image
        background_image = QPixmap(get_file_path("resources", "scenes", "scummbar_ega.png"))
        background_item = QGraphicsPixmapItem(background_image)
        self._scene.addItem(background_item)

        # TODO: Replace this basic say text solution
        self._say_text = SayTextItem()
        self._say_text.setPos(QPointF(20,50))
        self._scene.addItem(self._say_text)

        # Create bucket prop
        bucket_image = QPixmap(get_file_path("resources", "inventory", "bucket.png"))
        self._bucket_prop = Prop("bucket", bucket_image)
        self._bucket_prop.setPos(110, 125)
        self._bucket_prop.clicked.connect(self.handle_prop_click)
        self._bucket_prop.entered.connect(self.handle_prop_enter)
        self._bucket_prop.left.connect(self.handle_prop_leave)
        self._scene.addItem(self._bucket_prop)

        # Create pirate1 hotspot
        self._pirate1_hotspot = Hotspot("Pirate", 80, 80, 40, 40)
        self._pirate1_hotspot.clicked.connect(self.handle_hotspot_click)
        self._pirate1_hotspot.entered.connect(self.handle_hotspot_enter)
        self._pirate1_hotspot.left.connect(self.handle_hotspot_leave)
        self._scene.addItem(self._pirate1_hotspot)

        # Place in view
        self._view = QGraphicsView(self._scene)

        # Remove scroll bars
        self._view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._view.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._view.setContentsMargins(0,0,0,0)

    # Setup standalone widgets. Excludes verbs and inventory which are handled in setup_layout. 
    def setup_widgets(self):

        # Info
        self._info_label = InfoLabel()
        
        # Toolbar
        self._options_button = StyledButton("Options")
        self._options_button.setEnabled(False)
        self._save_button = StyledButton("Save")
        self._save_button.setEnabled(False)
        self._quit_button = StyledButton("Quit")

        # Inventory Scroll
        self._inv_scrollup_button = StyledButton('Up')
        self._inv_scrollup_button.setDisabled(True)
        self._inv_scrolldwn_button = StyledButton('Down')
 
        self._inv_scrolldwn_button.setDisabled(True)

    # Setup screen layout and return for central widget. Includes verbs and inventory setup.
    def setup_layout(self):
    
        # Define 9 verbs for SCUMM style point-and-click interactions 
        verbs = ['Give', 'Pick up', 'Use', 'Open', 'Look at', 'Push', 'Close', 'Talk to', 'Pull']
        
        # Interate verbs to place within 3x3 grid
        verb_layout = QGridLayout()
        row, col = 0, 0
        for verb in verbs:
            verb_button = StyledButton(verb)
            verb_button.clicked.connect(self.handle_verb_button_click) # signal handled in view to streamline with controller
            verb_layout.addWidget(verb_button, row, col)
            col += 1
            if col > 2:
                row += 1
                col = 0
          
        # Place toolbar buttons vertically
        toolbar_layout = QVBoxLayout()
        toolbar_layout.addWidget(self._options_button)
        toolbar_layout.addWidget(self._save_button)
        toolbar_layout.addWidget(self._quit_button)

        # Same with inventory scrollers
        inv_scroll_layout = QVBoxLayout()
        inv_scroll_layout.addWidget(self._inv_scrollup_button)
        inv_scroll_layout.addWidget(self._inv_scrolldwn_button)

        # Create a scroll area for the inventory
        self._inv_scroll_area = InventoryScrollArea()
       
        # Place gui layouts together horizontally
        gui_layout = QHBoxLayout()
        gui_layout.addLayout(verb_layout)
        gui_layout.addLayout(toolbar_layout)
        gui_layout.addLayout(inv_scroll_layout)
        gui_layout.addWidget(self._inv_scroll_area)

        # Place view (scene), info label, and guid layout vertically
        screen_layout = QVBoxLayout()
        screen_layout.addWidget(self._view)
        screen_layout.addWidget(self._info_label)
        screen_layout.addLayout(gui_layout)
       
        return screen_layout

    @pyqtProperty(str)
    def quit_button(self):
        return self._quit_button

    @pyqtProperty(str)
    def inv_scroll_area(self):
        return self._inv_scroll_area

    def is_cursor_over_view(self):
        view_rect = self._view.geometry()
        cursor_pos = self.mapFromGlobal(QCursor.pos())

        return view_rect.contains(cursor_pos)

    # Functions to handle view changes based on events passed from controller

    def display_info(self, info):
        self._info_label.setText(info)

    def display_inventory(self, inventory_list):
        self._inv_scroll_area.display_inventory(inventory_list)
                                             

    def display_character_say(self, text):
        self._say_text.setPlainText(text)

    # Functions to handle user interactions and pass them to the controller

    def handle_verb_button_click(self):
        sender = self.sender()
        verb = sender.text()
        self.verb_button_clicked.emit(verb)

    def handle_prop_click(self):
        sender = self.sender()
        prop_name = sender.name
        self.prop_clicked.emit(prop_name)

        # TODO: Not where or how I  want to handle, but for now. Bug fix needed to only remove bucket if matching verb.
        # likely have to signal back grame model to remove it.
      
        if prop_name == "bucket":
            self._scene.removeItem(sender)
            sender.deleteLater()

    def handle_prop_enter(self):
        sender = self.sender()
        prop_name = sender.name
        self.prop_entered.emit(prop_name)

    def handle_prop_leave(self):
        sender = self.sender()
        prop_name = sender.name
        self.prop_left.emit(prop_name)

    def handle_hotspot_click(self):
        sender = self.sender()
        hotspot_name = sender.name
        self.hotspot_clicked.emit(hotspot_name)

    def handle_hotspot_enter(self):
        sender = self.sender()
        hotspot_name = sender.name
        self.hotspot_entered.emit(hotspot_name)

    def handle_hotspot_leave(self):
        sender = self.sender()
        hotspot_name = sender.name
        self.hotspot_left.emit(hotspot_name)

    
    # Audio functions
    # Todo: Custom audio class to to remove setup here

    def play_audio(self, file_name):

        # Load audio file
        file_path = get_file_path("resources", "audio", file_name)
        audio_file = QUrl.fromLocalFile(file_path)

        self._player.setSource(audio_file)
        self._player.play()

    def pause_audio(self):
        self._player.pause()
