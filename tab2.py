from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QRadioButton, QButtonGroup, QLabel, \
    QPushButton, QListWidgetItem
from PyQt6.QtGui import QFont,QPixmap
from PyQt6.QtCore import QSize, QTimer,Qt
import sqlite3
import random,pickle


class Tab2(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_correct_answer = None
        self.mode = "notes"
        self.horizontal1 = QHBoxLayout()
        self.horizontal2 = QHBoxLayout()
        self.theory4 = QListWidget()
        self.theory4.clicked.connect(self.theory4_clicked)
        self.theory5 = QListWidget()
        self.horizontal1.addWidget(self.theory4)
        self.horizontal1.addWidget(self.theory5)
        self.theory4.addItems(['Notes', "Keys"])
        self.signaturetype = "Major"
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
        # self.horizontal2.addWidget(self.question_label)
        # self.horizontal2.addWidget(self.question_image)
        self.horizontal1_vertical.addWidget(self.key_label)
        self.horizontal1_vertical.addWidget(self.inversion_label)
        self.horizontal1_vertical.addWidget(self.fingering_label)
        self.horizontal1_vertical.addWidget(self.score_label)
        self.horizontal1_vertical.addWidget(self.score_value)
        self.horizontal1_vertical.addWidget(self.go_button)

        self.go_button.clicked.connect(self.load_quiz)
        self.layout = QVBoxLayout(self)
        self.layout.addLayout(self.horizontal1, 1)
        self.layout.addLayout(self.horizontal2, 3)

        self.option_buttons = []
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.question_image)
        self.button_layout.addWidget(self.question_label)
        self.layout.addLayout(self.button_layout)

        self.vertical_layout1 = QVBoxLayout()
        self.vertical_layout2 = QVBoxLayout()
        self.button_layout.addLayout(self.vertical_layout1)
        self.button_layout.addLayout(self.vertical_layout2)

        for i in range(4):
            button = QPushButton(self)
            button.setFixedHeight(50)
            button.setFixedWidth(200)
            button.setStyleSheet("""
                    font-size: 24px;
                    background-color: green;
                    border-radius: 8px;
                    border: 2px solid black;
                """)
            if i < 2:
                self.vertical_layout1.addWidget(button)
            else:
                self.vertical_layout2.addWidget(button)
            self.option_buttons.append(button)

        with open('theory.pkl', 'rb') as file:
            self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file:
            self.Settings = pickle.load(file)

    def theory4_clicked(self):
        self.theory5.clear()
        self.theorymode = self.theory4.selectedItems()[0].text()
        match self.theorymode:
            case "Notes":
                self.theory5.addItems(["Note Identification"])
                self.mode = "notes"
            case "Keys":
                self.mode = "keys"
                self.theory5.addItems(["Key Identification"])

    def database_lookup(self, query):
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        cursor.execute(query)
        response = cursor.fetchall()
        conn.close()
        return response

    def generate_quiz(self, last_correct_answer=None):
        if self.mode == 'notes':
            query = "SELECT note_file_name, note_display_name, note_clef,note_file_name2 FROM notes WHERE note_clef = 'Treble'"
            file_field = "note_file_name"
            display_field = "note_display_name"
        else:  # mode == 'signatures'
            query = f"SELECT signature_filename, signature_displayname FROM signatures WHERE signature_type = '{self.signaturetype}'"
            file_field = "signature_filename"
            display_field = "signature_displayname"

        rows = self.database_lookup(query)

        if last_correct_answer:
            rows = [row for row in rows if row[0] != last_correct_answer]

        correct_row = random.choice(rows)
        correct_answer = {
            "answer_image": correct_row[0],
            "note_display_name": correct_row[1],
            "note_file_name2" : correct_row[3]
        }

        # print(f"Correct Answer: {correct_row[0]}")

        remaining_rows = [row for row in rows if row[1] != correct_row[1]]
        wrong_rows = random.sample(remaining_rows, 3)
        wrong_answers = {
            "wrong_answer_1": {
                "answer_image": wrong_rows[0][0],
                "note_display_name": wrong_rows[0][1]
            },
            "wrong_answer_2": {
                "answer_image": wrong_rows[1][0],
                "note_display_name": wrong_rows[1][1]
            },
            "wrong_answer_3": {
                "answer_image": wrong_rows[2][0],
                "note_display_name": wrong_rows[2][1]
            }
        }
        #
        # for key, answer in wrong_answers.items():
        #     print(f"Wrong Answer: {answer['answer_image']}")

        return {"correct_answer": correct_answer, "wrong_answers": wrong_answers}

    def load_quiz(self):
        self.quiz = self.generate_quiz( self.last_correct_answer)

        if self.mode == 'notes':
            image_base_path = "/Users/williamcorney/PycharmProjects/Oralia4.5/Images/Notes/Treble/"
        else:
            image_base_path = "/Users/williamcorney/PycharmProjects/Oralia4.5/Images/Signatures/"

        image_path = image_base_path + self.quiz['correct_answer']['answer_image']
        self.question_image.clear()
        # Load and set the image
        pixmap = QPixmap(image_path)

        scaled_pixmap = pixmap.scaled(int(pixmap.width() * 0.1), int(pixmap.height() * 0.3), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.question_label.setPixmap(pixmap)
        # Clear the result label
        options = [self.quiz['correct_answer']['note_display_name']]
        options.extend([self.quiz['wrong_answers'][key]['note_display_name'] for key in self.quiz['wrong_answers']])
        random.shuffle(options)

        for i, option in enumerate(options):
            self.option_buttons[i].setText(option)
            # Disconnect any existing signal
            try:
                self.option_buttons[i].clicked.disconnect()
            except TypeError:
                pass
            # Connect the new signal
            self.option_buttons[i].clicked.connect(
                lambda checked, opt=option: self.check_answer(opt, self.quiz['correct_answer']['note_display_name']))

        # Remember the correct answer to avoid repeating it next time
        self.last_correct_answer = self.quiz['correct_answer']['answer_image']

    def check_answer(self, selected, correct):
        if selected == correct:
            result_image = "correct.png"
            QTimer.singleShot(500, self.load_quiz)
        else:
            result_image = "incorrect.png"

        result_image_path = "/Users/williamcorney/PycharmProjects/Oralia4.5/Images/Notes/Treble/" + result_image
        pixmap = QPixmap(result_image_path)


        scaled_pixmap = pixmap.scaled(int(pixmap.width() * 0.3), int(pixmap.height() * 0.3),
                                      Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.question_image.setPixmap(scaled_pixmap)



    def midiprocessor (self,mididata):

        if mididata.type == "note_on":
            pressednote1 =  (self.Theory["Chromatic"][mididata.note %12 ])
            pressednote2 = mididata.note // 12 -1
            pressednote = (f"{pressednote1}{pressednote2}")


            self.check_answer(pressednote, self.quiz['correct_answer']['note_file_name2'])
