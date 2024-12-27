from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton)

class TabButtons(QWidget):
    def __init__(self):
        super().__init__()

        self.main_widget    = QWidget()
        self.main_layout    = QVBoxLayout(self.main_widget)

        self.buttons_widget = QWidget()
        self.buttons_layout = QHBoxLayout(self.buttons_widget)
        self.buttons_layout.setSpacing(0)


        self.main_layout.addWidget(self.buttons_widget)

        self.stacked_widgets = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widgets)

        self.names   = []
        self.buttons = []

        self.idx_curr = -1

    def add(self, name, widget):
        idx = len(self.stacked_widgets)
        button = QPushButton(name)
        button.clicked.connect(lambda _, index=idx: self.on_button_clicked(index))

        self.stacked_widgets.addWidget(widget)
        self.names.append(name)
        self.buttons.append(button)

        self.buttons_layout.addWidget(button)

        if idx == 0:
            self.on_button_clicked(0)

        
    def get(self):
        return self.main_widget

    def on_button_clicked(self, idx):
        if idx == self.idx_curr:
            return
        
        self.idx_curr = idx

        for button in self.buttons:
            button.setStyleSheet("")
        
        self.buttons[self.idx_curr].setStyleSheet("background-color: #1E90FF; color: white;")

        self.stacked_widgets.setCurrentIndex(self.idx_curr)
