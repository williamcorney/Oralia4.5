from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
import pickle


class Tab3(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open('theory.pkl', 'rb') as file:
            self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file:
            self.Settings = pickle.load(file)
        # self.update_theory_shells()
        #
        # self.save_theory_to_file()


        # print (self.Settings)
        # for key, value in self.Theory.items():
        #     print(f"{key}: {value}")



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

    def update_theory_shells(self):
        # Initialize the Shells key in self.Theory if it doesn't already exist
        if "Shells" not in self.Theory:
            self.Theory["Shells"] = {}

        # Define the major and minor scales with their 3rd and 7th degree notes
        scales = {
            "C Major": [4, 11], "G Major": [11, 6], "D Major": [6, 1], "A Major": [1, 8], "E Major": [8, 3],
            "B Major": [3, 10], "F# Major": [10, 5],
            "C Minor": [3, 10], "G Minor": [10, 5], "D Minor": [5, 0], "A Minor": [0, 7], "E Minor": [7, 2],
            "B Minor": [2, 9], "F# Minor": [9, 4],
            "F Major": [9, 4], "B♭ Major": [4, 11], "E♭ Major": [11, 6], "A♭ Major": [6, 1], "D♭ Major": [1, 8],
            "G♭ Major": [8, 3], "C♭ Major": [3, 10],
            "F Minor": [8, 3], "B♭ Minor": [3, 10], "E♭ Minor": [10, 5], "A♭ Minor": [5, 0], "D♭ Minor": [0, 7],
            "G♭ Minor": [7, 2], "C♭ Minor": [2, 9]
        }

        # Populate the Shells structure
        for scale, notes in scales.items():
            self.Theory["Shells"][scale] = {
                0: notes,
                1: notes[::-1]
            }

    # Example usage
    # self.update_theory_shells()
    # print(self.Theory["Shells"]["C Major"])
    def save_theory_to_file(self):
        with open('theory.pkl', 'wb') as file:
            pickle.dump(self.Theory, file)

    # Example usage
    # self.save_theory_to_file()