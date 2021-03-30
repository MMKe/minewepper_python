import enum
from typing import List, Tuple
from enum import Enum, auto
from collections import deque


class Difficulty(Enum):
    EASY = 0
    MIDDIUM = 1
    HARD = 2


class MinesweeperBoard:
    """
    지뢰찾기에 사용되는 보드
    """

    class BoardState(Enum):
        "게임 보드의 상태"
        INITIALIZED = auto()  # 초기화된 상태
        GAME_OVER = auto()  # 게임 오버
        IN_PROGRESS = auto()  # 진행중
        CLEAR = auto()  # 클리어

    class CellState(Enum):
        "셀의 상태를 나타낸다."
        UNSTEPPED = auto()  # 아직 밟히지 않은 상태
        FLAGGED = auto()  # 깃발이 세워진 상태
        STEPPED_ON = auto()  # 밟힌 상태

        GAME_OVER_MINE = auto()  # 게임 오버가 되게 만든 지뢰
        GAME_OVER_INCOTRRECT_FLAG = auto()  # 게임 오버가 되게 만든 깃발

    board_widths = [9, 16, 30]  # 게임판의 난이도별 너비
    board_heights = [9, 16, 16]  # 게임판의 난이도별 높이
    board_mine_cnts = [10, 40, 99]  # 게임판의 난이도별 지뢰의 갯수

    MINE = "*"  # 지뢰 상수

    def __init__(self, difficulty: Difficulty) -> None:
        """
        주어진 난이도에 따라 내부 변수를 설정한다.
        또한 내부 변수에 board를 생성한다.
        """

        # 게임 상태 초기화
        self.board_state = self.BoardState.INITIALIZED

        # 게임 보드, 셀 상태 초기화
        self.board = []
        self.cell_states = []  # 셀의 상태를 관리한다.
        self.mine_points = []  # 지뢰의 위치

        # 난이도별 너비, 높이, 지뢰 수를 초기화
        self.board_width = self.board_widths[difficulty.value]
        self.board_height = self.board_heights[difficulty.value]
        self.mine_cnt = self.board_mine_cnts[difficulty.value]
        self.mine_counter = self.mine_cnt

        # 보드를 만든다.
        self.__make_board()

    def __select_random_num(self, limit) -> int:
        " 0 ~ limit - 1 범위의 무작위 정수를 하나 반환한다.  "
        import random

        return random.randint(0, limit - 1)

    def __select_random_point(self) -> Tuple[int, int]:
        "board 크기를 기반으로 무작위 좌표를 반환한다."
        y = self.__select_random_num(self.board_height)
        x = self.__select_random_num(self.board_width)
        return (y, x)

    def __create_mine_points(self) -> List[Tuple[int, int]]:
        "self.mine_cnt 개수만큼 무작위 지뢰 좌표들을 생성한다."
        mine_points = []
        for _ in range(self.mine_cnt):
            mine_point = self.__select_random_point()
            while mine_point in mine_points:
                mine_point = self.__select_random_point()

            mine_points.append(mine_point)

        return mine_points

    def __make_board(self):
        "지뢰찾기를 진행할 board를 만든다. 내부 변수에 저장한다."
        self.board = []
        self.cell_states = []

        for _ in range(self.board_height):
            self.board.append([0] * self.board_width)
            self.cell_states.append([self.CellState.UNSTEPPED] * self.board_width)

        # 지뢰 좌표 생성 및 지뢰를 심으면서 주변 타일 값 세팅
        self.mine_points = self.__create_mine_points()
        for mine_point in self.mine_points:
            y, x = mine_point
            self.board[y][x] = self.MINE

            def add_num(self, y, x):
                if self.board[y][x] == self.MINE:
                    return

                self.board[y][x] += 1

            self.__traverse_around(y, x, add_num)

    def __traverse_around(self, y, x, callback):
        "y, x의 주변을 순회하면서 callback을 호출한다."
        start_y = y - 1
        start_x = x - 1

        for traverse_y in range(start_y, start_y + 3):
            for traverse_x in range(start_x, start_x + 3):
                # y 범위 초과시 continue
                if traverse_y < 0 or traverse_y >= self.board_height:
                    continue
                # x 범위 초과시 continue
                if traverse_x < 0 or traverse_x >= self.board_width:
                    continue

                # 호출한 좌표에서는 함수를 호출하지 않는다.
                if traverse_y == y and traverse_x == x:
                    continue

                callback(self, traverse_y, traverse_x)

    def is_game_over(self):
        "게임 오버인지 확인한다."
        return self.board_state == self.BoardState.GAME_OVER

    def is_cleared(self):
        "클리어 되었는지 확인한다."
        return self.board_state == self.BoardState.CLEAR

    def game_over(self, y, x, *, real_mine_points=None, incorrect_flag_points=None):
        "게임을 게임오버 시킨다. 지뢰 셀을 오픈한다."
        self.board_state = self.BoardState.GAME_OVER

        if real_mine_points == None and incorrect_flag_points == None:
            # 지뢰를 클릭하여 게임오버 된 경우
            self.cell_states[y][x] = self.CellState.GAME_OVER_MINE
        else:
            # 잘못된 깃발로 게임오버 된 경우
            for mine_y, mine_x in real_mine_points:
                self.cell_states[mine_y][mine_x] = self.CellState.GAME_OVER_MINE

            for flag_y, flag_x in incorrect_flag_points:
                self.cell_states[flag_y][
                    flag_x
                ] = self.CellState.GAME_OVER_INCOTRRECT_FLAG

        for mine_y, mine_x in self.mine_points:
            if self.cell_states[mine_y][mine_x] == self.CellState.UNSTEPPED:
                self.cell_states[mine_y][mine_x] = self.CellState.STEPPED_ON

    def reset(self):
        "게임 상태와 보드를 초기화한다."
        self.board_state = self.BoardState.INITIALIZED

        self.__make_board()

    def change_difficulty(self, difficulty: Difficulty):
        "난이도를 바꾸고 게임을 초기화한다."
        self.__init__(difficulty)

        self.reset()

    def step_on_point(self, y, x):
        if self.board_state == self.BoardState.INITIALIZED:
            self.board_state = self.BoardState.IN_PROGRESS

        if self.cell_states[y][x] == self.CellState.FLAGGED:  # 깃발이 꽂힌 곳은 종료한다.
            return

        if self.cell_states[y][x] == self.CellState.STEPPED_ON:  # 이미 밟은 곳일 경우
            self.__step_already_stepped_on(y, x)
        elif self.cell_states[y][x] == self.CellState.UNSTEPPED:  # 처음 밟는 곳일 경우
            self.__step_unstepped_point(y, x)

        self.__check_clear()

    def flag_on_point(self, y, x):
        if self.board_state == self.BoardState.INITIALIZED:
            self.board_state = self.BoardState.IN_PROGRESS

        "해당 포인트에 깃발을 꼽거나 해제한다."
        if self.cell_states[y][x] == self.CellState.STEPPED_ON:
            return

        if self.cell_states[y][x] == self.CellState.UNSTEPPED:
            self.cell_states[y][x] = self.CellState.FLAGGED
            self.mine_counter -= 1
            return
        elif self.cell_states[y][x] == self.CellState.FLAGGED:
            self.cell_states[y][x] = self.CellState.UNSTEPPED
            self.mine_counter += 1
            return

        return

    def __step_already_stepped_on(self, y, x):
        """
        이미 밟은 곳을 다시 밟는 경우를 처리한다. 
        """
        if self.cell_states[y][x] == self.CellState.UNSTEPPED:
            raise Exception("{0}, {1} is not stepped on ".format(y, x))

        if self.cell_states[y][x] == self.CellState.FLAGGED:
            return

        if self.board[y][x] == 0:  # 빈 칸이면 종료
            return

        class MineFlagCounter:
            "지뢰와 깃발의 위치를 저장하는 카운터 클래스"

            def __init__(self):
                self.around_mine_points = []
                self.around_flag_points = []

            def __call__(self, board: MinesweeperBoard, y, x):
                if board.board[y][x] == board.MINE:
                    self.around_mine_points.append((y, x))

                if board.cell_states[y][x] == board.CellState.FLAGGED:
                    self.around_flag_points.append((y, x))

        # y, x 주변을 순회하면서 지뢰와 깃발의 포인트를 찾는다.
        count_mine_flag = MineFlagCounter()
        self.__traverse_around(y, x, count_mine_flag)

        around_mine_points = count_mine_flag.around_mine_points
        around_flag_points = count_mine_flag.around_flag_points

        if len(around_mine_points) != len(around_flag_points):
            # 주변의 지뢰와 깃발 갯수가 같을 때만 동작. 다르면 종료
            return

        # 깃발이 잘못 꽂혀 있을 경우, 실제 지뢰의 위치와 잘못된 깃발의 위치를 저장한다.
        real_mine_points = []
        incorrect_flag_points = []

        for mine_point, flag_point in zip(around_mine_points, around_flag_points):
            if mine_point == flag_point:
                continue

            if mine_point != flag_point:
                real_mine_points.append(mine_point)
                incorrect_flag_points.append(flag_point)

        if real_mine_points and incorrect_flag_points:  # 잘못된 깃발이 존재하면 게임 오버시키고 종료
            self.game_over(
                y,
                x,
                real_mine_points=real_mine_points,
                incorrect_flag_points=incorrect_flag_points,
            )
            return
        else:  # 모든 지뢰를 찾은 경우, 주변의 타일에서 지뢰가 아닌 곳을 step on 처리 한다.
            start_y = y - 1
            start_x = x - 1

            for traverse_y in range(start_y, start_y + 3):
                for traverse_x in range(start_x, start_x + 3):
                    # y 범위 초과시 continue
                    if traverse_y < 0 or traverse_y >= self.board_height:
                        continue
                    # x 범위 초과시 continue
                    if traverse_x < 0 or traverse_x >= self.board_width:
                        continue

                    # 호출한 좌표에서는 함수를 호출하지 않는다.
                    if traverse_y == y and traverse_x == x:
                        continue

                    if (
                        self.cell_states[traverse_y][traverse_x]
                        == self.CellState.UNSTEPPED
                    ):
                        self.step_on_point(traverse_y, traverse_x)

            return

    def __step_unstepped_point(self, y, x):
        """
        처음 밟는 곳을 처리한다. 
        """
        if self.cell_states[y][x] == self.CellState.STEPPED_ON:
            raise Exception("{0}, {1} is already stepped on ".format(y, x))

        if self.cell_states[y][x] == self.CellState.FLAGGED:
            raise Exception("{0}, {1} is flagged ".format(y, x))

        if self.board[y][x] == self.MINE:
            # 지뢰를 밟은 경우, 셀 상태와 게임 상태를 갱신하고 종료
            self.game_over(y, x)
            return

        around_mine_cnt = self.board[y][x]

        if around_mine_cnt != 0:
            # 2-1. 주변에 지뢰가 한 개 이상 있는 경우, 해당 포인트를 STEP ON 하고 종료
            self.cell_states[y][x] = self.CellState.STEPPED_ON
            return

        # 2-2. 주변에 지뢰가 없는 경우, bfs 하여 연결된 0인 셀을 전부 STEP ON 시킨다.

        # class BfsQueue:
        #     def __init__(self):
        #         self.queue = []

        #     def __call__(self, board: MinesweeperBoard, y, x):
        #         if board.cell_states[y][x] == board.CellState.STEPPED_ON:
        #             return

        #         if board.board[y][x] == board.MINE:
        #             return

        #         board.cell_states[y][x] = board.CellState.STEPPED_ON

        #         if board.board[y][x] == 0:
        #             self.queue.append((y, x))

        #     def append(self, item):
        #         self.queue.append(item)

        queue = deque()
        queue.append((y, x))
        self.cell_states[y][x] = self.CellState.STEPPED_ON

        while queue:

            def bfs_callback(self: MinesweeperBoard, y, x):
                """
                bfs 과정에서의 콜백 함수 
                해당 셀이 이미 밟은 상태이거나, 지뢰이면 패스 
                그렇지 않으면 셀을 step on 상태로 갱신하고, 0인 경우 queue에 넣는다. 
                """
                nonlocal queue

                if self.cell_states[y][x] == self.CellState.STEPPED_ON:
                    return

                if self.board[y][x] == self.MINE:
                    return

                self.cell_states[y][x] = self.CellState.STEPPED_ON

                if self.board[y][x] == 0:
                    queue.append((y, x))

            now_y, now_x = queue.popleft()
            self.__traverse_around(now_y, now_x, bfs_callback)

    def __check_clear(self):
        """
        클리어 여부를 체크하고, 보드의 상태를 갱신한다.
        """
        if self.board_state != self.BoardState.IN_PROGRESS:
            return

        is_clear = True

        for y in range(self.board_height):
            for x in range(self.board_width):
                if (
                    self.board[y][x] != self.MINE  # 지뢰가 아닌 셀이
                    and self.cell_states[y][x]
                    == self.CellState.UNSTEPPED  # 아직 밝혀지지 않았다면
                ):
                    is_clear = False
                    break

        if is_clear:
            self.board_state = self.BoardState.CLEAR

            # 클리어 한 경우, 깃발이 꽂히지 않은 지뢰를 전부 깃발을 꽂는다.
            for mine_point in self.mine_points:
                mine_y, mine_x = mine_point
                if self.cell_states[mine_y][mine_x] != self.CellState.FLAGGED:
                    self.cell_states[mine_y][mine_x] = self.CellState.FLAGGED
                    self.mine_counter -= 1
        else:
            self.board_state = self.BoardState.IN_PROGRESS


if __name__ == "__main__":
    board = MinesweeperBoard(Difficulty.EASY)

    print("GAME OVER")

