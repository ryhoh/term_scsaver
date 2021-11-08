#!/usr/bin/env python3

from os import system
from random import choice
import shutil
from time import sleep
from typing import Any, Final, List, Tuple

from core.color import Color
from core.partial_writer import PartialWriter


EMPTY       = 0
PLATFORM    = 1

TRAIN_BOTTOM  = 0
TRAIN_TOP     = 1
TRAIN_GLASS   = 2
TRAIN_DOOR    = 3  # deprecated
GRAY_PARTS    = 4
TRAIN_BELT    = 5
TRAIN_MIDDLE  = 6
DOOR_MIDDLE   = 7
DOOR_BELT     = 8
DOOR_BOTTOM   = 9

EMPTY_TEXTURE    = " "
PLATFORM_TEXTURE = "█"
WHEEL_TEXTURES = [
    Color.char_256_colored('⊗', 242),
    Color.char_256_colored('⊕', 242),
]
BOTTOM_EQUIPMENTS_TEXTURE = Color.char_256_colored('▀', 242)

class Train:
    def put(self, env: "Environment", pos: int = 0) -> List[Tuple[Tuple[int, int]]]:
        """
        描画をして，PartialWriter 用の更新範囲をタプルにして，リストに詰めて返す
        """
        raise NotImplementedError


class Odakyu(Train):  # WIP
    TEXTURE = [
        "\u001b[00;37m█\u001b[00m",
        "\u001b[00;34m█\u001b[00m",
        "\u001b[01;36m█\u001b[00m",
        "\u001b[02;37m█\u001b[00m",
        "\u001b[02;39m█\u001b[00m",
    ]
    CAR_LENGTH = 18 * 3 - 1  # メートル * 定数 - 調整項


class TrainWith3Doors(Train):
    CAR_LENGTH = 18 * 3 - 2  # メートル * 定数 - 調整項

    def __init__(self, car_n: int = 4) -> None:
        super().__init__()
        self.car_n = car_n
        self.f_length = self.CAR_LENGTH * car_n + 4 * (car_n - 1)
        self.TEXTURE: List[str]

    def put(self, env: "Environment", pos: int = 0):
        """
        電車を位置 pos に配置する
        pos は，プラットフォーム上の停止位置を原点とした数直線

        （京阪っぽいカラーリング）
        """
        # PartialWriter 用の更新範囲リスト
        partial_write_res = []

        def write_range(row_i: int, begin: int, end: int, fill_texture: str, end_lim: int = env.width):
            # 範囲 [begin end) で書き込み
            left, right = max(min(begin, end_lim), 0), max(min(end, end_lim), 0)
            env.array[row_i][left: right] = [fill_texture for _ in range(right - left)]
            partial_write_res.append((row_i, (left, right)))

        def write_spot(row_i: int, col_i: int, fill_texture: str, end_lim: int = env.width):
            # 特定の1マス (col_i, row_i) に書き込み
            if 0 <= col_i < end_lim:
                env.array[row_i][col_i] = fill_texture
                partial_write_res.append((row_i, (col_i, col_i + 1)))

        for car_i in range(self.car_n):
            # 先頭の位置
            front_pos = env.platform_range[0] + 1 + pos + (self.CAR_LENGTH + 4) * car_i

            for row_i in range(2, 7):  # 車体の1マス後ろをリセット
                write_spot(row_i, front_pos + self.CAR_LENGTH + 1, EMPTY_TEXTURE)
            # 車両
            write_range(2, front_pos, front_pos + self.CAR_LENGTH, self.TEXTURE[TRAIN_TOP])     # 車体上部
            for row_i in range(3, 5):  # 車体中部
                write_range(row_i, front_pos, front_pos + self.CAR_LENGTH, self.TEXTURE[TRAIN_MIDDLE])
            write_range(5, front_pos, front_pos + self.CAR_LENGTH, self.TEXTURE[TRAIN_BELT])    # 帯
            write_range(6, front_pos, front_pos + self.CAR_LENGTH, self.TEXTURE[TRAIN_BOTTOM])  # 車体下部

            if car_i % 4 == 0:  # パンタグラフ
                write_spot(0, front_pos + 10, Color.char_256_colored('▗', 246))
                write_spot(1, front_pos + 10, Color.char_256_colored('▚', 246))
                write_spot(0, front_pos + self.CAR_LENGTH - 10, Color.char_256_colored('▖', 246))
                write_spot(1, front_pos + self.CAR_LENGTH - 10, Color.char_256_colored('▞', 246))
                # パンタグラフの1マス後ろをリセット
                write_spot(0, front_pos + 11, EMPTY_TEXTURE)
                write_spot(1, front_pos + 11, EMPTY_TEXTURE)
                write_spot(0, front_pos + self.CAR_LENGTH - 9, EMPTY_TEXTURE)
                write_spot(1, front_pos + self.CAR_LENGTH - 9, EMPTY_TEXTURE)

            try:  # ドア
                door_textures = [self.TEXTURE[7], self.TEXTURE[8], self.TEXTURE[9]]
            except IndexError:
                door_textures = [self.TEXTURE[TRAIN_DOOR] for _ in range(3)]
            for row_i, texture in zip(range(3, 7), [door_textures[0], door_textures[0], door_textures[1], door_textures[2]]):
                if row_i == 5 or row_i == 6:  # ドア下部
                    for door_i in range(7, self.CAR_LENGTH, self.CAR_LENGTH // 3):
                        write_range(row_i, front_pos + door_i, front_pos + door_i + 5, texture)
                else:  # ドア上部
                    for door_i in range(7, self.CAR_LENGTH, self.CAR_LENGTH // 3):
                        textures = [texture, self.TEXTURE[TRAIN_GLASS], texture, self.TEXTURE[TRAIN_GLASS], texture]
                        for col_i, texture in enumerate(textures, start=front_pos + door_i):
                            write_spot(row_i, col_i, texture)
                
                if car_i == 0:  # 先頭の乗務員用扉
                    write_range(row_i, front_pos + 1, front_pos + 3, texture)
                elif car_i == self.car_n - 1:
                    write_range(row_i, front_pos + self.CAR_LENGTH - 2, front_pos + self.CAR_LENGTH, texture)
                    # 末尾の乗務員用扉
                    write_range(row_i, front_pos + self.CAR_LENGTH - 1, front_pos + self.CAR_LENGTH, texture)
                    # ボディが上書きされるので，もう一度ボディを1列描画する
                    write_range(2, front_pos + self.CAR_LENGTH, front_pos + self.CAR_LENGTH + 1, self.TEXTURE[TRAIN_TOP])  # 車体上部
                    for row_i in range(3, 5):  # 車体中部
                        write_range(row_i, front_pos + self.CAR_LENGTH, front_pos + self.CAR_LENGTH + 1, self.TEXTURE[TRAIN_MIDDLE])
                    write_range(5, front_pos + self.CAR_LENGTH, front_pos + self.CAR_LENGTH + 1, self.TEXTURE[TRAIN_BELT])  # 帯
                    write_range(6, front_pos + self.CAR_LENGTH, front_pos + self.CAR_LENGTH + 1, self.TEXTURE[TRAIN_BOTTOM])  # 車体下部
            
            for row_i in range(3, 5):  # 窓
                for glass_i in range(14, self.CAR_LENGTH * 2 // 3, self.CAR_LENGTH // 3):
                    write_range(row_i, front_pos + glass_i, front_pos + glass_i + 3, self.TEXTURE[TRAIN_GLASS])
                    write_range(row_i, front_pos + glass_i + 5, front_pos + glass_i + 8, self.TEXTURE[TRAIN_GLASS])
                if car_i == 0:  # 前後の窓
                    write_range(row_i, front_pos + 4, front_pos + 6, self.TEXTURE[TRAIN_GLASS])
                else:
                    write_range(row_i, front_pos + 2, front_pos + 5, self.TEXTURE[TRAIN_GLASS])
                if car_i != self.car_n - 1:
                    write_range(row_i, front_pos + self.CAR_LENGTH - 4, front_pos + self.CAR_LENGTH - 1, self.TEXTURE[TRAIN_GLASS])
                else:
                    write_range(row_i, front_pos + self.CAR_LENGTH - 5, front_pos + self.CAR_LENGTH - 3, self.TEXTURE[TRAIN_GLASS])
                if car_i != self.car_n - 1:  # 貫通路
                    for row_i in range(3, 7):
                        write_range(row_i, front_pos + self.CAR_LENGTH + 1, front_pos + self.CAR_LENGTH + 5, self.TEXTURE[GRAY_PARTS])
            
            for col_i in range(6, self.CAR_LENGTH, self.CAR_LENGTH * 2 // 3 + 1):  # 車輪
                write_spot(7, front_pos + col_i, WHEEL_TEXTURES[pos % 2], end_lim=env.width // 4)
                write_spot(7, front_pos + col_i + 4, WHEEL_TEXTURES[pos % 2], end_lim=env.width // 4)
                # 車輪の1マス後ろをリセット
                write_spot(7, front_pos + col_i + 1, EMPTY_TEXTURE, end_lim=env.width // 4)
                write_spot(7, front_pos + col_i + 5, EMPTY_TEXTURE, end_lim=env.width // 4)
            
            for col_i in range(18, self.CAR_LENGTH * 2 // 3, 6):  # 床下機器
                write_range(7, front_pos + col_i, front_pos + col_i + 3, BOTTOM_EQUIPMENTS_TEXTURE, end_lim=env.width // 4)
                # 1マス後ろをリセット
                write_spot(7, front_pos + col_i + 4, EMPTY_TEXTURE, end_lim=env.width // 4)
        
        return partial_write_res


class Keihan(TrainWith3Doors):
    TEXTURE = [
        Color.char_256_colored('█', 254),
        Color.char_256_colored('█', 28),
        Color.char_256_colored('█', 81),
        None,
        Color.char_256_colored('█', 242),
        Color.char_256_colored('█', 118),
        Color.char_256_colored('█', 28),
        Color.char_256_colored('█', 22),
        Color.char_256_colored('█', 76),
        Color.char_256_colored('█', 251),
    ]

class OsakaLoop(TrainWith3Doors):
    TEXTURE = [
        Color.char_256_colored('█', 208),
        Color.char_256_colored('█', 208),
        Color.char_256_colored('█', 81),
        None,
        Color.char_256_colored('█', 242),
        Color.char_256_colored('█', 208),
        Color.char_256_colored('█', 208),
        Color.char_256_colored('█', 166),
        Color.char_256_colored('█', 166),
        Color.char_256_colored('█', 166),
    ]

class OsakaMetroMidosuji(TrainWith3Doors):
    TEXTURE = [
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 81),
        None,
        Color.char_256_colored('█', 242),
        Color.char_256_colored('█', 196),
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 248),
        Color.char_256_colored('█', 160),
        Color.char_256_colored('█', 248),
    ]

class OsakaMetroChuo(TrainWith3Doors):
    TEXTURE = [
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 81),
        None,
        Color.char_256_colored('█', 242),
        Color.char_256_colored('█', 28),
        Color.char_256_colored('█', 251),
        Color.char_256_colored('█', 248),
        Color.char_256_colored('█', 22),
        Color.char_256_colored('█', 248),
    ]

class Hankyu(TrainWith3Doors):
    TEXTURE = [
        Color.char_256_colored('█', 88),
        Color.char_256_colored('▄', 88, 251),
        Color.char_256_colored('█', 81),
        None,
        Color.char_256_colored('█', 242),
        Color.char_256_colored('█', 88),
        Color.char_256_colored('█', 88),
        Color.char_256_colored('█', 52),
        Color.char_256_colored('█', 52),
        Color.char_256_colored('█', 52),
    ]


AVAILABLE_TRAINS = [
    Keihan,
    OsakaMetroMidosuji,
    OsakaMetroChuo,
    Hankyu,
]


class Environment(PartialWriter):
    def __init__(self, width: int) -> None:
        super().__init__(height=9, width=width)
        self.width: Final[int] = width // 4 * 4
        self.array = [[EMPTY_TEXTURE for _ in range(width)] for _ in range(7)]
        self.array.extend([
            [EMPTY_TEXTURE for _ in range(width // 4)] + [PLATFORM_TEXTURE for _ in range(width * 3 // 4)]
        ])
        self.height = len(self.array)
        self.platform_range = (width // 4, width * 3 // 4 - 1)
        self.line_is_updated = [False for _ in range(len(self.array))]


    def __str__(self) -> str:
        return '%s\n' % ('\n'.join(''.join(row) for row in self.array))

    def set_into_array(self, y: int, x: int, val: Any):
        if y < 0 or self.height <= y or x < 0 or self.width <= x:
            return None
        self.array[y][x] = val

    def stopping(self, from_x: int, train: Train, base_interval: int = 250):
        """
        from_x から原点まで移動して停車する．
        直線運動モデルを仮定して，描画インターバルを変化させて滑らかに止める．

        時刻tにおいて，
        a: (定数，負)
        v = at
        x = at^2 / 2

        ここで，式3より，
        t = sqrt(2x / a)
        あるマスにいるとき，次のマスに到達すべき時刻を求めて，それまで待つ
        """
        # とりあえず Keihan モデルを仮定
        # 減速度も可変にする (3.0 ~ 0.25) でスケール
        a_vec = [3.0 - (2.75 / (from_x - 1)) * step for step in range(from_x)]
        # 描画
        for x, a in zip(range(from_x, 0, -1), a_vec):  # 1マスごとに描画
            partial_write_res = train.put(self, x)
            for row_i, partial_write_range in partial_write_res:
                self.set_line_updated_range(row_i, partial_write_range)
            self.partial_write()
            if x != 0:
                t = (2 * x / a) ** 0.5
                next_t = (2 * (x-1) / a) ** 0.5
                sleep((t - next_t) * base_interval / 1000)
                t = next_t

    def leaving(self, to_x: int, train: Train, base_interval: int = 250):
        """
        原点から to_x まで移動する．
        直線運動モデルを仮定して，描画インターバルを変化させて滑らかに止める．

        時刻tにおいて，
        a: (定数，負)
        v = at
        x = at^2 / 2

        ここで，式3より，
        t = sqrt(2x / a)
        あるマスにいるとき，次のマスに到達すべき時刻を求めて，それまで待つ
        """
        # とりあえず Keihan モデルを仮定
        # 加速度も可変にする (1.0 ~ 3.0) でスケール
        a_vec = [(2.0 / (-to_x - 1)) * step + 1.0 for step in range(-to_x)]
        # 描画
        for x, a in zip(range(0, to_x, -1), a_vec):  # 1マスごとに描画
            partial_write_res = train.put(self, x)
            for row_i, partial_write_range in partial_write_res:
                self.set_line_updated_range(row_i, partial_write_range)
            self.partial_write()
            if x != to_x:
                t = (2 * -x / a) ** 0.5
                next_t = (2 * (-x+1) / a) ** 0.5
                sleep((next_t - t) * base_interval / 1000)
                t = next_t


def train():
    while True:
        ts = shutil.get_terminal_size()
        width, height = ts.columns, ts.lines
        width -= 1
        system('clear')
        print('\n' * height)  # ターミナル画面の下に押し付けないと，カーソル移動による描画処理が正しく行われない
        env = Environment(width)
        # train = Hankyu()
        train = choice(AVAILABLE_TRAINS)()
        print(env)
        env.stopping(width * 3 // 4, train)
        sleep(2)
        env.leaving(-train.f_length - width // 4 - 3, train)
        sleep(5)


if __name__ == '__main__':
    train()
