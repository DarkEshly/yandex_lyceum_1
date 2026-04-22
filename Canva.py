import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPainter, QPen, QColor
import random
from PIL import Image
from PIL.ImageQt import ImageQt


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


def cross_point(first_points, second_points):  # функция вычисления точек для звезды
    y1 = first_points[0][1]
    y2 = first_points[1][1]
    x1 = first_points[0][0]
    x2 = first_points[1][0]
    if x1 - x2 == 0:
        first_k = 0
    else:
        first_k = (y1 - y2) / (x1 - x2)
    first_b = y2 - first_k * x2
    y1 = second_points[0][1]
    y2 = second_points[1][1]
    x1 = second_points[0][0]
    x2 = second_points[1][0]
    if x1 - x2 == 0:
        second_k = 0
    else:
        second_k = (y1 - y2) / (x1 - x2)
    second_b = y2 - second_k * x2
    x = (second_b - first_b) // (first_k - second_k)
    y = x * first_k + first_b
    a = (x, y)
    return a


def get_pixel(x, y, im, w):  # функция получения значения пикселя
    i = (x + (y * w)) * 4
    return im[i:i + 4]


class Canva(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent_form = args[0]
        self.canvas = QPixmap(500, 500)  # создание pixmap для холста
        self.canvas.fill(QColor(255, 255, 255))
        self.setPixmap(self.canvas)
        self.first_color = QColor(0, 0, 0)  # обозначение цветов
        self.second_color = QColor(255, 255, 255)
        self.state = None  # обозначение состояния
        self.last_canva = self.pixmap().copy()  # последнее состояние
        self.width = 1  # толщина
        self.brush_color = False  # заливаем ли мы фигуру или нет
        self.states_of_canva = [self.pixmap().copy()]  # состояния холста
        self.current_number_of_canva = 0  # наш номер холста
        self.polygon_points = []  # точки полигона
        self.dont_do_it_please = False
        self.selected_area = None  # выбранная область
        self.selected_coords = [-1, -1, -1, -1]
        self.is_selected = False  # выбрана ли область
        self.helpy_canva = None
        self.first_select = True  # выделено, без перемещения
        self.first_select_coords = [-1, -1]  # первые координаты выделенной части

    def set_image(self, file_name):  # загрузка изображения
        self.a = Image.open(file_name)
        size = [self.size().width(), self.size().height()]
        self.a = self.a.copy()
        if size[0] - 1 <= self.a.size[0] or size[1] - 1 <= self.a.size[1]:  # подгоняем изображение под холст
            coefficient_0 = size[0] / self.a.size[0]
            coefficient_1 = size[1] / self.a.size[1]
            if coefficient_1 < coefficient_0:
                coefficient = coefficient_1
            else:
                coefficient = coefficient_0
            self.a = self.a.resize((int(self.a.size[0] * coefficient), int(self.a.size[1] * coefficient)))
        self.a = ImageQt(self.a)
        self.setPixmap(QPixmap.fromImage(self.a))
        our_image = self.pixmap().copy()
        help_pixmap = QPixmap(self.size().width(), self.size().height())
        help_pixmap.fill(QColor(255, 255, 255))  # создаём белую картинку, на которую накладываем наше изображение
        self.painter = QPainter(help_pixmap)
        self.painter.drawPixmap(0, 0, our_image)
        self.painter.end()
        self.setPixmap(help_pixmap)
        self.last_canva = self.pixmap().copy()
        if self.current_number_of_canva != len(self.states_of_canva) - 1:
            self.states_of_canva = self.states_of_canva[:self.current_number_of_canva + 1]
            self.current_number_of_canva = len(self.states_of_canva) - 1
        if self.states_of_canva[-1].toImage() != self.pixmap().copy().toImage():
            self.states_of_canva.append(self.pixmap().copy())
            if len(self.states_of_canva) > 10:
                del self.states_of_canva[0]
            else:
                self.current_number_of_canva = self.current_number_of_canva + 1
        if self.current_number_of_canva != 0:
            self.parent_form.go_back_button.setEnabled(True)
        self.parent_form.go_forward_button.setEnabled(False)

    def mousePressEvent(self, event):  # обработка нажатия мыши
        self.last_x = event.x()  # сохраняем последние координаты
        self.last_y = event.y()
        if (event.x() < self.selected_coords[0] or event.y() < self.selected_coords[1] or
            event.x() > self.selected_coords[0] + self.selected_coords[2] or
            event.y() > self.selected_coords[1] + self.selected_coords[3]) and \
                (self.selected_coords[0] != -1 and self.selected_coords[1] != -1):  # если нажали не в выбранной области
            self.to_null_select(from_click=True)
        if self.state == self.dropper:  # если пипетка то используем
            self.state(event.x(), event.y(), event.button())
        elif self.state == self.fill:  # если заливка то используем
            self.state(event.x(), event.y())
        if self.state == self.draw_polygon:  # рисуем полигон при нажатии если уже создан иначе добавляем первую точку
            if not self.polygon_points:
                self.polygon_points.append((event.x(), event.y()))
            else:
                self.draw_polygon(event.x(), event.y())

    def mouseMoveEvent(self, event):  # события передвижения мыши выполняем текущую функцию
        if self.state and self.state != self.dropper and self.state != self.fill:
            self.state(event.x(), event.y())

    def mouseReleaseEvent(self, event):  # события отпускания мыши
        if self.selected_area is not None:  # активируем выделение если есть выделенная область
            self.is_selected = True
        if self.selected_area is None:  # если нет выделенной области сохраняем последний холст
            self.last_canva = self.pixmap().copy()
        elif self.helpy_canva is not None:  # сохраняем новые координаты выделенной области
            self.selected_coords[0] = self.selected_coords[0] + event.x() - self.last_x
            self.selected_coords[1] = self.selected_coords[1] + event.y() - self.last_y
        if self.current_number_of_canva != len(
                self.states_of_canva) - 1 and self.state != self.dropper and self.state is not None and \
                (self.state == self.to_select and not self.first_select):
            self.states_of_canva = self.states_of_canva[:self.current_number_of_canva + 1]  # удаляем все состояния
            self.current_number_of_canva = len(self.states_of_canva) - 1  # что впереди
            self.parent_form.go_forward_button.setEnabled(False)
        if self.last_canva.toImage() != self.states_of_canva[-1].toImage() and self.state != self.dropper and \
                self.state is not None:
            self.parent_form.go_forward_button.setEnabled(False)
            if (self.state != self.draw_polygon or self.polygon_points == 0) and (
                    self.state != self.to_select or not self.is_selected):  # если не рисуем по-
                self.states_of_canva.append(self.last_canva)  # лигон и нету выделенной области то прибавляем состояние
                if len(self.states_of_canva) > 10:
                    del self.states_of_canva[0]
                else:
                    self.current_number_of_canva = self.current_number_of_canva + 1
        if self.current_number_of_canva != 0:  # ключаем кнопку перемещения назад только если не на первом холсте
            self.parent_form.go_back_button.setEnabled(True)
        if not self.dont_do_it_please:
            if self.polygon_points:
                x = self.polygon_points[0][0]  # если есть точки то берём координаты начала многоугольника
                y = self.polygon_points[0][1]
            else:
                x = None  # если нет то приравниваем к ничему
                y = None
            if x == event.x() and y == event.y():  # если координаты отрыва равны координатам начала
                self.mouseDoubleClickEvent(event)  # многоугольника то строим его двойным кликом
            elif self.state == self.draw_polygon:  # иначе прибавляем точки в многоугольник
                self.polygon_points.append((event.x(), event.y()))
        else:  # если мы не прошли первый раз по клику то теперь разрешаем проход
            self.dont_do_it_please = False

    def set_color(self, color, slot):  # меняем цвет
        if slot == 1:
            self.first_color = QColor(color)
        else:
            self.second_color = QColor(color)

    def pencil(self, x, y):  # функция карандаша
        self.painter = QPainter(self.pixmap())
        pen = QPen(QColor(self.first_color), self.width)
        self.painter.setPen(pen)
        self.painter.drawLine(self.last_x, self.last_y, x, y)
        self.last_x = x
        self.last_y = y
        self.painter.end()
        self.update()

    def rubber(self, x, y):  # функция ластика
        self.painter = QPainter(self.pixmap())
        pen = QPen(QColor(self.second_color), self.width * 2)
        self.painter.setPen(pen)
        self.painter.drawLine(self.last_x, self.last_y, x, y)
        self.last_x = x
        self.last_y = y
        self.painter.end()
        self.update()

    def draw_ellipse(self, x, y):  # функция эллипса
        a = self.last_canva.copy()
        self.painter = QPainter(a)
        if self.last_x != x or self.last_y != y:
            pen = QPen(QColor(self.first_color), self.width)
            self.painter.setPen(pen)
            if self.brush_color:
                self.painter.setBrush(self.second_color)
            self.painter.drawEllipse(self.last_x, self.last_y, x - self.last_x, y - self.last_y)
            self.setPixmap(a)
        self.painter.end()
        self.update()

    def draw_rectangle(self, x, y):  # функция прямоугольника
        a = self.last_canva.copy()
        self.painter = QPainter(a)
        if self.last_x != x or self.last_y != y:
            pen = QPen(QColor(self.first_color), self.width)
            self.painter.setPen(pen)
            if self.brush_color:
                self.painter.setBrush(self.second_color)
            self.painter.drawRect(self.last_x, self.last_y, x - self.last_x, y - self.last_y)
            self.setPixmap(a)
        self.painter.end()
        self.update()

    def draw_line(self, x, y):  # функция линия
        a = self.last_canva.copy()
        self.painter = QPainter(a)
        if self.last_x != x or self.last_y != y:
            pen = QPen(QColor(self.first_color), self.width)
            self.painter.setPen(pen)
            self.painter.drawLine(self.last_x, self.last_y, x, y)
            self.setPixmap(a)
        self.painter.end()
        self.update()

    def draw_triangle(self, x, y):  # функция треугольника
        a = self.last_canva.copy()
        self.painter = QPainter(a)
        if self.last_x != x or self.last_y != y:
            pen = QPen(QColor(self.first_color), self.width)
            if self.brush_color:
                self.painter.setBrush(self.second_color)
            self.painter.setPen(pen)
            self.painter.drawPolygon(QPoint(self.last_x, y), QPoint(self.last_x + (x - self.last_x) // 2, self.last_y),
                                     QPoint(x, y))
            self.setPixmap(a)
        self.painter.end()
        self.update()

    def spray(self, x, y):  # функция спрея
        self.painter = QPainter(self.pixmap())
        pen = QPen(self.first_color, 1)
        self.painter.setPen(pen)
        for n in range(100):
            x_random = random.gauss(0, self.width * 5)
            y_random = random.gauss(0, self.width * 5)
            self.painter.drawPoint(x + x_random, y + y_random)
        self.painter.end()
        self.update()

    def set_fill(self, to_fill):  # функция установки заливки
        self.brush_color = to_fill

    def draw_star(self, x, y):  # функция звезды
        if self.last_x != x or self.last_y != y:
            try:
                a = self.last_canva.copy()
                self.painter = QPainter(a)
                pen = QPen(QColor(self.first_color), self.width)
                if self.brush_color:
                    self.painter.setBrush(self.second_color)
                self.painter.setPen(pen)
                first_point = (self.last_x, self.last_y + int(0.37 * (y - self.last_y)))
                third_point = (self.last_x + ((x - self.last_x) // 2), self.last_y)
                fifth_point = (x, self.last_y + int(0.37 * (y - self.last_y)))
                seventh_point = (x - (int(0.21 * (x - self.last_x))), y)
                ninth_point = (self.last_x + (int(0.21 * (x - self.last_x))), y)
                second_point = cross_point((first_point, fifth_point), (third_point, ninth_point))
                fourth_point = cross_point((first_point, fifth_point), (third_point, seventh_point))
                sixth_point = cross_point((ninth_point, fifth_point), (third_point, seventh_point))
                eigth_point = cross_point((ninth_point, fifth_point), (first_point, seventh_point))
                tenth_point = cross_point((ninth_point, third_point), (first_point, seventh_point))
                self.painter.drawPolygon(QPoint(*first_point), QPoint(*second_point), QPoint(*third_point),
                                         QPoint(*fourth_point), QPoint(*fifth_point),
                                         QPoint(*sixth_point), QPoint(*seventh_point), QPoint(*eigth_point),
                                         QPoint(*ninth_point),
                                         QPoint(*tenth_point))
                self.setPixmap(a)
                self.painter.end()
                self.update()
            except ZeroDivisionError:  # если есть деление на ноль в точках рисуем линию
                self.draw_line(x, y)

    def change_width(self, width):  # изменяем толщину
        self.width = width
        pass

    def change_state(self, state):  # меняем состояние
        self.setCursor(Qt.ArrowCursor)
        if self.state == self.draw_polygon and state != 'polygon':
            self.to_finish_polygon(from_click=False)  # дорисовываем многоугольник
        if state == 'pencil':
            cursor_icon = QPixmap('sprites/pencil.png').scaled(20, 20)
            cursor = QCursor(cursor_icon)
            self.setCursor(cursor)
            self.state = self.pencil
        elif state == 'rubber':
            cursor_icon = QPixmap('sprites/rubber.png').scaled(20, 20)
            cursor = QCursor(cursor_icon)
            self.setCursor(cursor)
            self.state = self.rubber
        elif state == 'ellipse':
            self.state = self.draw_ellipse
        elif state == 'rectangle':
            self.state = self.draw_rectangle
        elif state == 'line':
            self.state = self.draw_line
        elif state == 'triangle':
            self.state = self.draw_triangle
        elif state == 'spray':
            cursor_icon = QPixmap('sprites/spray_cursor.png').scaled(20, 20)
            cursor = QCursor(cursor_icon)
            self.setCursor(cursor)
            self.state = self.spray
        elif state == 'dropper':
            cursor_icon = QPixmap('sprites/dropper_cursor.png').scaled(20, 20)
            cursor = QCursor(cursor_icon)
            self.setCursor(cursor)
            self.state = self.dropper
        elif state == 'fill':
            cursor_icon = QPixmap('sprites/fill_cursor.png').scaled(20, 20)
            cursor = QCursor(cursor_icon)
            self.setCursor(cursor)
            self.state = self.fill
        elif state == 'star':
            self.state = self.draw_star
        elif state == 'hexagon':
            self.state = self.draw_hexagon
        elif state == 'polygon':
            self.state = self.draw_polygon
            self.polygon_points = []
        elif state == 'selection':
            self.selected_area = None
            self.state = self.to_select
        elif state is None:
            self.state = None
        if self.state != self.to_select:
            self.to_null_select()

    def mouseDoubleClickEvent(self, event):  # при двойно щелчке рисуем многоугольник
        self.to_finish_polygon()

    def to_finish_polygon(self, from_click=True):  # функция завершения рисования многоугольника
        if self.state == self.draw_polygon and self.polygon_points:
            self.draw_polygon(None, None, full=True)
            self.polygon_points = []
            if not from_click:
                self.last_canva = self.pixmap().copy()
                self.states_of_canva.append(self.last_canva)
                if len(self.states_of_canva) > 10:
                    del self.states_of_canva[0]
                else:
                    self.current_number_of_canva = self.current_number_of_canva + 1
            else:
                self.dont_do_it_please = True

    def dropper(self, x, y, button):  # пипетка
        if button == Qt.LeftButton:
            number = 1
        else:
            number = 2
        self.set_color(self.pixmap().toImage().pixel(x, y), number)
        self.parent_form.choose_color(True, QColor(self.pixmap().toImage().pixel(x, y)), number)

    def fill(self, x, y):  # заливка
        image = self.pixmap().toImage()
        w, h = image.width(), image.height()
        im = image.bits().asstring(w * h * 4)
        self.painter = QPainter(self.pixmap())
        pen = QPen(QColor(self.first_color))
        self.painter.setPen(pen)
        i = (x + (y * w)) * 4
        need_color = im[i:i + 4]
        filled_pixels = set()
        all_points = [(x, y)]

        def get_points(center_pos):  # функция получения центральных точек
            points = []
            center_x, center_y = center_pos
            for x, y in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                x1, y1 = center_x + x, center_y + y
                if 0 <= x1 < w and 0 <= y1 < h and (x1, y1) not in filled_pixels:
                    points.append((x1, y1))
                    filled_pixels.add((x1, y1))
            return points

        while all_points:  # пока есть точки закрашиваем их
            x, y = all_points.pop()
            if get_pixel(x, y, im, w) == need_color:
                self.painter.drawPoint(QPoint(x, y))
                all_points.extend(get_points((x, y)))
        self.painter.end()
        self.update()

    def go_back(self):  # функция возвращения в предыдущее состояние
        if len(self.polygon_points) != 0:
            self.draw_polygon(None, None, full=True)
        if self.current_number_of_canva - 1 <= 0:
            self.parent_form.go_back_button.setEnabled(False)
        if self.current_number_of_canva - 1 >= 0:
            self.current_number_of_canva = self.current_number_of_canva - 1
            self.parent_form.go_forward_button.setEnabled(True)
            self.setPixmap(self.states_of_canva[self.current_number_of_canva])
            self.last_canva = self.states_of_canva[self.current_number_of_canva].copy()
            self.polygon_points = []

    def go_forward(self):  # функция перемещения вперёд на состояние
        if self.current_number_of_canva + 1 >= len(self.states_of_canva) - 1:
            self.parent_form.go_forward_button.setEnabled(False)
        if self.current_number_of_canva + 1 <= len(self.states_of_canva) - 1:
            self.current_number_of_canva = self.current_number_of_canva + 1
            self.parent_form.go_back_button.setEnabled(True)
            self.last_canva = self.states_of_canva[self.current_number_of_canva].copy()
            self.setPixmap(self.states_of_canva[self.current_number_of_canva])

    def clean(self):  # функция очистки
        self.to_null_select()
        self.to_finish_polygon(from_click=False)
        new_canva = QPixmap(self.size().width(), self.size().height())
        new_canva.fill(QColor(self.second_color))
        self.setPixmap(new_canva)
        self.last_canva = self.pixmap().copy()
        if self.current_number_of_canva != len(self.states_of_canva) - 1:
            self.states_of_canva = self.states_of_canva[:self.current_number_of_canva + 1]
            self.current_number_of_canva = len(self.states_of_canva) - 1
        if self.states_of_canva[-1].toImage() != self.pixmap().copy().toImage():
            self.states_of_canva.append(self.pixmap().copy())
            if len(self.states_of_canva) > 10:
                del self.states_of_canva[0]
            else:
                self.current_number_of_canva = self.current_number_of_canva + 1
        if self.current_number_of_canva != 0:
            self.parent_form.go_back_button.setEnabled(True)
        self.parent_form.go_forward_button.setEnabled(False)

    def draw_hexagon(self, x, y):  # рисуем пятиугольник
        a = self.last_canva.copy()
        self.painter = QPainter(a)
        if self.last_x != x or self.last_y != y:
            pen = QPen(QColor(self.first_color), self.width)
            if self.brush_color:
                self.painter.setBrush(self.second_color)
            self.painter.setPen(pen)
            first_point = (self.last_x, y - int(0.25 * (y - self.last_y)))
            second_point = (self.last_x, self.last_y + int(0.25 * (y - self.last_y)))
            third_point = (self.last_x + ((x - self.last_x) // 2), self.last_y)
            fourth_point = (x, self.last_y + int(0.25 * (y - self.last_y)))
            fifth_point = (x, y - int(0.25 * (y - self.last_y)))
            sixth_point = (self.last_x + ((x - self.last_x) // 2), y)
            self.painter.drawPolygon(QPoint(*first_point), QPoint(*second_point), QPoint(*third_point),
                                     QPoint(*fourth_point), QPoint(*fifth_point), QPoint(*sixth_point))
            self.setPixmap(a)
        self.painter.end()
        self.update()

    def draw_polygon(self, x, y, full=False):
        if not full:  # рисуем продолжение многоугольника если не полный
            if len(self.polygon_points) == 1:
                self.draw_line(x, y)
            elif len(self.polygon_points) != 0:
                a = self.last_canva.copy()
                self.painter = QPainter(a)
                if self.polygon_points[-1][0] != x or self.polygon_points[-1][1] != y:
                    pen = QPen(QColor(self.first_color), self.width)
                    self.painter.setPen(pen)
                    self.painter.drawLine(self.polygon_points[-1][0], self.polygon_points[-1][1], x, y)
                    self.setPixmap(a)
                self.painter.end()
                self.update()
        elif self.polygon_points:  # рисуем полный многоугольник
            self.painter = QPainter(self.pixmap())
            if self.brush_color:
                self.painter.setBrush(QColor(self.second_color))
            pen = QPen(QColor(self.first_color), self.width)
            self.painter.setPen(pen)
            for i in range(len(self.polygon_points)):
                self.polygon_points[i] = QPoint(self.polygon_points[i][0], self.polygon_points[i][1])
            self.painter.drawPolygon(*self.polygon_points)
            self.painter.end()
            self.update()

    def to_select(self, x, y):  # выделение
        if not self.is_selected:  # если не выделенно до конца создаём область выделения
            b = self.last_canva.copy()
            self.painter = QPainter(b)
            if self.last_x != x or self.last_y != y:
                pen = QPen(QColor(0, 0, 0), 1, Qt.DotLine)
                self.painter.setPen(pen)
                self.painter.drawRect(self.last_x, self.last_y, x - self.last_x, y - self.last_y)
                self.setPixmap(b)
                self.selected_area = self.last_canva.copy(self.last_x,
                                                          self.last_y,
                                                          x - self.last_x,
                                                          y - self.last_y)
                self.selected_coords = [self.last_x, self.last_y, x - self.last_x, y - self.last_y]
                self.first_select_coords = [self.last_x, self.last_y]
            self.painter.end()
            self.update()

        elif self.selected_area is not None:  # если есть выбранная область и выделено перемещаем область
            self.first_select = False
            a = self.last_canva.copy()
            self.painter = QPainter(a)
            delta_x = x - self.last_x
            delta_y = y - self.last_y
            self.painter.setBrush(self.second_color)
            self.painter.setPen(self.second_color)
            self.painter.drawRect(self.first_select_coords[0], self.first_select_coords[1],
                                  self.selected_coords[2], self.selected_coords[3])
            self.painter.drawPixmap(self.selected_coords[0] + delta_x,
                                    self.selected_coords[1] + delta_y, self.selected_area)
            self.helpy_canva = a.copy()
            self.painter.end()
            self.painter = QPainter(a)
            pen = QPen(QColor(0, 0, 0), 1, Qt.DotLine)
            self.painter.setPen(pen)
            self.painter.drawRect(self.selected_coords[0] + delta_x,
                                  self.selected_coords[1] + delta_y, self.selected_coords[2], self.selected_coords[3])
            self.setPixmap(a)
            self.painter.end()
            self.update()

    def save_selected_area(self):  # сохранение выделенной области в буфер обмена
        if self.selected_area:
            c = QApplication.clipboard()
            c.setImage(QImage(self.selected_area))

    def convert_to_transparent(self):  # функция создающая прозрачный фон
        transparent_canva = QPixmap(self.size().width(), self.size().height())
        transparent_canva.fill(Qt.transparent)
        self.painter = QPainter(transparent_canva)
        help_painter = QPainter(self.pixmap())
        help_painter.setPen(QColor(self.second_color))
        last_color = QColor(self.pixmap().toImage().pixel(0, 0))
        help_painter.drawPoint(0, 0)
        image = self.pixmap().toImage()
        w, h = image.width(), image.height()
        im = image.bits().asstring(w * h * 4)
        need_color = im[0:0 + 4]
        help_painter.setPen(last_color)
        help_painter.drawPoint(0, 0)
        for j in range(w):
            for k in range(h):
                if get_pixel(j, k, im, w) != need_color:
                    self.painter.setPen(QColor(image.pixel(j, k)))
                    self.painter.drawPoint(j, k)
        self.painter.end()
        help_painter.end()
        return transparent_canva

    def to_null_select(self, from_click=False):  # обнуляем выделение
        self.first_select = True
        if self.selected_area is None:
            from_click = True
        self.selected_area = None  # обнуляем её
        self.selected_coords = [-1, -1, -1, -1]
        self.first_select_coords = [-1, -1]
        if self.helpy_canva:
            self.last_canva = self.helpy_canva.copy()
        self.is_selected = False
        self.setPixmap(self.last_canva.copy())
        self.helpy_canva = None
        if not from_click:
            if self.current_number_of_canva != len(self.states_of_canva) - 1:
                self.states_of_canva = self.states_of_canva[:self.current_number_of_canva + 1]
                self.current_number_of_canva = len(self.states_of_canva) - 1
            if self.states_of_canva[-1].toImage() != self.pixmap().copy().toImage():
                self.states_of_canva.append(self.pixmap().copy())
                if len(self.states_of_canva) > 10:
                    del self.states_of_canva[0]
                else:
                    self.current_number_of_canva = self.current_number_of_canva + 1
            if self.current_number_of_canva != 0:
                self.parent_form.go_back_button.setEnabled(True)
            self.parent_form.go_forward_button.setEnabled(False)
