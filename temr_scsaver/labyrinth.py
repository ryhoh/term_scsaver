#!/usr/bin/env python3

from random import randrange, sample
import shutil
from time import sleep
from typing import Final, List, Set, Tuple


EMPTY = 0
WALL  = 1
TRAIL = 2
START = 3
GOAL  = 4
TEXTURE = [
    " ",
    "█",
    "\u001b[00;32m█\u001b[00m",
    "\u001b[00;36m█\u001b[00m",
    "\u001b[00;35m█\u001b[00m",
]
# 4近傍確認用
dx = [-1, 1, 0, 0]
dy = [0, 0, -1, 1]


class Labyrinth:
    def __init__(self, width: int, height: int) -> None:
        self.width: Final[int] = width
        self.height: Final[int] = height
        self.array = [[TEXTURE[WALL] for _ in range(width)] for _ in range(height)]
        self.start = None
        self.goal = None

    def __str__(self) -> str:
        return '%s\n' % '\n'.join(''.join(self.array[y]) for y in range(self.height))

    def partial_write(self, update_line: int):
        row_shift = self.height - update_line + 1
        print('\033[%sA\r%s\n\033[%sB' % (row_shift, ''.join(self.array[update_line]), row_shift), end='')


    def dig(self, interval_ms: int = 50):
        open_cells = []  # 枝分かれする（可能性のある）マスをここに詰め込む
        # 内側(width-1)*(height-1)の範囲の中からそれぞれ偶数である開始点を1つ選ぶ
        begin_x = randrange((self.width - 1) // 2) * 2 + 1
        begin_y = randrange((self.height - 1) // 2) * 2 + 1
        
        # 開始地点をpushして穴掘り開始
        here = (begin_x, begin_y)
        open_cells.append(here)
        self.array[begin_y][begin_x] = TEXTURE[EMPTY]
        while len(open_cells):
            # 4近傍のどれかに進みたい．ランダムな順番に見ていく
            found = False  # どこにも進めない場合 False
            for next in sample(list(range(4)), 4):
                next1_x = here[0] + dx[next]
                next1_y = here[1] + dy[next]
                next2_x = here[0] + 2 * dx[next]
                next2_y = here[1] + 2 * dy[next]
                # 範囲外に行かないかチェック
                if next2_x < 0 or next2_x >= self.width - 1 or next2_y < 0 or next2_y >= self.height - 1:
                    continue
                # さっきいた場所に戻りたくない，隣が道だといけない
                if self.array[next1_y][next1_x] != TEXTURE[WALL]:
                    continue
                if self.array[next2_y][next2_x] == TEXTURE[WALL]:  # 2マス先まで壁なら
                    self.array[next1_y][next1_x] = self.array[next2_y][next2_x] = TEXTURE[EMPTY]  # 道にする
                    here = (next2_x, next2_y)  # 次の開始地点
                    open_cells.append(here)
                    found = True
                    self.partial_write(next1_y)
                    self.partial_write(next2_y)
                    sleep(interval_ms / 1000)
                    break
            if not found:
                here = sample(open_cells, 1)[0]
                open_cells.remove(here)

    def placeStartGoal(self):
        # ランダムに道を1つ選び，そこから遠い場所，反対側の遠い場所を見る
        init_coordinate = self.selectEmptyRandomly()
        candidate_1 = self.farthest_from(init_coordinate)
        candidate_2 = self.farthest_from(candidate_1)
        # 左側にあるものをスタート，もう一方がゴール
        if candidate_1[0] < candidate_2[0]:
            self.array[candidate_1[1]][candidate_1[0]] = TEXTURE[START]
            self.array[candidate_2[1]][candidate_2[0]] = TEXTURE[GOAL]
            self.start = candidate_1
            self.goal = candidate_2
        else:
            self.array[candidate_2[1]][candidate_2[0]] = TEXTURE[START]
            self.array[candidate_1[1]][candidate_1[0]] = TEXTURE[GOAL]
            self.start = candidate_2
            self.goal = candidate_1
        self.partial_write(candidate_1[1])
        self.partial_write(candidate_2[1])

    def selectEmptyRandomly(self) -> Tuple[int, int]:
        while True:  # バグがなければ，1回で必ず終わるはず
            x = randrange((self.width - 1) // 2) * 2 + 1
            y = randrange((self.height - 1) // 2) * 2 + 1
            if self.array[y][x] == TEXTURE[EMPTY]:
                return x, y  # 道だったらそれを返す．壁なら4近傍から選ぶ
            for next in sample(list(range(4)), 4):
                next1_x = x[0] + dx[next]
                next1_y = y[1] + dy[next]
                if self.array[next1_y][next1_x] == TEXTURE[EMPTY]:
                    return next1_x, next1_y

    def farthest_from(self, coordinate_from: Tuple[int, int]) -> Tuple[int, int]:
        """
        一番遠い場所を BFS で見つける
        """
        queue: List[Tuple[int, int]] = [coordinate_from]
        checked: Set[Tuple[int, int]] = set()
        result: Tuple[int, int] = coordinate_from
        while len(queue):
            here = queue.pop(0)
            if here in checked:
                continue
            checked.add(here)
            # 4近傍を見る
            for next in range(4):
                next1_x = here[0] + dx[next]
                next1_y = here[1] + dy[next]
                if self.array[next1_y][next1_x] == TEXTURE[EMPTY]:
                    queue.append((next1_x, next1_y))
            result = here
        return result

    def solve(self, interval_ms: int = 500):
        """
        DFS で解くところを，1手 interval_ms かけながら見せる
        """
        stack: List[Tuple[int, int]] = [self.start]
        while len(stack):
            here = stack.pop()
            if here != self.start:
                self.array[here[1]][here[0]] = TEXTURE[TRAIL]
            if here == self.goal:
                break
            # 4近傍を見る
            for next in range(4):
                next1_x = here[0] + dx[next]
                next1_y = here[1] + dy[next]
                if self.array[next1_y][next1_x] in (TEXTURE[WALL], TEXTURE[START], TEXTURE[TRAIL]):
                    continue
                stack.append((next1_x, next1_y))
            self.partial_write(here[1])
            sleep(interval_ms / 1000)
            

def labyrinth():
    while True:
        ts = shutil.get_terminal_size()
        height, width = ts.lines, ts.columns
        height -= 2
        if width % 2 == 0:
            width -= 1
        if height % 2 == 0:
            height -= 1
        labyrinth = Labyrinth(width, height)
        print(labyrinth)
        labyrinth.dig()
        labyrinth.placeStartGoal()
        labyrinth.solve()
        sleep(10)


if __name__ == '__main__':
    labyrinth()
