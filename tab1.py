from PyQt6.QtWidgets import QWidget, QVBoxLayout,QListWidget,QHBoxLayout,QGraphicsScene, QGraphicsPixmapItem, QGraphicsView,QLabel,QPushButton
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import (
    Qt, QTimer, pyqtSignal)
import pickle,random,copy
class Tab1(QWidget):
    green_signal = pyqtSignal(int)
    red_signal = pyqtSignal(int)
    note_off_signal = pyqtSignal(int)
    def __init__(self, parent_widget, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.lastnote = 0
        self.previous_scale = None
        self.required_notes = []
        self.theorymode = None
        self.pressed_notes = []
        self.correct_answer = None
        self.correct_key = None

        with open('theory.pkl', 'rb') as file:
            self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file:
            self.Settings = pickle.load(file)
        self.parent_widget = parent_widget  # Store reference to QTabWidget

        self.setLayout(QVBoxLayout())

        self.horizontal = QHBoxLayout()
        self.layout().addLayout(self.horizontal)
        self.theory1 = QListWidget()
        self.theory2 = QListWidget()
        self.theory3 = QListWidget()

        self.horizontal.addWidget(self.theory1, stretch= 1)
        self.horizontal.addWidget(self.theory2, stretch=1)
        self.horizontal.addWidget(self.theory3, stretch=1)
        self.theory1.addItems(["Notes", "Scales", "Triads", "Sevenths", "Modes"])
        self.Scene = QGraphicsScene()
        self.BackgroundPixmap = QPixmap("/Users/williamcorney/PycharmProjects/Oralia4.5/Images/Piano/keys.png")
        self.BackgroundItem = QGraphicsPixmapItem(self.BackgroundPixmap)
        self.Scene.addItem(self.BackgroundItem)

        self.View = QGraphicsView(self.Scene)
        self.View.setFixedSize(self.BackgroundPixmap.size())
        self.View.setSceneRect(0, 0, self.BackgroundPixmap.width(), self.BackgroundPixmap.height())
        self.View.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.View.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.layout().addWidget(self.View)

        self.horizontal_vertical = QVBoxLayout()
        self.horizontal.addLayout(self.horizontal_vertical, 2)

        self.key_label = QLabel("C Major")
        self.key_label.setFont(QFont("Arial", 32))
        self.inversion_label = QLabel("B")
        self.fingering_label = QLabel("1,2,3,1,2,3,4,5")
        self.score_label = QLabel("Score :")
        self.score_value = QLabel("0")
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.go_button_clicked)

        self.horizontal_vertical.addWidget(self.key_label)
        self.horizontal_vertical.addWidget(self.inversion_label)
        self.horizontal_vertical.addWidget(self.fingering_label)
        self.horizontal_vertical.addWidget(self.score_label)
        self.horizontal_vertical.addWidget(self.score_value)
        self.horizontal_vertical.addWidget(self.go_button)
        self.green_signal.connect(self.insert_green_note)
        self.red_signal.connect(self.insert_red_note)
        self.note_off_signal.connect(self.delete_notes)

        with open('theory.pkl', 'rb') as file:
            self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file:
            self.Settings = pickle.load(file)

        self.pixmap_item = {}

        self.theory1.clicked.connect(self.theory1_clicked)
        self.theory2.clicked.connect(self.theory2_clicked)

        self.theory3.clicked.connect(self.theory3_clicked)

    def note_handler(self, mididata):
        if self.parent_widget.currentIndex() == 0:
            match self.theorymode:


                case "Notes":
                    if mididata.type == "note_on":
                        if mididata.note % 12 == self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.go_button_clicked()
                        else:
                            self.red_signal.emit(mididata.note)


                case "Scales":
                    if mididata.type == "note_on":
                        if mididata.note == self.required_notes[0]:
                            self.required_notes.pop(0)
                            self.green_signal.emit(mididata.note)
                            if len(self.required_notes) == 0:
                                self.go_button_clicked()
                        else:
                            self.red_signal.emit(mididata.note)
                            self.reset_scale()

                case "Triads":
                    if mididata.type == "note_on":
                        if mididata.note in self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.pressed_notes.append(mididata.note)
                            if len(self.pressed_notes) >= 3:
                                self.go_button_clicked()
                        else:
                            self.red_signal.emit(mididata.note)
                case "Sevenths":
                    if mididata.type == "note_on":
                        if mididata.note in self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.pressed_notes.append(mididata.note)
                            if len(self.pressed_notes) >= 4:
                                self.go_button_clicked()
                        else:
                            self.red_signal.emit(mididata.note)
                case "Modes":
                    if mididata.type == "note_on":
                        if mididata.note == self.required_notes[0]:
                            self.green_signal.emit(mididata.note)
                            self.required_notes.pop(0)
                            if len(self.required_notes) == 0:
                                self.go_button_clicked()
                        else:
                            self.red_signal.emit(mididata.note)
                            self.reset_scale()

            if mididata.type == "note_off":
                self.note_off_signal.emit(mididata.note)
                self.pressed_notes.remove(mididata.note)

        elif self.parent_widget.currentIndex() == 1:
        # Call the method in Tab2
            self.parent_widget.widget(1).midiprocessor(mididata)


    def insert_green_note(self, note):
        if self.parent_widget.currentIndex() == 0:

            self.xcord = self.Theory["NoteCoordinates"][note % 12] + ((note // 12) - 4) * 239
            self.pixmap_item[note] = QGraphicsPixmapItem(
                QPixmap("./Images/Piano/key_" + "green" + self.Theory["NoteFilenames"][note % 12])
            )
            self.pixmap_item[note].setPos(self.xcord, 0)
            current_scene = self.pixmap_item[note].scene()
            if current_scene:
                current_scene.removeItem(self.pixmap_item[note])
            self.Scene.addItem(self.pixmap_item[note])

    def insert_red_note(self, note):
        if self.parent_widget.currentIndex() == 0:


            self.xcord = self.Theory["NoteCoordinates"][note % 12] + ((note // 12) - 4) * 239
            self.pixmap_item[note] = QGraphicsPixmapItem(
                QPixmap("./Images/Piano/key_" + "red" + self.Theory["NoteFilenames"][note % 12])
            )
            self.pixmap_item[note].setPos(self.xcord, 0)
            current_scene = self.pixmap_item[note].scene()
            if current_scene:
                current_scene.removeItem(self.pixmap_item[note])
            self.Scene.addItem(self.pixmap_item[note])

    def delete_notes(self, note):

        if note in self.pixmap_item:
            if self.pixmap_item[note].scene():
                self.pixmap_item[note].scene().removeItem(self.pixmap_item[note])
            del self.pixmap_item[note]

    def go_button_clicked(self):

        self.get_theory_items()

    def theory1_clicked(self):
        self.theory2.clear()
        self.theory3.clear()
        self.theorymode = self.theory1.selectedItems()[0].text()

        match self.theorymode:
            case "Notes":
                self.theory2.addItems(["Naturals", "Sharps", "Flats"])
            case "Scales":
                self.theory2.addItems(["Major", "Minor", "Melodic Minor", "Harmonic Minor"])
            case "Triads":
                self.theory2.addItems(["Major", "Minor"])
            case "Sevenths":
                self.theory2.addItems(["Maj7", "Min7", "7", "Dim7", "m7f5"])
            case "Modes":
                self.theory2.addItems(["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"])

    def theory2_clicked(self):
        match self.theorymode:
            case "Notes":
                self.theory2list = [item.text() for item in self.theory2.selectedItems()]
            case "Scales":
                self.theory2list = [item.text() for item in self.theory2.selectedItems()]
            case "Triads":
                self.theory2list = [item.text() for item in self.theory2.selectedItems()]
                self.theory3.clear()
                self.theory3.addItems(["Root", "First", "Second"])
            case "Sevenths":
                self.theory2list = [item.text() for item in self.theory2.selectedItems()]
                self.theory3.clear()
                self.theory3.addItems(["Root", "First", "Second", "Third"])
            case "Modes":
                self.theory2list = [item.text() for item in self.theory2.selectedItems()]

    def theory3_clicked(self):
        match self.theorymode:
            case "Notes":
                self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Scales":
                self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Triads":
                self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Sevenths":
                self.theory3list = [item.text() for item in self.theory3.selectedItems()]
    def get_theory_items(self):
        if hasattr(self, 'theorymode'):
            match self.theorymode:
                case "Notes":
                    self.get_random_values()
                    self.required_notes = self.int
                    if self.type == "Flats":
                        self.key_label.setText(self.Theory["Enharmonic"][self.required_notes])
                    else:
                        self.key_label.setText(self.Theory["Chromatic"][self.required_notes])
                case "Scales":
                    self.get_random_values()
                    while self.current_scale == self.previous_scale:
                        self.get_random_values()
                    self.required_notes = (self.midi_note_scale_generator((self.Theory["Scales"][self.type][self.int]),
                                                                          octaves=int(self.Settings['User']['Octaves']),
                                                                          base_note=60))
                    self.deepnotes = copy.deepcopy(self.required_notes)
                    self.previous_scale = self.current_scale
                    self.key_label.setText(self.current_scale)
                    self.fingering_label.setText(str(self.Theory['Fingering'][self.int][self.current_scale]["Right"]))
                case "Triads":
                    if not self.theory2list:
                        print("You need to select a scale type")
                        return
                    if not self.theory3list:
                        print("You need to select an inversion")
                        return
                    self.get_random_values()
                    while self.current_scale == self.previous_scale:
                        self.get_random_values()
                    self.required_notes = self.midi_note_scale_generator(
                        self.Theory["Triads"][self.current_scale][self.inv],
                        octaves=1,
                        base_note=60, include_descending=False)
                    self.current_scale = f"{self.current_scale} {self.inv}"
                    self.deepnotes = copy.deepcopy(self.required_notes)
                    self.previous_scale = self.current_scale
                    self.key_label.setText(self.current_scale)
                case "Sevenths":
                    if not self.theory2list:
                        print("You need to select a scale type")
                        return
                    if not self.theory3list:
                        print("You need to select an inversion")
                        return
                    self.get_random_values()
                    while self.current_scale == self.previous_scale:
                        self.get_random_values()
                    self.required_notes = self.midi_note_scale_generator(
                        self.Theory["Sevenths"][self.current_scale][self.inv],
                        octaves=1,
                        base_note=60, include_descending=False)
                    self.current_scale = f"{self.current_scale} {self.inv}"
                    self.deepnotes = copy.deepcopy(self.required_notes)
                    self.previous_scale = self.current_scale
                    self.key_label.setText(self.current_scale)
                case "Modes":
                    if not self.theory2list:
                        print("You need to select a scale type")
                        return
                    self.get_random_values()
                    while self.current_scale == self.previous_scale:
                        self.get_random_values()
                    self.required_notes = (
                        self.midi_note_scale_generator((self.Theory["Modes"][self.letter][self.type]),
                                                       octaves=1,
                                                       base_note=60))
                    self.deepnotes = copy.deepcopy(self.required_notes)
                    self.previous_scale = self.current_scale
                    self.key_label.setText(self.current_scale)

    def midi_note_scale_generator(self, notes, octaves=1, base_note=60, repeat_middle=False, include_descending=True):
        adjusted_notes = [note + base_note for note in notes]
        extended_notes = adjusted_notes[:]
        for octave in range(1, octaves):
            extended_notes.extend([note + 12 * octave for note in adjusted_notes[1:]])
        if include_descending:
            if repeat_middle:
                reversed_notes = extended_notes[::-1]
            else:
                reversed_notes = extended_notes[:-1][::-1]
            extended_notes.extend(reversed_notes)
        return extended_notes

    def get_random_values(self):
        match self.theorymode:
            case "Notes":
                self.type = random.choice(self.theory2list)
                self.notes = self.Theory["Notes"][self.type]
                self.int = random.choice(self.notes)
                while self.lastnote == self.int:
                    self.int = random.choice(self.notes)
                self.letter = self.Theory["Chromatic"][self.int]
                self.lastnote = self.int
            case "Scales":
                self.int = random.choice([0, 2, 4, 5, 7, 9, 11])
                self.letter = self.Theory["Enharmonic"][self.int]
                self.type = random.choice(self.theory2list)
                self.current_scale = f"{self.letter} {self.type}"
            case "Triads":
                self.int = random.randint(0, 11)
                self.letter = self.Theory["Enharmonic"][self.int]
                self.type = random.choice(self.theory2list)
                self.current_scale = f"{self.letter} {self.type}"
                self.inv = random.choice(self.theory3list)
            case "Sevenths":
                self.int = random.randint(0, 11)
                self.letter = self.Theory["Enharmonic"][self.int]
                self.type = random.choice(self.theory2list)
                self.current_scale = f"{self.letter} {self.type}"
                self.inv = random.choice(self.theory3list)
            case "Modes":
                self.int = random.randint(0, 11)
                self.letter = self.Theory["Enharmonic"][self.int]
                self.type = random.choice(self.theory2list)
                self.current_scale = f"{self.letter} {self.type}"


    def reset_scale(self):
        if hasattr(self, 'deepnotes') and self.deepnotes:
            self.required_notes = copy.deepcopy(self.deepnotes)