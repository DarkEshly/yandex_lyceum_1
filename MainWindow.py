import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QColor
from Canva import Canva


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('MainWindow.ui', self)
        self.frame = QLabel(self)  # создаём холст
        fr = QPixmap('sprites/frame.jpg')
        fr = fr.scaledToWidth(600)
        fr = fr.scaledToHeight(600)
        self.frame.setPixmap(fr)
        self.frame.move(150, 150)
        self.frame.resize(600, 600)
        self.canva_now = Canva(self)
        self.canva_now.resize(500, 500)
        self.canva_now.move(200, 200)
        self.first_color_slot.clicked.connect(self.choose_color)  # привязываем события
        self.second_color_slot.clicked.connect(self.choose_color)
        self.first_color_slot.setStyleSheet("background-color: {}".format(QColor(0, 0, 0).name()))
        self.second_color_slot.setStyleSheet("background-color: {}".format(QColor(255, 255, 255).name()))
        self.tools_actions = [self.rubber_action, self.pencil_action, self.ellipse_action, self.triangle_action,
                              self.line_action, self.rectangle_action, self.star_action, self.spray_action,
                              self.dropper_action, self.fill_action, self.hexagon_action, self.polygon_action,
                              self.select_action]
        for action in self.tools_actions:
            action.triggered.connect(self.change_tool)
        self.widthValue.currentTextChanged.connect(self.change_width_of_pen)
        self.fill_box.clicked.connect(self.change_filling)
        self.go_back_button.clicked.connect(self.change_number_of_canva)
        self.go_forward_button.clicked.connect(self.change_number_of_canva)
        self.clean_action.triggered.connect(self.to_clean)
        self.go_back_button.setEnabled(False)
        self.go_forward_button.setEnabled(False)
        self.save_action.triggered.connect(self.save_image)
        self.load_action.triggered.connect(self.load_image)
        self.exit_action.triggered.connect(self.to_exit)
        self.shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.shortcut.activated.connect(self.save_copy)

    def set_menu(self, menu):  # запоминаем объект MainMenu
        self.menu = menu

    def closeEvent(self, event):  # если нажали на крестик, то выполняем функцию to_exit
        self.to_exit(from_event=event)

    def to_exit(self, from_event=None):  # предлагаем сохранить картинку перед выходом из приложения
        msg = QMessageBox(self)
        msg.setWindowTitle("Выход")
        msg.setText('Вы хотите сохранить картинку перед выходом?')
        msg.addButton(QMessageBox.Yes)
        msg.addButton(QMessageBox.No)
        msg.addButton(QMessageBox.Cancel)
        reply = msg.exec_()
        if reply == QMessageBox.Yes:
            self.save_image()
        if reply != QMessageBox.Yes and reply != QMessageBox.No:
            if from_event:
                from_event.ignore()
        elif not from_event:
            self.setVisible(False)
            self.menu.setVisible(True)

    def to_clean(self):  # функция очистки
        self.canva_now.clean()

    def change_number_of_canva(self):  # функция перемещения между состояниями холста
        self.canva_now.to_null_select()
        self.canva_now.to_finish_polygon(from_click=False)
        if self.sender() == self.go_back_button:
            self.canva_now.go_back()
        else:
            self.canva_now.go_forward()

    def choose_color(self, from_canva=False, canva_color=None, number=None):  # изменение цвета
        if not from_canva:
            color = QColorDialog.getColor()
            self.sender().setStyleSheet(
                "background-color: {}".format(color.name()))
            if self.sender() == self.first_color_slot:
                self.canva_now.set_color(color, 1)
            else:
                self.canva_now.set_color(color, 2)
        else:
            if number == 1:
                self.first_color_slot.setStyleSheet(
                    "background-color: {}".format(QColor(canva_color).name()))
            else:
                self.second_color_slot.setStyleSheet(
                    "background-color: {}".format(QColor(canva_color).name()))

    def change_tool(self):  # изменения инструмента
        self.fill_box.setEnabled(False)
        if self.sender().isChecked():
            if self.sender() in [self.triangle_action, self.rectangle_action, self.ellipse_action, self.star_action,
                                 self.hexagon_action, self.polygon_action]:
                self.fill_box.setEnabled(True)  # открываем возможность заливки если фигура
            for action in self.tools_actions:
                action.setChecked(False)
            if self.sender() == self.rubber_action:
                self.canva_now.change_state('rubber')
                self.rubber_action.setChecked(True)
            elif self.sender() == self.pencil_action:
                self.canva_now.change_state('pencil')
                self.pencil_action.setChecked(True)
            elif self.sender() == self.spray_action:
                self.spray_action.setChecked(True)
                self.canva_now.change_state('spray')
            elif self.sender() == self.ellipse_action:
                self.ellipse_action.setChecked(True)
                self.canva_now.change_state('ellipse')
            elif self.sender() == self.rectangle_action:
                self.rectangle_action.setChecked(True)
                self.canva_now.change_state('rectangle')
            elif self.sender() == self.triangle_action:
                self.triangle_action.setChecked(True)
                self.canva_now.change_state('triangle')
            elif self.sender() == self.line_action:
                self.line_action.setChecked(True)
                self.canva_now.change_state('line')
            elif self.sender() == self.star_action:
                self.star_action.setChecked(True)
                self.canva_now.change_state('star')
            elif self.sender() == self.fill_action:
                self.fill_action.setChecked(True)
                self.canva_now.change_state('fill')
            elif self.sender() == self.dropper_action:
                self.dropper_action.setChecked(True)
                self.canva_now.change_state('dropper')
            elif self.sender() == self.hexagon_action:
                self.hexagon_action.setChecked(True)
                self.canva_now.change_state('hexagon')
            elif self.sender() == self.polygon_action:
                self.polygon_action.setChecked(True)
                self.canva_now.change_state('polygon')
            elif self.sender() == self.select_action:
                self.select_action.setChecked(True)
                self.canva_now.change_state('selection')
        else:
            self.canva_now.change_state(None)

    def change_width_of_pen(self):  # изменяем толщину пера
        self.canva_now.change_width(int(self.widthValue.currentText()))

    def change_filling(self):  # изменить применение заливки фигуры
        self.canva_now.set_fill(self.sender().isChecked())

    def save_image(self):  # сохранение изображения
        self.canva_now.to_null_select()
        self.canva_now.to_finish_polygon(from_click=False)
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image",
                                                   "", "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
        format = file_name[file_name.rfind('.') + 1:]
        to_save = True
        picture = self.canva_now.pixmap()
        if format == 'png':
            is_transparent, ok_pressed = QInputDialog.getItem(
                self, "формат png", "Будете ли вы сохранять в формате png с прозрачным фоном?",
                ("Да", "Нет"), 1, False)
            if not ok_pressed:
                to_save = False
            if is_transparent == 'Да':  # если выбрано да создаём прозрачный фон
                picture = self.canva_now.convert_to_transparent()
        if file_name != "" and to_save:
            picture.save(file_name)

    def load_image(self):  # загрузка изображения
        self.canva_now.to_null_select()
        self.canva_now.to_finish_polygon(from_click=False)
        file_name = QFileDialog.getOpenFileName(self, 'Выберите картинку',
                                                '', 'PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ')[0]
        if file_name != '':
            self.canva_now.set_image(file_name)

    def save_copy(self):  # вызываем функцию холста, сохраняющую выделенную область в буфер обмена
        self.canva_now.save_selected_area()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainForm()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())
