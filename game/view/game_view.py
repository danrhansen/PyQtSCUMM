import os
from PyQt6.QtCore import pyqtProperty, pyqtSignal, QSize, Qt, QPointF
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QScrollArea, QLabel, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsTextItem
from PyQt6.QtGui import QPixmap, QIcon, QColor, QCursor, QFont
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtCore import QUrl

from .game_view_helpers import InventoryLabel, Hotspot, Prop

### Provides the main view component for the UI ###
class GameView(QMainWindow):  

    # Custom signals to streamline controller mappings
    verb_button_clicked = pyqtSignal(str) 
    inventory_label_clicked = pyqtSignal(str)
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
        self.setWindowTitle("PyQtSCUMM - My Crappy Adventure Game Interface")
        self.setFixedSize(QSize(680,440))

        # Create media player for music
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(50)

        # Setup screen layout
        self.setup_scene()
        self.setup_widgets()
        screen_layout = self.setup_layout()
        
        # Set the main widget and show the window
        widget = QWidget()
        widget.setLayout(screen_layout)
        self.setCentralWidget(widget)
        self.show()

        # TODO: should be part of the scene load
        self.play_audio("scumm_bar.mp3")


    # Update UI components based on game tick
    def update_view(self):
        
        # Set cursor to crosshair if over the view. Probably could have been done with hover event but proves game tick is working...
        # Also some special handling for Walk To
        if self.is_cursor_over_view():
            self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
            # TODO
            #if(self.info_label.text() == ""):
                #self.info_label.setText("Walk to")
        else:
            self.unsetCursor()
            # TODO
            #if(self.info_label.text() == "Walk to"):
                #self.info_label.setText("")


    # Setup the scene
    # TODO: load and refresh from game state
    def setup_scene(self):

        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(QColor("black"))
        self.view = QGraphicsView(self.scene)

        # Load example background image
        background_image = QPixmap(self.get_file_path("resources", "scenes", "scummbar_ega.png"))
        background_item = QGraphicsPixmapItem(background_image)
        self.scene.addItem(background_item)

        # TODO: Replace this basic say text solution  - not working
        self.say_text = QGraphicsTextItem()
        self.say_text.setPos(QPointF(40,100))
        self.say_text.setDefaultTextColor(QColor("white")) 
        self.say_text.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.scene.addItem(self.say_text)

        # Create bucket prop
        bucket_image = QPixmap(self.get_file_path("resources", "inventory", "bucket.png"))
        self.bucket_prop = Prop("bucket", bucket_image)
        self.bucket_prop.setPos(225, 250)
        self.bucket_prop.clicked.connect(self.handle_prop_click)
        self.bucket_prop.entered.connect(self.handle_prop_enter)
        self.bucket_prop.left.connect(self.handle_prop_leave)
        self.scene.addItem(self.bucket_prop)

        # Create pirate1 hotspot
        self.pirate1_hotspot = Hotspot("Pirate", 160, 160, 80, 80)
        self.pirate1_hotspot.clicked.connect(self.handle_hotspot_click)
        self.pirate1_hotspot.entered.connect(self.handle_hotspot_enter)
        self.pirate1_hotspot.left.connect(self.handle_hotspot_leave)
        self.scene.addItem(self.pirate1_hotspot)

    # Setup standalone widgets. Excludes verbs and inventory which are handled in setup_layout. 
    def setup_widgets(self):

        # Info
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("background-color: black; color: blue; font-size: 16px;")
        self.info_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))

        # Toolbar
        self.options_button = QPushButton("Options")
        self.options_button.setIcon(QIcon(self.get_file_path("resources", "gui", "options_button.png")))
        self.options_button.setEnabled(False)
        self.save_button = QPushButton("Save")
        self.save_button.setIcon(QIcon(self.get_file_path("resources", "gui", "save_button.png")))
        self.save_button.setEnabled(False)
        self.quit_button = QPushButton("Quit")
        self.quit_button.setIcon(QIcon(self.get_file_path("resources", "gui", "quit_button.png")))

        # Inventory Scroll
        self.inv_scrollup_button = QPushButton('Up')
        self.inv_scrollup_button.setIcon(QIcon(self.get_file_path("resources", "gui", "inv_scrollup_button.png")))
        self.inv_scrollup_button.setDisabled(True)
        self.inv_scrolldwn_button = QPushButton('Down')
        self.inv_scrolldwn_button.setIcon(QIcon(self.get_file_path("resources", "gui", "inv_scrolldwn_button.png")))
        self.inv_scrolldwn_button.setDisabled(True)

    # Setup screen layout and return for central widget. Includes verbs and inventory setup.
    def setup_layout(self):
    
        # Define 9 verbs for SCUMM style point-and-click interactions 
        verbs = ['Give', 'Pick up', 'Use', 'Open', 'Look at', 'Push', 'Close', 'Talk to', 'Pull']
        
        # Interate verbs to place within 3x3 grid
        verb_layout = QGridLayout()
        row, col = 0, 0
        for verb in verbs:
            verb_button = QPushButton(verb)
            verb_button.clicked.connect(self.handle_verb_button_click) # signal handled in view to streamline with controller
            verb_layout.addWidget(verb_button, row, col)
            col += 1
            if col > 2:
                row += 1
                col = 0
          
        # Place toolbar buttons vertically
        toolbar_layout = QVBoxLayout()
        toolbar_layout.addWidget(self.options_button)
        toolbar_layout.addWidget(self.save_button)
        toolbar_layout.addWidget(self.quit_button)

        # Same with inventory scrollers
        inv_scroll_layout = QVBoxLayout()
        inv_scroll_layout.addWidget(self.inv_scrollup_button)
        inv_scroll_layout.addWidget(self.inv_scrolldwn_button)

        # TODO: Scrollable inventory within 4x2 grid
        self.inventory_layout = QGridLayout()

        # Create a scroll area for the inventory
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allow the content to be resized
        self.scroll_area.setFixedSize(160, 90)
        self.scroll_content = QWidget()
        self.scroll_content.setLayout(self.inventory_layout)
        self.scroll_area.setWidget(self.scroll_content)
       
        # Place gui layouts together horizontally
        gui_layout = QHBoxLayout()
        gui_layout.addLayout(verb_layout)
        gui_layout.addLayout(toolbar_layout)
        gui_layout.addLayout(inv_scroll_layout)
        gui_layout.addWidget(self.scroll_area)

        # Place view (scene), info label, and guid layout vertically
        screen_layout = QVBoxLayout()
        screen_layout.addWidget(self.view)
        screen_layout.addWidget(self.info_label)
        screen_layout.addLayout(gui_layout)
       
        return screen_layout

    def is_cursor_over_view(self):
        view_rect = self.view.geometry()
        cursor_pos = self.mapFromGlobal(QCursor.pos())

        return view_rect.contains(cursor_pos)

    # Functions to handle view changes based on events passed from controller

    def display_info(self, info):
        self.info_label.setText(info)

    def display_inventory(self, inventory_list): # TODO not working
        
        # Clear the existing items from the layout
        #while self.inventory_layout.count() > 0:
        #    item = self.inventory_layout.itemAt(0)
        #    self.inventory_layout.removeItem(item)
        #    item.widget().deleteLater()

        row, col = 0, 0
        for item in inventory_list:
            inventory_label = InventoryLabel(item, self.get_file_path("resources", "inventory", f"{item}.png"))
            inventory_label.clicked.connect(self.handle_inventory_label_click)
            self.inventory_layout.addWidget(inventory_label, row, col)
            col += 1
            if col > 3:
                col = 0 
                row += 1

    def display_character_say(self, text):
        self.say_text.setPlainText(text)

    # Functions to handle user interactions and pass them to the controller

    def handle_verb_button_click(self):
        sender = self.sender()
        verb = sender.text()
        self.verb_button_clicked.emit(verb)

    def handle_prop_click(self):
        sender = self.sender()
        prop_name = sender.name
        self.prop_clicked.emit(prop_name)

        # TODO: Not where or how I  want to handle, but for now
      
        if prop_name == "bucket":
            self.scene.removeItem(sender)
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

    def handle_inventory_label_click(self):
        sender = self.sender()
        inventory_name = sender.text()
        self.inventory_label_clicked.emit(inventory_name)

    
    # Audio functions

    def play_audio(self, file_name):

        file_path = self.get_file_path("resources", "audio", file_name)
        # Load audio file
        audio_file = QUrl.fromLocalFile(file_path)

        self.player.setSource(audio_file)
        self.player.play()

    def pause_audio(self):
        self.player.pause()


    # Misc

    def get_file_path(self, *path_segments):
        root_directory = os.path.dirname(os.path.abspath(__file__))
        root_directory = os.path.abspath(os.path.join(root_directory, "..", ".."))  # Move two levels up
        image_path = os.path.join(root_directory, *path_segments)
        return image_path

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()