from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QRadioButton, QButtonGroup, QLabel, \
    QPushButton, QListWidgetItem
from PyQt6.QtGui import QFont


class Tab2(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.horizontal1 = QHBoxLayout()
        self.horizontal2 = QHBoxLayout()

        self.theory4 = QListWidget()
        self.theory5 = QListWidget()

        self.theory4.clicked.connect(self.set_question_bank)

        self.horizontal1.addWidget(self.theory4)
        self.horizontal1.addWidget(self.theory5)

        self.theory4.addItems(['Note Identification', "Key Identification", "Key Signature Identification"])

        self.radiobuttons = QButtonGroup()
        self.A = QRadioButton("A")
        self.B = QRadioButton("B")
        self.C = QRadioButton("C")
        self.D = QRadioButton("D")

        self.radio_buttons = [self.A, self.B, self.C, self.D]

        for radio_button in self.radio_buttons:
            self.radiobuttons.addButton(radio_button)
            radio_button.clicked.connect(self.check_answer)

        self.question_label = QLabel("ABC")
        self.question_image = QLabel("Image")
        self.key_label = QLabel("C Major")
        self.key_label.setFont(QFont("Arial", 32))
        self.inversion_label = QLabel("B")
        self.fingering_label = QLabel("1,2,3,1,2,3,4,5")
        self.score_label = QLabel("Score :")
        self.score_value = QLabel("0")
        self.go_button = QPushButton("Go")

        self.horizontal1_vertical = QVBoxLayout()
        self.horizontal1.addLayout(self.horizontal1_vertical)
        self.horizontal2_vertical = QVBoxLayout()
        self.horizontal2.addLayout(self.horizontal2_vertical)

        self.horizontal2.addWidget(self.question_label)
        self.horizontal1_vertical.addWidget(self.key_label)
        self.horizontal1_vertical.addWidget(self.inversion_label)
        self.horizontal1_vertical.addWidget(self.fingering_label)
        self.horizontal1_vertical.addWidget(self.score_label)
        self.horizontal1_vertical.addWidget(self.score_value)
        self.horizontal1_vertical.addWidget(self.go_button)

        self.go_button.clicked.connect(self.generate_question)

        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.horizontal1)
        self.layout.addLayout(self.horizontal2)
        self.layout.addWidget(self.A)
        self.layout.addWidget(self.B)
        self.layout.addWidget(self.C)
        self.layout.addWidget(self.D)

    def set_question_bank(self):
        # Define your method here
        pass

    def check_answer(self):
        # Define your method here
        pass

    def generate_question(self):
        # Define your method here
        pass
