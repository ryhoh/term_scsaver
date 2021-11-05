from os import system
import shutil
from time import sleep


EMPTY = 0
GLASS = 1
BEER = 2
BUBBLE = 3
# BUBBLE_TOP = 4
TEXTURE = [
    " ",
    "█",
    "\u001b[00;33m█\u001b[00m",
    "\u001b[00;37m█\u001b[00m",
    # "\u001b[00;37m▂\u001b[00m",
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
        print(self.array)
        # あふれそうな泡を表すパラメータ
        self.delta_x = 0
        # 取っ手
        self.array[3][-1] = self.array[3][-2] = TEXTURE[GLASS]
        self.array[4][-1] = self.array[5][-1] = self.array[6][-1] = TEXTURE[GLASS]
        self.array[7][-1] = self.array[7][-2] = TEXTURE[GLASS]

        self.top = None

    def __str__(self) -> str:
        return '%s\n' % ('\n'.join(''.join(row) for row in self.array))

    def fill(self, interval_ms: int = 500) -> int:
        """
        泡を波うたせながら，interval_ms ずつかけてビールを注ぐ
        """
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
                self.array[self.top + 2][1:1 + self.diameter] = [TEXTURE[BEER] for _ in range(self.diameter)]
            
            self.wave(self.top - 1)
            system('clear')
            print(self)
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
            system('clear')
            print(self)
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
            system('clear')
            print(self)
            sleep(interval_ms / 1000)
        self.top = None


def beer():
    while True:
        ts = shutil.get_terminal_size()
        height, width = ts.lines, ts.columns
        height -= 2

        height = max(height, 5)
        width = max(width, 5)
        beer = Beer()
        beer.fill()
        beer.keep_waving(0, 10)
        beer.drink()
        sleep(5)


if __name__ == '__main__':
    beer()
