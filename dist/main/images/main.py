import sys
from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5 import uic
from minesweeper import MinesweeperBoard
import minesweeper
import threading

import sys
import os


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


form = resource_path("main.ui")
form_class = uic.loadUiType(form)[0]


class WindowClass(QMainWindow, form_class):
    difficulty = minesweeper.Difficulty.EASY

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_refresh.clicked.connect(self.refresh_game)

        self.__image_load()

        self.refresh_game()

    def __image_load(self):
        self.number_images = []
        for num in range(9):
            number_pixmap = QPixmap("images/" + str(num) + ".png")
            number_pixmap = number_pixmap.scaled(30, 30)
            self.number_images.append(number_pixmap)

        self.flag_image = QPixmap("images/flagged.png").scaled(30, 30)
        self.bomb_image = QPixmap("images/bomb.png").scaled(30, 30)
        self.boom_image = QPixmap("images/boom.png").scaled(30, 30)

        self.sun_smile_image = QPixmap("images/sun-smile.png").scaled(50, 50)
        self.sun_glasses_image = QPixmap("images/sun-glasses.png").scaled(50, 50)
        self.sun_sad_image = QPixmap("images/sun-sad.png").scaled(50, 50)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.MouseButtonPress:
            if event.button() == QtCore.Qt.LeftButton:
                row = obj.r
                col = obj.c
                self.cell_left_click(row, col)
            elif event.button() == QtCore.Qt.RightButton:
                row = obj.r
                col = obj.c
                self.cell_right_click(row, col)
        return QtCore.QObject.event(obj, event)

    def refresh_btn_image_update(self):
        if self.board.is_cleared():
            self.btn_refresh.setIcon(QIcon(self.sun_glasses_image))
        elif self.board.is_game_over():
            self.btn_refresh.setIcon(QIcon(self.sun_sad_image))
        else:
            self.btn_refresh.setIcon(QIcon(self.sun_smile_image))

    def print_board(self):
        # 상단 영역 출력
        self.refresh_btn_image_update()  # 해 이미지 갱신
        self.lcd_mine_cnt.display(self.board.mine_counter)
        if self.board.is_game_over() or self.board.is_cleared():
            self.timer.stop()

        # 보드 출력
        for r in range(self.board.board_height):
            for c in range(self.board.board_width):
                button = QPushButton(self)
                button.setIconSize(QSize(32, 32))
                button.r, button.c = r, c

                cell_state = self.board.cell_states[r][c]
                if cell_state == self.board.CellState.UNSTEPPED:
                    pass
                elif cell_state == self.board.CellState.STEPPED_ON:
                    cell = self.board.board[r][c]

                    if cell == self.board.MINE:
                        button.setIcon(QIcon(self.bomb_image))
                    else:
                        button.setIcon(QIcon(self.number_images[cell]))
                elif cell_state == self.board.CellState.FLAGGED:
                    button.setIcon(QIcon(self.flag_image))
                elif cell_state == self.board.CellState.GAME_OVER_MINE:
                    button.setIcon(QIcon(self.boom_image))
                elif cell_state == self.board.CellState.GAME_OVER_INCOTRRECT_FLAG:
                    button.setIcon(QIcon(self.bomb_image))

                if self.board.is_game_over() or self.board.is_cleared():
                    pass
                else:
                    button.installEventFilter(self)

                self.table_board.setCellWidget(r, c, button)

    def refresh_game(self):
        self.board = MinesweeperBoard(self.difficulty)
        self.print_board()

        self.board.reset()

        # 상단 영역 초기화
        self.btn_refresh.setIcon(QIcon(self.sun_smile_image))
        self.lcd_time.display(0)

        for r in range(self.board.board_height):
            for c in range(self.board.board_width):
                table_widget_item = QTableWidgetItem()
                self.table_board.setItem(r, c, table_widget_item)

        self.print_board()

    def cell_left_click(self, row, col):
        if self.board.board_state == self.board.BoardState.INITIALIZED:
            self.timer_start()
        self.board.step_on_point(row, col)

        self.print_board()

    def cell_right_click(self, row, col):
        if self.board.board_state == self.board.BoardState.INITIALIZED:
            self.timer_start()
        self.board.flag_on_point(row, col)

        self.print_board()

    def timer_start(self):
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.timeout)
        self.timer.start()

    def timeout(self):
        now_time = self.lcd_time.intValue()
        self.lcd_time.display(now_time + 1)

    # utility funciton
    def __append_style_sheet(self, obj: QWidget, new_css):
        css = obj.styleSheet()
        obj.setStyleSheet(css + new_css)

    def _start_timer(self):
        self.elapsed_time += 1

        timer = threading.Timer(1, self._start_timer)


if __name__ == "__main__":
    # QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv)

    # WindowClass의 인스턴스 생성
    myWindow = WindowClass()

    # 프로그램 화면을 보여주는 코드
    myWindow.show()

    # 프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()

