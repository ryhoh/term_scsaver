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
        # def write_range(row_i: int, begin: int, end: int)

        # PartialWriter 用の更新範囲リスト
        partial_write_res = []

        for car_i in range(self.car_n):
            # 先頭の位置
            front_pos = env.platform_range[0] + 1 + pos + (self.CAR_LENGTH + 4) * car_i

            # 車体の1マス後ろをリセット
            if 0 <= front_pos + self.CAR_LENGTH + 1 < env.width:
                for row_i in range(2, 7):
                    env.array[row_i][front_pos + self.CAR_LENGTH + 1] = EMPTY_TEXTURE
                    partial_write_res.append((row_i, (front_pos + self.CAR_LENGTH + 1, front_pos + self.CAR_LENGTH + 2)))
            # 車両
            for row_i in range(2, 3):  # 車体上部
                left, right = max(min(front_pos, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
                env.array[row_i][left: right] = [self.TEXTURE[TRAIN_TOP] for _ in range(right - left)]
                partial_write_res.append((row_i, (left, right)))
            for row_i in range(3, 5):  # 車体中部
                left, right = max(min(front_pos, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
                env.array[row_i][left: right] = [self.TEXTURE[TRAIN_MIDDLE] for _ in range(right - left)]
                partial_write_res.append((row_i, (left, right)))
            # 帯
            left, right = max(min(front_pos, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
            env.array[5][left: right] = [self.TEXTURE[TRAIN_BELT] for _ in range(right - left)]
            partial_write_res.append((5, (left, right)))
            for row_i in range(6, 7):  # 車体下部
                left, right = max(min(front_pos, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
                env.array[row_i][left: right] = [self.TEXTURE[TRAIN_BOTTOM] for _ in range(right - left)]
                partial_write_res.append((row_i, (left, right)))

            if car_i % 4 == 0:  # パンタグラフ
                if 0 <= front_pos + 10 < env.width:
                    env.array[0][front_pos + 10] = Color.char_256_colored('▗', 246)
                    env.array[1][front_pos + 10] = Color.char_256_colored('▚', 246)
                    partial_write_res.append((0, (front_pos + 10, front_pos + 11)))
                    partial_write_res.append((1, (front_pos + 10, front_pos + 11)))
                if 0 <= front_pos + self.CAR_LENGTH - 10 < env.width:
                    env.array[0][front_pos + self.CAR_LENGTH - 10] = Color.char_256_colored('▖', 246)
                    env.array[1][front_pos + self.CAR_LENGTH - 10] = Color.char_256_colored('▞', 246)
                    partial_write_res.append((0, (front_pos + self.CAR_LENGTH - 10, front_pos + self.CAR_LENGTH - 9)))
                    partial_write_res.append((1, (front_pos + self.CAR_LENGTH - 10, front_pos + self.CAR_LENGTH - 9)))
                # パンタグラフの1マス後ろをリセット
                if 0 <= front_pos + 11 < env.width:
                    env.array[0][front_pos + 11] = EMPTY_TEXTURE
                    env.array[1][front_pos + 11] = EMPTY_TEXTURE
                    partial_write_res.append((0, (front_pos + 11, front_pos + 12)))
                    partial_write_res.append((1, (front_pos + 11, front_pos + 12)))
                if 0 <= front_pos + self.CAR_LENGTH - 9 < env.width:
                    env.array[0][front_pos + self.CAR_LENGTH - 9] = EMPTY_TEXTURE
                    env.array[1][front_pos + self.CAR_LENGTH - 9] = EMPTY_TEXTURE
                    partial_write_res.append((0, (front_pos + self.CAR_LENGTH - 9, front_pos + self.CAR_LENGTH - 8)))
                    partial_write_res.append((1, (front_pos + self.CAR_LENGTH - 9, front_pos + self.CAR_LENGTH - 8)))

            # ドア
            try:
                door_textures = [self.TEXTURE[7], self.TEXTURE[8], self.TEXTURE[9]]
            except IndexError:
                door_textures = [self.TEXTURE[TRAIN_DOOR] for _ in range(3)]
            for row_i, texture in zip(range(3, 7), [door_textures[0], door_textures[0], door_textures[1], door_textures[2]]):
                if row_i == 5 or row_i == 6:  # ドア下部
                    for door_i in range(7, self.CAR_LENGTH, self.CAR_LENGTH // 3):
                        left, right = max(min(front_pos + door_i, env.width), 0), max(min(front_pos + door_i + 5, env.width), 0)
                        env.array[row_i][left: right] = [texture for _ in range(right - left)]
                        partial_write_res.append((row_i, (left, right)))
                else:  # ドア上部
                    for door_i in range(7, self.CAR_LENGTH, self.CAR_LENGTH // 3):
                        textures = [texture, self.TEXTURE[TRAIN_GLASS], texture, self.TEXTURE[TRAIN_GLASS], texture]
                        for col_i, texture in enumerate(textures, start=front_pos + door_i):
                            if 0 <= col_i < env.width:
                                env.array[row_i][col_i] = texture
                                partial_write_res.append((row_i, (col_i, col_i + 1)))
                if car_i == 0:  # 先頭の乗務員用扉
                    left, right = max(min(front_pos + 1, env.width), 0), max(min(front_pos + 3, env.width), 0)
                    env.array[row_i][left: right] = [texture for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                elif car_i == self.car_n - 1:
                    left, right = max(min(front_pos + self.CAR_LENGTH - 2, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
                    env.array[row_i][left: right] = [texture for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                    # ボディが上書きされるので，もう一度ボディを1列描画する
                    left, right = max(min(front_pos + self.CAR_LENGTH, env.width), 0), max(min(front_pos + self.CAR_LENGTH + 1, env.width), 0)
                    env.array[2][left: right] = [self.TEXTURE[TRAIN_TOP] for _ in range(right - left)]  # 車体上部
                    for row_i in range(3, 5):  # 車体中部
                        env.array[row_i][left: right] = [self.TEXTURE[TRAIN_MIDDLE] for _ in range(right - left)]
                        partial_write_res.append((row_i, (left, right)))
                    env.array[5][left: right] = [self.TEXTURE[TRAIN_BELT] for _ in range(right - left)]  # 帯
                    for row_i in range(6, 7):  # 車体下部
                        env.array[row_i][left: right] = [self.TEXTURE[TRAIN_BOTTOM] for _ in range(right - left)]
                        partial_write_res.append((row_i, (left, right)))

                    # 末尾の乗務員用扉
                    left, right = max(min(front_pos + self.CAR_LENGTH - 1, env.width), 0), max(min(front_pos + self.CAR_LENGTH, env.width), 0)
                    env.array[row_i][left: right] = [texture for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))

            for row_i in range(3, 5):  # 窓
                for glass_i in range(14, self.CAR_LENGTH * 2 // 3, self.CAR_LENGTH // 3):
                    left, right = max(min(front_pos + glass_i, env.width), 0), max(min(front_pos + glass_i + 3, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                    left, right = max(min(front_pos + glass_i + 5, env.width), 0), max(min(front_pos + glass_i + 8, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))

                # 前後の窓
                if car_i == 0:
                    left, right = max(min(front_pos + 4, env.width), 0), max(min(front_pos + 6, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                else:
                    left, right = max(min(front_pos + 2, env.width), 0), max(min(front_pos + 5, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                if car_i != self.car_n - 1:
                    left, right = max(min(front_pos + self.CAR_LENGTH - 4, env.width), 0), max(min(front_pos + self.CAR_LENGTH - 1, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))
                else:
                    left, right = max(min(front_pos + self.CAR_LENGTH - 5, env.width), 0), max(min(front_pos + self.CAR_LENGTH - 3, env.width), 0)
                    env.array[row_i][left: right] = [self.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                    partial_write_res.append((row_i, (left, right)))

                # 貫通路
                if car_i != self.car_n - 1:
                    left, right = max(min(front_pos + self.CAR_LENGTH + 1, env.width), 0), max(min(front_pos + self.CAR_LENGTH + 5, env.width), 0)
                    for row_i in range(3, 7):
                        env.array[row_i][left: right] = [self.TEXTURE[GRAY_PARTS] for _ in range(right - left)]
                        partial_write_res.append((row_i, (left, right)))

            # 車輪
            for col_i in range(6, self.CAR_LENGTH, self.CAR_LENGTH * 2 // 3 + 1):
                if 0 <= front_pos + col_i < env.width // 4:
                    env.array[7][front_pos + col_i] = WHEEL_TEXTURES[pos % 2]
                    partial_write_res.append((7, (front_pos + col_i, front_pos + col_i + 1)))
                if 0 <= front_pos + col_i + 4 < env.width // 4:
                    env.array[7][front_pos + col_i + 4] = WHEEL_TEXTURES[pos % 2]
                    partial_write_res.append((7, (front_pos + col_i + 4, front_pos + col_i + 5)))
                # 車輪の1マス後ろをリセット
                if 0 <= front_pos + col_i + 1 < env.width // 4:
                    env.array[7][front_pos + col_i + 1] = EMPTY_TEXTURE
                    partial_write_res.append((7, (front_pos + col_i + 1, front_pos + col_i + 2)))
                if 0 <= front_pos + col_i + 5 < env.width // 4:
                    env.array[7][front_pos + col_i + 5] = EMPTY_TEXTURE
                    partial_write_res.append((7, (front_pos + col_i + 5, front_pos + col_i + 6)))

            # 床下機器
            for col_i in range(18, self.CAR_LENGTH * 2 // 3, 6):
                left, right = max(min(front_pos + col_i, env.width // 4), 0), max(min(front_pos + col_i + 3, env.width // 4), 0)
                env.array[7][left: right] = [BOTTOM_EQUIPMENTS_TEXTURE for _ in range(right - left)]
                partial_write_res.append((7, (front_pos + col_i, front_pos + col_i + 4)))
                # 1マス後ろをリセット
                if 0 <= front_pos + col_i + 4 < env.width // 4:
                    env.array[7][front_pos + col_i + 4] = EMPTY_TEXTURE
                    partial_write_res.append((7, (front_pos + col_i + 4, front_pos + col_i + 5)))
        
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

    def stopping(self, from_x: int, train: Train, base_interval: int = 500):
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

    def leaving(self, to_x: int, train: Train, base_interval: int = 500):
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
