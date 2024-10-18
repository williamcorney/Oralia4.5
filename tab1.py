from PyQt6.QtWidgets import QWidget, QVBoxLayout,QListWidget,QHBoxLayout,QGraphicsScene, QGraphicsPixmapItem, QGraphicsView,QLabel,QPushButton,QAbstractItemView
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import (Qt, QTimer, pyqtSignal)
import pickle,random,copy, pygame,os,time
class Tab1(QWidget):
    green_signal = pyqtSignal(int)
    red_signal = pyqtSignal(int)
    note_off_signal = pyqtSignal(int)
    def __init__(self, parent_widget, *args, **kwargs):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        pygame.mixer.init()
        super().__init__(*args, **kwargs)
        self.score = 0
        self.lastnote = 0
        self.index = 0
        self.previous_scale = None
        self.theorymode = None
        self.correct_answer = None
        self.correct_key = None
        self.required_notes = []
        self.pressed_notes = []
        self.pixmap_item = {}
        with open('theory.pkl', 'rb') as file: self.Theory = pickle.load(file)
        with open('settings.pkl', 'rb') as file: self.Settings = pickle.load(file)
        self.parent_widget = parent_widget  # Store reference to QTabWidget
        self.setLayout(QVBoxLayout())
        self.horizontal = QHBoxLayout()
        self.layout().addLayout(self.horizontal)
        self.theory1 = QListWidget()
        self.theory2 = QListWidget()
        self.theory3 = QListWidget()
        self.horizontal.addWidget(self.theory1, stretch=1)
        self.horizontal.addWidget(self.theory2, stretch=1)
        self.horizontal.addWidget(self.theory3, stretch=1)
        self.theory1.addItems(["Notes", "Scales", "Triads", "Sevenths", "Modes","Shells"])
        self.Theory["Stats"] = {}
        self.theory2.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.Scene = QGraphicsScene()
        self.BackgroundPixmap = QPixmap("/Users/williamcorney/PycharmProjects/Oralia5/Images/Piano/keys.png")
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
        self.key_label = QLabel("")
        self.key_label.setFont(QFont("Arial", 32))
        self.inversion_label = QLabel("")
        self.fingering_label = QLabel("")
        self.score_value = QLabel("")
        self.go_button = QPushButton("Go")
        self.go_button.clicked.connect(self.go_button_clicked)
        self.horizontal_vertical.addWidget(self.key_label)
        self.horizontal_vertical.addWidget(self.inversion_label)
        self.horizontal_vertical.addWidget(self.fingering_label)
        self.horizontal_vertical.addWidget(self.score_value)
        self.horizontal_vertical.addWidget(self.go_button)
        self.green_signal.connect(self.insert_green_note)
        self.red_signal.connect(self.insert_red_note)
        self.note_off_signal.connect(self.delete_notes)
        self.theory1.clicked.connect(self.theory1_clicked)
        self.theory2.clicked.connect(self.theory2_clicked)
        self.theory3.clicked.connect(self.theory3_clicked)
        horizontal_layout = QHBoxLayout()
        self.labels = []
        for i in range(6):
            v_layout = QVBoxLayout()
            for j in range(2):
                label = QLabel("", self)
                self.labels.append(label)
                v_layout.addWidget(label)
            horizontal_layout.addLayout(v_layout)
        self.horizontal_vertical.addLayout(horizontal_layout)
    def note_handler(self, mididata):
        if self.parent_widget.currentIndex() == 0:
            match self.theorymode:
                case "Notes":
                    if mididata.type == "note_on":
                        if mididata.note % 12 == self.required_notes:
                            self.Theory["Stats"][str(self.letter)] +=1
                            self.populate_labels(self.Theory['Stats'])
                            self.green_signal.emit(mididata.note)
                            self.go_button_clicked()
                            self.result_pixmap("correct")

                        else:
                            self.result_pixmap("incorrect")
                            self.red_signal.emit(mididata.note)
                            self.Theory["Stats"][str(self.letter)] -= 1
                            self.populate_labels(self.Theory['Stats'])
                case "Scales":
                    if mididata.type == "note_on":
                        if mididata.note == self.required_notes[0]:
                            self.required_notes.pop(0)
                            self.green_signal.emit(mididata.note)
                            if len(self.required_notes) == 0:
                                self.announce_scale("01")
                                self.Theory["Stats"][str(self.letter)] += 1
                                self.populate_labels(self.Theory['Stats'])
                                self.go_button_clicked()
                        else:
                            self.Theory["Stats"][str(self.letter)] -= 1
                            self.populate_labels(self.Theory['Stats'])
                            self.red_signal.emit(mididata.note)
                            self.reset_scale()
                case "Triads":
                    if mididata.type == "note_on":
                        if mididata.note in self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.pressed_notes.append(mididata.note)
                            if len(self.pressed_notes) >= 3:
                                self.Theory["Stats"][str(self.letter)] += 1
                                self.populate_labels(self.Theory['Stats'])
                                self.result_pixmap("correct")
                                self.go_button_clicked()
                        else:
                            self.result_pixmap("incorrect")
                            self.red_signal.emit(mididata.note)
                case "Sevenths":
                    if mididata.type == "note_on":
                        if mididata.note in self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.pressed_notes.append(mididata.note)
                            if len(self.pressed_notes) >= 4:
                                self.Theory["Stats"][str(self.letter)] += 1
                                self.populate_labels(self.Theory['Stats'])
                                self.result_pixmap("correct")
                                self.go_button_clicked()
                        else:
                            self.result_pixmap("incorrect")
                            self.red_signal.emit(mididata.note)
                case "Modes":
                    if mididata.type == "note_on":
                        if mididata.note == self.required_notes[0]:
                            self.green_signal.emit(mididata.note)
                            self.required_notes.pop(0)
                            if len(self.required_notes) == 0:
                                self.result_pixmap("correct")
                                self.go_button_clicked()
                        else:
                            self.result_pixmap("incorrect")
                            self.red_signal.emit(mididata.note)
                            self.reset_scale()
                case "Shells":
                    if mididata.type == "note_on":
                        if mididata.note in self.required_notes:
                            self.green_signal.emit(mididata.note)
                            self.pressed_notes.append(mididata.note)
                            if len(self.pressed_notes) >= 2:
                                self.Theory["Stats"][str(self.letter)] += 1
                                self.populate_labels(self.Theory['Stats'])
                                self.go_button_clicked()
                                self.result_pixmap("correct")
                        else:
                            self.result_pixmap("incorrect")

                            self.red_signal.emit(mididata.note)

            if mididata.type == "note_off":
                self.note_off_signal.emit(mididata.note)
                self.pressed_notes.remove(mididata.note)
        elif self.parent_widget.currentIndex() == 1:self.parent_widget.widget(1).midiprocessor(mididata)
    def insert_green_note(self, note):
        if self.parent_widget.currentIndex() == 0:
            self.xcord = self.Theory["NoteCoordinates"][note % 12] + ((note // 12) - 4) * 239
            self.pixmap_item[note] = QGraphicsPixmapItem(QPixmap("./Images/Piano/key_" + "green" + self.Theory["NoteFilenames"][note % 12]))
            self.pixmap_item[note].setPos(self.xcord, 0)
            current_scene = self.pixmap_item[note].scene()
            if current_scene:current_scene.removeItem(self.pixmap_item[note])
            self.Scene.addItem(self.pixmap_item[note])
    def insert_red_note(self, note):
        if self.parent_widget.currentIndex() == 0:
            self.xcord = self.Theory["NoteCoordinates"][note % 12] + ((note // 12) - 4) * 239
            self.pixmap_item[note] = QGraphicsPixmapItem(QPixmap("./Images/Piano/key_" + "red" + self.Theory["NoteFilenames"][note % 12]))
            self.pixmap_item[note].setPos(self.xcord, 0)
            current_scene = self.pixmap_item[note].scene()
            if current_scene:current_scene.removeItem(self.pixmap_item[note])
            self.Scene.addItem(self.pixmap_item[note])
    def delete_notes(self, note):
        if note in self.pixmap_item:
            if self.pixmap_item[note].scene():self.pixmap_item[note].scene().removeItem(self.pixmap_item[note])
            del self.pixmap_item[note]
    def go_button_clicked(self):
        self.get_theory_items()
    def theory1_clicked(self):
        self.clear_labels()
        self.score_value.setText("")
        self.fingering_label.clear()
        self.key_label.setText("")
        self.Theory['Stats'] = {}
        self.theory2.clear()
        self.theory3.clear()
        self.theorymode = self.theory1.selectedItems()[0].text()
        match self.theorymode:
            case "Notes":self.theory2.addItems(["Naturals", "Sharps", "Flats"])
            case "Scales":self.theory2.addItems(["Major", "Minor", "Melodic Minor", "Harmonic Minor"])
            case "Triads":self.theory2.addItems(["Major", "Minor"])
            case "Sevenths":self.theory2.addItems(["Maj7", "Min7", "7", "Dim7", "m7f5"])
            case "Modes":self.theory2.addItems(["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian", "Locrian"])
            case "Shells":self.theory2.addItems(["Major", "Minor","Dominant"])
    def theory2_clicked(self):
        self.Theory['Stats'] = {}
        self.theory3.clear()
        self.theory2list = [item.text() for item in self.theory2.selectedItems()]
        match self.theorymode:
            case "Notes": pass
            case "Scales": self.theory3.addItems(["Right","Left"])
            case "Triads": self.theory3.addItems(["Root", "First", "Second"])
            case "Sevenths": self.theory3.addItems(["Root", "First", "Second", "Third"])
            case "Modes": pass
            case "Shells": self.theory3.addItems(["3/7","7/3"])
    def theory3_clicked(self):
        match self.theorymode:
            case "Notes":self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Scales":self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Triads":self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Sevenths":self.theory3list = [item.text() for item in self.theory3.selectedItems()]
            case "Shells":self.theory3list = [item.text() for item in self.theory3.selectedItems()]

    def get_theory_items(self):
        if not hasattr(self, 'theorymode') or not hasattr(self, 'theory2list'):
            return

        self.get_random_values()

        # Handle non-Notes cases where self.current_scale is necessary
        if self.theorymode in ["Scales", "Triads", "Sevenths", "Modes", "Shells"]:
            while self.current_scale == self.previous_scale:
                self.get_random_values()
            self.previous_scale = self.current_scale

        if self.letter not in self.Theory["Stats"]:
            self.Theory["Stats"][str(self.letter)] = 0

        match self.theorymode:
            case "Notes":
                self.required_notes = self.int
                scale_text = self.Theory["Enharmonic"][self.required_notes] if self.type == "Flats" else \
                self.Theory["Chromatic"][self.required_notes]
                self.key_label.setText(scale_text)
            case "Scales":
                if self.type == "Harmonic Minor":
                    self.required_notes = self.midi_note_scale_generator(
                        self.Theory["Scales"]["Harmonic Minor"][self.int],
                        octaves=int(self.Settings['User']['Octaves']), base_note=60, include_descending=False)
                    descending_notes = self.midi_note_scale_generator(self.Theory["Scales"]["Minor"][self.int],
                                                                      octaves=int(self.Settings['User']['Octaves']),
                                                                      base_note=60, include_descending=True)
                    self.required_notes.extend(descending_notes[len(descending_notes) // 2:])
                else:
                    self.required_notes = self.midi_note_scale_generator(self.Theory["Scales"][self.type][self.int],
                                                                         octaves=int(self.Settings['User']['Octaves']),
                                                                         base_note=60)
                self.key_label.setText(self.current_scale)
            case "Triads":
                self.set_chord_notes(self.Theory["Triads"])
                self.key_label.setText(f"{self.current_scale} {self.inv}")
            case "Sevenths":
                self.set_chord_notes(self.Theory["Sevenths"])
                self.key_label.setText(f"{self.current_scale} {self.inv}")
            case "Modes":
                self.required_notes = self.midi_note_scale_generator(self.Theory["Modes"][self.letter][self.type],
                                                                     octaves=1, base_note=60)
                self.key_label.setText(self.current_scale)
            case "Shells":
                self.set_shell_notes()
                self.key_label.setText(f"{self.current_scale} 7th")

        self.deepnotes = copy.deepcopy(self.required_notes)

        # Announce the scale for all modes except "Notes"
        if self.theorymode != "Notes":
            self.announce_scale(self.current_scale)

    def midi_note_scale_generator(self, notes, octaves=1, base_note=60, repeat_middle=False, include_descending=True):
        adjusted_notes = [note + base_note for note in notes]
        extended_notes = adjusted_notes[:]
        for octave in range(1, octaves):
            extended_notes.extend([note + 12 * octave for note in adjusted_notes[1:]])
        if include_descending:
            reversed_notes = extended_notes[::-1] if repeat_middle else extended_notes[:-1][::-1]
            extended_notes.extend(reversed_notes)
        return extended_notes

    def get_random_values(self):
        if not hasattr(self, 'theorymode'): return

        def set_common_values(int_range, scale_key):
            self.int = random.choice(int_range)
            while self.lastnote == self.int: self.int = random.choice(int_range)
            self.letter = self.Theory[scale_key][self.int]
            self.lastnote = self.int
            self.type = random.choice(self.theory2list)
            self.current_scale = f"{self.letter} {self.type}"

        match self.theorymode:
            case "Notes":
                if not hasattr(self,"theory2list") : return
                self.type = random.choice(self.theory2list)
                self.notes = self.Theory["Notes"][self.type]
                self.int = random.choice(self.notes)
                while self.lastnote == self.int:self.int = random.choice(self.notes)
                self.letter = self.Theory["Chromatic"][self.int]
                self.lastnote = self.int
            case "Scales":
                set_common_values([0, 2, 4, 5, 7, 9, 11], "Enharmonic")
            case "Triads" | "Sevenths" | "Modes" | "Shells":
                set_common_values(range(12), "Enharmonic")
                if self.theorymode in ["Triads", "Sevenths"]:self.inv = random.choice(self.theory3list)

    def reset_scale(self):
        if hasattr(self, 'deepnotes') and self.deepnotes: self.required_notes = copy.deepcopy(self.deepnotes)
    def increment_score(self, points=1):
        self.score += points
        self.score_value.setText(f"Score: {self.score}")
    def decrement_score(self, points=1):
        self.score -= points
        self.score_value.setText(f"Score: {self.score}")
    def announce_scale(self, scale_name):
        file_path = f"/Users/williamcorney/PycharmProjects/Oralia5/sounds/{scale_name}.mp3"
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.set_volume(0.1)
        pygame.mixer.music.play()
    def populate_labels(self, values_dict):
        items = [f"{key}: {value}" for key, value in values_dict.items()]
        for i, label in enumerate(self.labels):
            if i < len(items): label.setText(items[i])
            else: label.setText("")

    def clear_labels(self):
        for label in self.labels:
            label.setText("")


    def result_pixmap(self,label):
        self.fingering_label.setPixmap(QPixmap(f"/Users/williamcorney/PycharmProjects/Oralia5/Images/{label}.png"))
if __name__ == "__main__":
    import Oralia
    oralia.main()
