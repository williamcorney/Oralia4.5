from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
import pickle


class Tab3(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open('theory.pkl', 'rb') as file:
            self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file:
            self.Settings = pickle.load(file)

        print (self.Settings)

        layout = QVBoxLayout(self)

        # Create a label
        self.label = QLabel("Select Octaves", self)
        layout.addWidget(self.label)

        # Create a combo box
        self.combo_box = QComboBox(self)
        self.combo_box.addItems(['1', '2', '3'])

        # Set current value
        current_value = str(self.Settings['User']['Octaves'])
        self.combo_box.setCurrentText(current_value)
        layout.addWidget(self.combo_box)

        self.combo_box.currentTextChanged.connect(self.update_octaves)

        self.setLayout(layout)

    def update_octaves(self, value):
        self.Settings['User']['Octaves'] = int(value)
        with open('settings.pkl', 'wb') as file:
            pickle.dump(self.Settings, file)
