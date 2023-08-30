import os
from PyQt6.QtGui import QGuiApplication

# Constants
SCREEN_RESOLUTION_HEIGHT = 180

def get_file_path(*path_segments):
    root_directory = os.path.dirname(os.path.abspath(__file__))
    root_directory = os.path.abspath(os.path.join(root_directory, "..", ".."))  # Move two levels up
    file_path = os.path.join(root_directory, *path_segments)
    return file_path

def calculate_scale_factor():
    primary_screen = QGuiApplication.primaryScreen()
    screen_geometry = primary_screen.availableGeometry()
    return screen_geometry.height() / SCREEN_RESOLUTION_HEIGHT