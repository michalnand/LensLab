import sys

from PyQt5.QtWidgets import (QFileDialog, QWidget)

from Core       import *
from PhotoView  import *

from TabButtons import *

from Tools      import *
from Stacking   import *
from Export     import *


class LensLabApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.core   = Core()

        self.setWindowTitle("Lens Lab")
        self.setGeometry(100, 100, 1800, 900)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)


        self.main_layout = QHBoxLayout(self.central_widget)

        # photo view and thumbnails
        self.photo_view = PhotoView(self.core)
        self.main_layout.addWidget(self.photo_view.get(), stretch=15)

        # create main tabs
        self.main_tabs = TabButtons()

        # tool panel
        self.tool_widget = Tools(self.core)
        self.main_tabs.add("Tools", self.tool_widget.get())

        self.stacking_widget = Stacking(self.core)
        self.main_tabs.add("Stacking", self.stacking_widget.get())

        self.export_widget = Export(self.core)
        self.main_tabs.add("Export", self.export_widget.get())


        self.main_layout.addWidget(self.main_tabs.get(), stretch=5)

        
        self.menu = self.menuBar()
        file_menu = self.menu.addMenu("File")

        open_folder_action = file_menu.addAction("Open Folder")
        open_folder_action.triggered.connect(self.on_open_folder)

    def on_open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder:
            self.core.load_images(folder)
       
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app_main = LensLabApp()
    app_main.show()
    sys.exit(app.exec_())

