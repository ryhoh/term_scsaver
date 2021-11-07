#!/usr/bin/env python3

from os import system
from random import random
import shutil
from time import sleep


EMPTY = 0
GLASS = 1
BEER = 2
BUBBLE = 3
BLACK_BEER = 4
TEXTURE = [
    " ",
    "█",
    "\u001b[00;33m█\u001b[00m",
    "\u001b[00;37m█\u001b[00m",
    "\u001b[00;30m█\u001b[00m",
]
WAVE_TOP = [
    " ",
    "\u001b[00;37m▂\u001b[00m",
    " ",
    " ",
    " ",
    " ",
]
WAVE_BUTTOM = [
    "\u001b[00;37m█\u001b[00m",
    "\u001b[00;37m█\u001b[00m",
    "\u001b[00;37m█\u001b[00m",
    "\u001b[00;37m▇\u001b[00m",
    "\u001b[00;37m▆\u001b[00m",
    "\u001b[00;37m▇\u001b[00m",
]


class Beer:
    def __init__(self) -> None:
        self.diameter = 8
        self.array = [[TEXTURE[EMPTY] for _ in range(12)]]
        self.array.extend([[
            TEXTURE[GLASS],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY],
            TEXTURE[GLASS],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY]
        ] for _ in range(8)])
        self.array.append([
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[GLASS],
            TEXTURE[EMPTY],
            TEXTURE[EMPTY]
        ])
        # あふれそうな泡を表すパラメータ
        self.delta_x = 0
        # 取っ手
        self.array[3][-1] = self.array[3][-2] = TEXTURE[GLASS]
        self.array[4][-1] = self.array[5][-1] = self.array[6][-1] = TEXTURE[GLASS]
        self.array[7][-1] = self.array[7][-2] = TEXTURE[GLASS]

        self.top = None
        self.is_black = False  # 稀に黒ビールになる

        # 部分書き込み用 (begin, end)
        self.line_updated_range = [None for _ in range(len(self.array))]

    def __str__(self) -> str:
        return '%s\n' % ('\n'.join(''.join(row) for row in self.array))

    def partial_write(self):
        print('\033[11A\r', end='')
        for row_i in range(len(self.array)):
            if self.line_updated_range[row_i] is not None:
                begin, end = self.line_updated_range[row_i]
                print('\033[%sC' % end, end='')  # 書き換え箇所の終わりにカーソル移動
                print('\b' * (end - begin), end='')
                print(''.join(self.array[row_i][begin: end]), end='')
                self.line_updated_range[row_i] = None
            print('\033[1B\r', end='')
        print('\033[1B\r', end='')

    def fill(self, interval_ms: int = 500):
        """
        泡を波うたせながら，interval_ms ずつかけてビールを注ぐ
        """
        # 確率で黒ビールになる
        self.is_black = True if random() < 0.02 else False
        BEER_TEXTURE = TEXTURE[BLACK_BEER] if self.is_black else TEXTURE[BEER]
        
        while self.top is None or self.top > 1:
            self.delta_x += 1
            if self.top is None:
                self.top = len(self.array) - 2
            else:
                self.top -= 1
            # テクスチャ反映
            self.array[self.top][1:1 + self.diameter] = [TEXTURE[BUBBLE] for _ in range(self.diameter)]
            if self.top + 1 < len(self.array) - 1:
                self.array[self.top + 1][1:1 + self.diameter] = [TEXTURE[BUBBLE] for _ in range(self.diameter)]
            if self.top + 2 < len(self.array) - 1:
                self.array[self.top + 2][1:1 + self.diameter] = [BEER_TEXTURE for _ in range(self.diameter)]
            
            self.wave(self.top - 1)
            self.line_updated_range[self.top - 1] = self.line_updated_range[self.top] = (1, 1 + self.diameter)
            if self.top + 1 < len(self.array) - 1:
                self.line_updated_range[self.top + 1] = (1, 1 + self.diameter)
            if self.top + 2 < len(self.array) - 1:
                self.line_updated_range[self.top + 2] = (1, 1 + self.diameter)
            self.partial_write()
            sleep(interval_ms / 1000)

    # 正弦波風に揺らしたいな〜
    def wave(self, top_altitude: int):
        for x in range(1, 1 + self.diameter):
            self.array[top_altitude    ][x] = WAVE_TOP   [(x + self.delta_x) % len(WAVE_TOP)]
            self.array[top_altitude + 1][x] = WAVE_BUTTOM[(x + self.delta_x) % len(WAVE_TOP)]

    def keep_waving(self, top_altitude: int, times: int, interval_ms: int = 500) -> int:
        end = self.delta_x + times
        while self.delta_x < end:
            self.delta_x += 1
            self.wave(top_altitude)
            self.line_updated_range[top_altitude] = self.line_updated_range[top_altitude + 1] = (1, 1 + self.diameter)
            self.partial_write()
            sleep(interval_ms / 1000)

    def drink(self, interval_ms: int = 500) -> int:
        """
        泡を波うたせながら，interval_ms ずつかけてビールを飲む
        """
        if self.top is None:
            return None  # すでに空やん…
        while self.top < len(self.array) - 1:
            self.delta_x += 1
            self.top += 1
            # テクスチャ反映
            self.array[self.top - 2][1:1 + self.diameter] = [TEXTURE[EMPTY] for _ in range(self.diameter)]
            self.array[self.top - 1][1:1 + self.diameter] = [TEXTURE[EMPTY] for _ in range(self.diameter)]
            if self.top + 1 < len(self.array) - 1:
                self.array[self.top + 1][1:1 + self.diameter] = [TEXTURE[BUBBLE] for _ in range(self.diameter)]
            if self.top + 1 < len(self.array):
                self.wave(self.top - 1)
            self.line_updated_range[self.top - 2] = self.line_updated_range[self.top - 1] = (1, 1 + self.diameter)
            if self.top + 1 < len(self.array) - 1:
                self.line_updated_range[self.top + 1] = (1, 1 + self.diameter)
            if self.top + 1 < len(self.array):
                self.line_updated_range[self.top] = (1, 1 + self.diameter)
            self.partial_write()
            sleep(interval_ms / 1000)
        self.top = None


def beer():
    beer = Beer()
    while True:
        system('clear')
        print('\n' * shutil.get_terminal_size().lines)  # ターミナル画面の下に押し付けないと，カーソル移動による描画処理が正しく行われない
        print(beer)
        beer.fill()
        beer.keep_waving(0, 10)
        beer.drink()
        sleep(5)


if __name__ == '__main__':
    beer()
