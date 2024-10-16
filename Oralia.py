import sys, mido
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from tab1 import Tab1
from tab2 import Tab2
from tab3 import Tab3

class Oralia(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = {}  # Dictionary to hold tab objects
        self.tab_widget = QTabWidget(self)  # QTabWidget object
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.West)
        self.setCentralWidget(self.tab_widget)
        self.tabs["Practical"] = Tab1(self.tab_widget)
        self.tab_widget.addTab(self.tabs["Practical"], "Practical")
        self.tabs["Theory"] = Tab2()
        self.tab_widget.addTab(self.tabs["Theory"], "Theory")
        self.tabs["Settings"] = Tab3()
        self.tab_widget.addTab(self.tabs["Settings"], "Settings")

app = QApplication([])
window = Oralia()
window.show()

with mido.open_input(callback=window.tabs["Practical"].note_handler) as inport:
    app.exec()
