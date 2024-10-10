import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor
from PyQt6.QtCore import Qt, QPoint
from enum import Enum
import random

class Color(Enum):
    WHITE = 1
    BLACK = 2

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Рендзю")
        self.setFixedSize(600, 600)

        self.board_size = 15  # Размер поля 15x15
        self.cell_size = 40  # Размер одной клетки
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]  # Игровое поле

        self.ball_color = Color.WHITE
        self.game_over = False
        self.vs_computer = False  # Режим игры: игрок против компьютера

        self.setStyleSheet("background-color: rgb(255, 250, 205);")
        self.select_game_mode()  # Выбор режима игры

    def select_game_mode(self):
        msg_box = QMessageBox(self)
        vs_computer_button = msg_box.addButton("Играть против компьютера", QMessageBox.ButtonRole.AcceptRole)
        vs_player_button = msg_box.addButton("Играть против игрока", QMessageBox.ButtonRole.AcceptRole)
        
        msg_box.setWindowTitle("Выбор режима игры")
        msg_box.exec()

        if msg_box.clickedButton() == vs_computer_button:
            self.vs_computer = True
            self.first_comp_move()  # Компьютер делает первый ход

    def first_comp_move(self):
        """Компьютер делает первый ход в центр"""
        self.board[7][7] = Color.WHITE  # Компьютер ставит белый шар в центр
        self.ball_color = Color.BLACK  # Теперь ход игрока (черный)
        self.update()

    def computer_move(self):
        """Функция, позволяющая компьютеру сделать следующий ход"""
        if self.game_over or not self.vs_computer:  # Если игра завершена или игра не против компьютера
            return

        possible_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] is None]

        last_move = None
        black_block = None
        max_in_row = 0
        best_moves_list = []

        for r, c in possible_moves:
            white_move = self.is_five(r, c, Color.WHITE)
            black_move = self.is_five(r, c, Color.BLACK)

            if white_move >= 5: # ходит, если есть возможность выиграть
                last_move = (r, c)
                break

            if black_move >= 5: # блокирует победу черных
                black_block = (r, c)

            if white_move == max_in_row:
                best_moves_list += [(r, c)]

            elif white_move > max_in_row:
                max_in_row = white_move
                best_moves_list = [(r, c)]

        if not last_move:
            if black_block: # Если найден ход для блокировки чёрных, блокируем
                last_move = black_block

            else:
                last_move = random.choice(best_moves_list)

        row, col = last_move
        self.board[row][col] = Color.WHITE  # Компьютер ставит белую фишку

        # Проверка на победу
        if self.is_five(row, col, Color.WHITE) >= 5:
            self.game_over = True
            self.show_game_over_message(Color.WHITE)

        self.ball_color = Color.BLACK  # Меняем ход на игрока (черный)
        self.update()

    def paintEvent(self, event):

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

        # Рисуем кружки на основе значений в self.board
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is not None:
                    self.draw_ball(painter, col * self.cell_size + 5, row * self.cell_size + 5, self.board[row][col])

    def is_five(self, row, col, color):
        """Считает макс количество кружков подряд"""
        directions = [
            (1, 0),  # горизонталь
            (0, 1),  # вертикаль
            (1, 1),  # диагональ (вниз вправо)
            (1, -1)  # диагональ (вниз влево)
        ]
        score = []

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
            score.append(count)

        return max(score)


    def draw_ball(self, painter, x, y, color):
        """Рисует черный или белый круг"""
        if color == Color.WHITE: 
            painter.setBrush(QBrush(QColor(255, 255, 255))) 
        elif color == Color.BLACK:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.PenStyle.SolidLine)  # Граница белого круга
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
            self.board[row][col] = self.ball_color  # Обозначаем, что в этой клетке уже есть круг

            if self.is_five(row, col, self.ball_color) >= 5:  # Проверяем, есть ли 5 в ряд
                self.game_over = True
                self.show_game_over_message(self.ball_color)
                return  # Завершаем выполнение, чтобы избежать хода компьютера после завершения игры

            # Меняем цвет для следующего круга
            self.ball_color = Color.BLACK if self.ball_color == Color.WHITE else Color.WHITE

            self.update()

            if self.vs_computer and self.ball_color == Color.WHITE and not self.game_over:  # Если играет компьютер, он делает ход
                self.computer_move()

    def keyPressEvent(self, event):
        """Обрабатываем нажатие клавиш"""
        if event.key() == Qt.Key.Key_Escape:  # Если нажата клавиша Escape
            self.show_help_window()

    def show_game_over_message(self, winner):
        """Показываем сообщение о завершении игры"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Игра завершена")
        if self.vs_computer:
            text = "Вы выиграли!" if winner == Color.BLACK else "Вы проиграли :("
            msg_box.setText(text)
        else:
            winner_color = "белые" if winner == Color.WHITE else "чёрные"
            msg_box.setText(f"Победили {winner_color}.")

        msg_box.setStandardButtons(QMessageBox.StandardButton.Retry)
        result = msg_box.exec()  # Ожидаем нажатия кнопки
    
        if result == QMessageBox.StandardButton.Retry:
            self.restart()  # Перезапуск игры при выборе Retry

    def show_help_window(self):
        """Показывает окошко при esc"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Опции")
        msg_box.setText("Вы хотите начать заново?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.restart()

    def restart(self):
        """Перезапуск"""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]  # Игровое поле
        self.game_over = False
        if self.vs_computer:
            self.ball_color = Color.BLACK
            self.first_comp_move()  # Если игра с компьютером, то он делает первый ход
        else:
            self.ball_color = Color.WHITE
        self.update()

app = QApplication([])
window = MyWindow()
window.show()
app.exec()
