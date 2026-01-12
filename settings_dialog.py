from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSpinBox, QCheckBox, QHBoxLayout, QLabel
from db_config import settings

class SettingsDialog(QWidget):
    def __init__(self, parent = ..., flags = ...):
        super().__init__()
        layout  = QVBoxLayout()
        self.setLayout(layout)
        self.setWindowTitle('Ustawienia uzupełniania')

        # verbose
        verbose = QCheckBox('Pokazuj graf')
        verbose.setChecked(settings.verbose)
        verbose.clicked.connect(self.update_verbose)
        layout.addWidget(verbose)

        # pop size
        pop_size = QHBoxLayout()
        pop_size.addWidget(QLabel('Początkowa populacja:'))
        pop_size_spin = QSpinBox(minimum=0, maximum=100_000, value=settings.pop_size)
        pop_size.addWidget(pop_size_spin)
        pop_size_spin.valueChanged.connect(self.update_pop_size)
        layout.addLayout(pop_size)

        # generations
        generations = QHBoxLayout()
        generations.addWidget(QLabel('Liczba pokoleń:'))
        gen_spin = QSpinBox(value=settings.generations)
        generations.addWidget(gen_spin)
        gen_spin.valueChanged.connect(self.update_generations)
        layout.addLayout(generations)

        # cutoff
        cutoff = QHBoxLayout()
        cutoff.addWidget(QLabel('Przeżywalność:'))
        cut_spin = QSpinBox(suffix='%', maximum=100, value=int(settings.cutoff*100))
        cut_spin.valueChanged.connect(self.update_cutoff)
        cutoff.addWidget(cut_spin)
        layout.addLayout(cutoff)

    def update_verbose(self, value):
        settings.verbose = value

    def update_generations(self, value):
        settings.generations = value

    def update_pop_size(self, value):
        settings.pop_size = value

    def update_cutoff(self, value):
        settings.cutoff = value/100