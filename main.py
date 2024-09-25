import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
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
        self.game_over = False


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

    def is_five(self, row, col, color):
        """Проверяет, есть ли 5 одинаковых кружков подряд"""
        directions = [
            (1, 0),  # горизонталь
            (0, 1),  # вертикаль
            (1, 1),  # диагональ (вниз вправо)
            (1, -1)  # диагональ (вниз влево)
        ]

        for dr, dc in directions:
            count = 1  # Включаем текущий кружок
            # Проверяем в одну сторону
            r = row + dr
            c = col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == color:
                count += 1
                r += dr
                c += dc

            # Проверяем в другую сторону
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc

            if count >= 5:
                return True

        return False

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
        if self.game_over:   # Если игра завершена, не обрабатываем больше кликов
            return
        
        x = event.position().x()
        y = event.position().y()

        # Определяем, в какую клетку был клик
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        if self.board[row][col] is None:  # Если клетка пуста, ставим отметку
            # Добавляем центр клетки в список кружков
            self.circles.append((col * self.cell_size + 5, row * self.cell_size + 5, self.ball_color))
            self.board[row][col] = self.ball_color  # Обозначаем, что в этой клетке уже есть круг

            if self.is_five(row, col, self.ball_color):  # Проверяем, есть ли 5 в ряд
                self.game_over = True
                self.show_game_over_message(self.ball_color)

            # Меняем цвет для следующего круга
            if self.ball_color == 'white':
                self.ball_color = 'black'
            else:
                self.ball_color = 'white'

            self.update()

    def show_game_over_message(self, winner):
        """Показываем сообщение о завершении игры"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Игра завершена")
        msg_box.setText(f"Игра завершена! Победили {winner}.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()  # Ожидаем нажатия кнопки "ОК"


app = QApplication([])
window = MyWindow()
window.show()
app.exec()
