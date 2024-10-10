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

        self.setWindowTitle("Renju")
        self.setFixedSize(600, 600)

        self.board_size = 15  # Board size 15x15
        self.cell_size = 40  # Size of one cell
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]  # Game board

        self.ball_color = Color.WHITE
        self.game_over = False
        self.vs_computer = False  # Game mode: player vs computer

        self.setStyleSheet("background-color: rgb(255, 250, 205);")
        self.select_game_mode()  # Choose game mode

    def select_game_mode(self):
        msg_box = QMessageBox(self)
        vs_computer_button = msg_box.addButton("Play against computer", QMessageBox.ButtonRole.AcceptRole)
        vs_player_button = msg_box.addButton("Play against your friend", QMessageBox.ButtonRole.AcceptRole)
        
        msg_box.setWindowTitle("Choose game mode")
        msg_box.exec()

        if msg_box.clickedButton() == vs_computer_button:
            self.vs_computer = True
            self.first_comp_move()  # Computer makes the first move

    def first_comp_move(self):
        """Computer makes the first move in the center"""
        self.board[7][7] = Color.WHITE  # Computer places a white ball in the center
        self.ball_color = Color.BLACK  # Now it's the player's turn (black)
        self.update()

    def computer_move(self):
        """Allows the computer to make the next move"""
        if self.game_over or not self.vs_computer:  # If the game is over or the game is not against the computer
            return

        possible_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size) if self.board[r][c] is None]

        last_move = None
        black_block = None
        max_in_row = 0
        best_moves_list = []

        for r, c in possible_moves:
            white_move = self.is_five(r, c, Color.WHITE)
            black_move = self.is_five(r, c, Color.BLACK)

            if white_move >= 5: # Move if there is a chance to win
                last_move = (r, c)
                break

            if black_move >= 5: # Block black's win
                black_block = (r, c)

            if white_move == max_in_row:
                best_moves_list += [(r, c)]

            elif white_move > max_in_row:
                max_in_row = white_move
                best_moves_list = [(r, c)]

        if not last_move:
            if black_block: # If a move is found to block black, block it
                last_move = black_block

            else:
                last_move = random.choice(best_moves_list)

        row, col = last_move
        self.board[row][col] = Color.WHITE  # Computer places a white ball

        # Check for victory
        if self.is_five(row, col, Color.WHITE) >= 5:
            self.game_over = True
            self.show_game_over_message(Color.WHITE)

        self.ball_color = Color.BLACK  # Switch turn to the player (black)
        self.update()

    def paintEvent(self, event):

        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.black, 3)
        painter.setPen(pen)

        # Draw lines
        x = 20
        y = 20
        while x <= 600:
            painter.drawLine(0, y, 600, y)
            painter.drawLine(x, 0, x, 600)
            x += 40
            y += 40

        # Draw circles based on the values in self.board
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is not None:
                    self.draw_ball(painter, col * self.cell_size + 5, row * self.cell_size + 5, self.board[row][col])

    def is_five(self, row, col, color):
        """Counts the maximum number of consecutive balls"""
        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal (down-right)
            (1, -1)  # Diagonal (down-left)
        ]
        score = []

        for dr, dc in directions:
            count = 1  # Include the current ball
            # Check one direction
            r = row + dr
            c = col + dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == color:
                count += 1
                r += dr
                c += dc

            # Check the other direction
            r, c = row - dr, col - dc
            while 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == color:
                count += 1
                r -= dr
                c -= dc
            score.append(count)

        return max(score)


    def draw_ball(self, painter, x, y, color):
        """Draws a black or white circle"""
        if color == Color.WHITE: 
            painter.setBrush(QBrush(QColor(255, 255, 255))) 
        elif color == Color.BLACK:
            painter.setBrush(QBrush(QColor(0, 0, 0)))
        painter.setPen(Qt.PenStyle.SolidLine)  # Border of the white circle
        painter.drawEllipse(x, y, 30, 30)

    def mousePressEvent(self, event):
        """Handles mouse click"""

        if self.game_over:   # If the game is over, don't process further clicks
            return
        
        x = event.position().x()
        y = event.position().y()

        # Determine which cell was clicked
        col = int(x // self.cell_size)
        row = int(y // self.cell_size)

        if self.board[row][col] is None:  # If the cell is empty, place a mark
            self.board[row][col] = self.ball_color  # Mark that this cell now has a ball

            if self.is_five(row, col, self.ball_color) >= 5:  # Check if there are 5 in a row
                self.update()
                self.game_over = True
                self.show_game_over_message(self.ball_color)
                return  # End execution to prevent the computer's turn after the game ends

            # Switch color for the next ball
            self.ball_color = Color.BLACK if self.ball_color == Color.WHITE else Color.WHITE

            self.update()

            if self.vs_computer and self.ball_color == Color.WHITE and not self.game_over:  # If playing against the computer, it makes a move
                self.computer_move()

    def keyPressEvent(self, event):
        """Handles key presses"""
        if event.key() == Qt.Key.Key_Escape:  # If the Escape key is pressed
            self.show_help_window()

    def show_game_over_message(self, winner):
        """Displays a message about the end of the game"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Over")
        if self.vs_computer:
            text = "You win!" if winner == Color.BLACK else "You lose :("
            msg_box.setText(text)
        else:
            winner_color = "white" if winner == Color.WHITE else "black"
            msg_box.setText(f"{winner_color.capitalize()} wins.")

        msg_box.setStandardButtons(QMessageBox.StandardButton.Retry)
        result = msg_box.exec()  # Wait for a button to be pressed
    
        if result == QMessageBox.StandardButton.Retry:
            self.restart()  # Restart the game when Retry is chosen

    def show_help_window(self):
        """Shows a window when Esc is pressed"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Options")
        msg_box.setText("Do you want to restart?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg_box.exec()

        if result == QMessageBox.StandardButton.Yes:
            self.restart()

    def restart(self):
        """Restart"""
        self.board = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]  # Game board
        self.game_over = False
        if self.vs_computer:
            self.ball_color = Color.BLACK
            self.first_comp_move()  # If playing against the computer, it makes the first move
        else:
            self.ball_color = Color.WHITE
        self.update()

app = QApplication([])
window = MyWindow()
window.show()
app.exec()
