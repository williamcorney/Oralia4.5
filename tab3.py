from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class Tab3(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        layout = QVBoxLayout(self)
        label = QLabel("This is Tab 3", self)
        layout.addWidget(label)

        self.setLayout(layout)
