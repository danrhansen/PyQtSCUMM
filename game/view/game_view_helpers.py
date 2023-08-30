from PyQt6.QtCore import pyqtProperty, pyqtSignal, QRectF, Qt
from PyQt6.QtWidgets import QWidget, QGraphicsScene, QGraphicsTextItem, QPushButton, QScrollArea, QGridLayout, QLabel, QGraphicsObject
from PyQt6.QtGui import QPixmap, QColor, QFont

from .game_view_utils import get_file_path, calculate_scale_factor


# Constants
SCREEN_RESOLUTION_HEIGHT = 180

# Create a QFont instance with the loaded font family
scumm_text = QFont(get_file_path("resources", "fonts", "lucasarts-scumm-solid.ttf"), 24 )
scumm_gui = QFont(get_file_path("resources", "fonts", "lucasarts-scumm-menu-solid.ttf"), 24 )

### All classes supporting the GameView ###

class GameScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setBackgroundBrush(QColor("black"))
        
    def addItem(self, item):
        super().addItem(item)

        scale_factor = calculate_scale_factor()
        item.setPos(item.pos() * scale_factor)

        if not isinstance(item, QGraphicsTextItem):
            item.setScale(scale_factor)


class SayTextItem(QGraphicsTextItem):
    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)

        self.setFont(scumm_text)
        self.setDefaultTextColor(QColor("white")) 


class InfoLabel(QLabel):
    def __init__(self, text=None, parent=None):
        super().__init__(text, parent)
        
        self.setFont(scumm_gui) 
        self.setStyleSheet("background-color: black; color: teal;") # border: 2px solid white
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMargin(0)

class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setFont(scumm_gui)
        self.setStyleSheet("background-color: black; color: green;") # border: 2px solid white


class InventoryScrollArea(QScrollArea):
    inventory_label_clicked = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)  # Allow the content to be resized

        scale_factor = calculate_scale_factor()
        self.setFixedSize(int(152 * scale_factor) , int (22 * scale_factor))
        self.scroll_content = QWidget()
        self.inventory_layout = QGridLayout()
        self.scroll_content.setLayout(self.inventory_layout)
        self.setWidget(self.scroll_content)

    def display_inventory(self, inventory_list):

        row, col = 0, 0
        for item in inventory_list:
            inventory_label = InventoryLabel(item, get_file_path("resources", "inventory", f"{item}.png"))
            inventory_label.clicked.connect(self.handle_inventory_label_click)
            self.inventory_layout.addWidget(inventory_label, row, col)
            col += 1    
            if col > 3:
                col = 0 
                row += 1

    def handle_inventory_label_click(self):
        sender = self.sender()
        inventory_name = sender.text()
        self.inventory_label_clicked.emit(inventory_name)

# TODO - Created custom class but may not actually be required
class InventoryLabel(QLabel):
    clicked = pyqtSignal(QGraphicsObject)

    def __init__(self, text, sprite_file_path):
        super().__init__(text)
        self._sprite_file_path = sprite_file_path
        
        # Set pixmap with scaled sprite
        scale_factor = calculate_scale_factor()
        sprite = QPixmap(self._sprite_file_path)
        new_width = int(sprite.width() * scale_factor)
        new_height = int(sprite.height() * scale_factor)
        self.setPixmap(sprite.scaled(new_width, new_height))

        # Remove padding
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)  # Align content to top-left
        self.setMargin(0) 

    @pyqtProperty(str)
    def sprite(self):
        return self._sprite

    def mousePressEvent(self, event):
        self.clicked.emit(self)

# Provides an interactive prop for any object displayed independently from the scene background
class Prop(QGraphicsObject):
    clicked = pyqtSignal(QGraphicsObject)
    entered = pyqtSignal(QGraphicsObject)
    left = pyqtSignal(QGraphicsObject)
    
    def __init__(self, name, pixmap):
        super().__init__()
        self._name = name
        self._pixmap = pixmap
        self._color = QColor(0, 0, 0, 0)  # transparent
     
        self.setAcceptHoverEvents(True) # was False by default

    def boundingRect(self):
        return QRectF(self._pixmap.rect())

    def paint(self, painter, option, widget=None):
        painter.drawPixmap(self.boundingRect().toRect(), self._pixmap)
        painter.fillRect(self.boundingRect(), self._color)

    def mousePressEvent(self, event):
        self.clicked.emit(self)

    def hoverEnterEvent(self, event):

        self._color = QColor(0, 0, 255, 128)  # Red, Green, Blue, Alpha
        self.update()  # Refresh the paint when entering hover

        self.entered.emit(self)

    def hoverLeaveEvent(self, event):

        self._color = QColor(0, 0, 0, 0)  # transparent
        self.update()  # Refresh the paint when leaving hover

        self.left.emit(self)

    @pyqtProperty(str)
    def name(self):
        return self._name

# Provides an inveractive hotspot for any object that is always in the scene backgroud
class Hotspot(QGraphicsObject):
    clicked = pyqtSignal(QGraphicsObject)
    entered = pyqtSignal(QGraphicsObject)
    left = pyqtSignal(QGraphicsObject)

    def __init__(self, name, x, y, width, height):
        super().__init__()
        
        self._name = name
        self._width = width
        self._height = height
        self._color = QColor(0, 0, 0, 0)  # transparent
        
        self.setPos(x, y)
        self.setAcceptHoverEvents(True) # was False by default

    def boundingRect(self):
        return QRectF(0, 0, self._width, self._height)

    def paint(self, painter, option, widget=None):
        painter.fillRect(self.boundingRect(), self._color)

    def mousePressEvent(self, event):
        self.clicked.emit(self)

    def hoverEnterEvent(self, event):
        
        self._color = QColor(0, 0, 255, 128)  # Red, Green, Blue, Alpha
        self.update()  # Refresh the paint when entering hover

        self.entered.emit(self)

    def hoverLeaveEvent(self, event):

        self._color = QColor(0, 0, 0, 0)  # transparent
        self.update()  # Refresh the paint when leaving hover

        self.left.emit(self)

    @pyqtProperty(str)
    def name(self):
        return self._name