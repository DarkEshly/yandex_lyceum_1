import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from MainWindow import MainForm


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Main.ui', self)
        pixmap = QPixmap('sprites/menu.jpg')
        pixmap = pixmap.scaled(1500, 1000)
        self.image = QLabel(self)
        self.image.setPixmap(pixmap)
        self.image.resize(1500, 1000)
        self.resize(1500, 1000)
        self.button = QPushButton('START', self.image)
        self.button.move(700, 700)
        self.button.resize(100, 50)
        self.button.clicked.connect(self.to_start)
        self.exit_button = QPushButton('EXIT', self.image)
        self.exit_button.clicked.connect(self.to_exit)
        self.exit_button.resize(100, 50)
        self.exit_button.move(700, 800)

    def to_start(self):  # переход в основное окно программы
        self.main_window = MainForm()
        self.main_window.set_menu(self)
        self.setVisible(False)
        self.main_window.setVisible(True)

    def to_exit(self):  # закрытие программы
        QApplication.quit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenu()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
