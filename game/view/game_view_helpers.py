from PyQt6.QtCore import pyqtProperty, pyqtSignal, QRectF
from PyQt6.QtWidgets import QLabel, QGraphicsObject
from PyQt6.QtGui import QPixmap, QColor, QBrush

### All classes supporting the GameView ###

# TODO - Created custom class but may not actually be required
class InventoryLabel(QLabel):
    clicked = pyqtSignal(QGraphicsObject)

    def __init__(self, text, sprite):
        super().__init__(text)
        self._sprite = sprite
        self.setPixmap(QPixmap(self._sprite))

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
       