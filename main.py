import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPainter, QPen , QBrush, QColor
from PyQt6.QtCore import Qt, QPoint


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Рендзю")
        self.setFixedSize(600, 600)

        self.board_size = 15  # Размер поля 15x15
        self.cell_size = 40  # Размер одной клетки
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]  # Игровое поле

        self.circles = []   # Список для хранения координат кружков
        self.ball_color = 'white'


    def paintEvent(self, event):

        self.setStyleSheet("background-color: rgb(255, 250, 205);")
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.black, 3)
        painter.setPen(pen)

        # Рисуем линии
        x = 20
        y = 20
        while x <= 600:
            painter.drawLine(0, y, 600, y)
            painter.drawLine(x, 0, x, 600)
            x += 40
            y += 40

        # Рисуем кружки
        for circle in self.circles:
            self.draw_ball(painter, circle[0], circle[1], circle[2])

    def draw_ball(self, painter, x, y, color):
        """Рисует черный или белый круг"""
        if color == 'white': 
            painter.setBrush(QBrush(QColor(255, 255, 255))) 
        else: 
            painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.PenStyle.NoPen)  # Убираем границу круга
        painter.drawEllipse(x, y, 30, 30)

    def mousePressEvent(self, event):
        """Обрабатываем клик мыши"""
        x = event.position().x()
        y = event.position().y()

        # Определяем, в какую клетку был клик
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        if self.board[row][col] is None:  # Если клетка пуста, ставим отметку
            # Добавляем центр клетки в список кружков
            self.circles.append((col * self.cell_size + 5, row * self.cell_size + 5, self.ball_color))
            self.board[row][col] = self.ball_color  # Обозначаем, что в этой клетке уже есть круг

            if self.ball_color == 'white':
                self.ball_color = 'black'
            else:
                self.ball_color = 'white'

            self.update() 

            

app = QApplication([])
window = MyWindow()
window.show()
app.exec()
