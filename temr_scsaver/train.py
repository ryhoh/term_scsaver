from os import system
from random import randrange, sample
import shutil
import sys
from time import sleep
from typing import Any, Final


EMPTY       = 0
PLATFORM    = 1
TRAIN_BASE  = 0
TRAIN_COLOR = 1
TRAIN_GLASS = 2
TRAIN_DOOR  = 3
GRAY_PARTS  = 4
ACCENT_COLOR = 5

EMPTY_TEXTURE = " "
PLATFORM_TEXTURE = "█"
WHEEL_TEXTURE = "\u001b[02;39m●\u001b[00m"


class Train:
    def put(self, env: "Environment", pos: int = 0):
        raise NotImplementedError


class Odakyu(Train):
    TEXTURE = [
        "\u001b[00;37m█\u001b[00m",
        "\u001b[00;34m█\u001b[00m",
        "\u001b[01;36m█\u001b[00m",
        "\u001b[02;37m█\u001b[00m",
        "\u001b[02;39m█\u001b[00m",
    ]
    CAR_LENGTH = 18 * 3 - 1  # メートル * 定数 - 調整項


class Keihan(Train):
    TEXTURE = [
        "\u001b[00;37m█\u001b[00m",
        "\u001b[02;32m█\u001b[00m",
        "\u001b[01;36m█\u001b[00m",
        "\u001b[02;37m█\u001b[00m",
        "\u001b[02;39m█\u001b[00m",
        "\u001b[00;32m█\u001b[00m",
    ]
    CAR_LENGTH = 18 * 3 - 1  # メートル * 定数 - 調整項

    def put(self, env: "Environment", pos: int = 0):
        """
        電車を位置 pos に配置する
        pos は，プラットフォーム上の停止位置を原点とした数直線

        （京阪っぽいカラーリング）
        """
        # 背景をリセットする
        env.array[: 7] = [[EMPTY_TEXTURE for _ in range(env.width)] for _ in range(7)]
        env.array[7] = [EMPTY_TEXTURE for _ in range(env.width // 4)] + [PLATFORM_TEXTURE for _ in range(env.width * 3 // 4)]

        # 車両
        front_pos = env.platform_range[0] + 1 + pos
        for row_i in range(2, 5):  # 車体上部
            left, right = max(min(front_pos, env.width), 0), max(min(front_pos + Keihan.CAR_LENGTH, env.width), 0)
            env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_COLOR] for _ in range(right - left)]
        for row_i in range(5, 7):  # 車体下部
            left, right = max(min(front_pos, env.width), 0), max(min(front_pos + Keihan.CAR_LENGTH, env.width), 0)
            env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_BASE] for _ in range(right - left)]
        # 帯
        left, right = max(min(front_pos, env.width), 0), max(min(front_pos + Keihan.CAR_LENGTH, env.width), 0)
        env.array[5][left: right] = [Keihan.TEXTURE[ACCENT_COLOR] for _ in range(right - left)]
        # パンタグラフ
        if 0 <= front_pos + 10 < env.width:
            env.array[0][front_pos + 10] = "\u001b[02;39m▗\u001b[00m"
            env.array[1][front_pos + 10] = "\u001b[02;39m▚\u001b[00m"
        
        for row_i in range(3, 7):  # ドア
            if row_i == 5 or row_i == 6:  # ドア下部
                for door_i in range(7, Keihan.CAR_LENGTH, Keihan.CAR_LENGTH // 3):
                    left, right = max(min(front_pos + door_i, env.width), 0), max(min(front_pos + door_i + 5, env.width), 0)
                    env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_DOOR] for _ in range(right - left)]
            else:  # ドア上部
                for door_i in range(7, Keihan.CAR_LENGTH, Keihan.CAR_LENGTH // 3):
                    textures = [Keihan.TEXTURE[TRAIN_DOOR], Keihan.TEXTURE[TRAIN_GLASS], Keihan.TEXTURE[GRAY_PARTS], Keihan.TEXTURE[TRAIN_GLASS], Keihan.TEXTURE[TRAIN_DOOR]]
                    for col_i, texture in enumerate(textures, start=front_pos + door_i):
                        if 0 <= col_i < env.width:
                            env.array[row_i][col_i] = texture
            # 乗務員用扉
            left, right = max(min(front_pos + 1, env.width), 0), max(min(front_pos + 3, env.width), 0)
            env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_DOOR] for _ in range(right - left)]

        for row_i in range(3, 5):  # 窓
            for glass_i in range(14, Keihan.CAR_LENGTH * 2 // 3, Keihan.CAR_LENGTH // 3):
                left, right = max(min(front_pos + glass_i, env.width), 0), max(min(front_pos + glass_i + 3, env.width), 0)
                env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
                left, right = max(min(front_pos + glass_i + 5, env.width), 0), max(min(front_pos + glass_i + 8, env.width), 0)
                env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]

            # 前後の窓
            left, right = max(min(front_pos + 4, env.width), 0), max(min(front_pos + 6, env.width), 0)
            env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]
            left, right = max(min(front_pos + Keihan.CAR_LENGTH - 5, env.width), 0), max(min(front_pos + Keihan.CAR_LENGTH - 2, env.width), 0)
            env.array[row_i][left: right] = [Keihan.TEXTURE[TRAIN_GLASS] for _ in range(right - left)]

        for col_i in range(6, Keihan.CAR_LENGTH, Keihan.CAR_LENGTH * 2 // 3 + 1):
            if 0 <= front_pos + col_i < env.width // 4:
                env.array[7][front_pos + col_i] = WHEEL_TEXTURE
            if 0 <= front_pos + col_i + 4 < env.width // 4:
                env.array[7][front_pos + col_i + 4] = WHEEL_TEXTURE


class Environment:
    def __init__(self, width: int) -> None:
        self.width: Final[int] = width // 4 * 4
        self.array = [[EMPTY_TEXTURE for _ in range(width)] for _ in range(7)]
        self.array.extend([
            [EMPTY_TEXTURE for _ in range(width // 4)] + [PLATFORM_TEXTURE for _ in range(width * 3 // 4)]
            # + [TEXTURE[EMPTY] for _ in range(width // 4)]
        ])
        self.height = len(self.array)
        # self.array.extend([
        #     [TEXTURE[EMPTY] for _ in range(width)]
        # ])
        # プラットフォームの範囲
        self.platform_range = (width // 4, width * 3 // 4 - 1)
        # プラットフォームの足
        # self.array[7][self.platform_range[0]] \
        #     = self.array[7][self.platform_range[0] + 1] \
        #     = self.array[7][self.platform_range[1]] \
        #     = self.array[7][self.platform_range[1] - 1] \
        #     = TEXTURE[PLATFORM]
        self.line_is_updated = [False for _ in range(len(self.array))]


    def __str__(self) -> str:
        return '%s\n' % ('\n'.join(''.join(row) for row in self.array))

    def partial_write(self):
        print('\033[7A\r', end='')
        for i in range(len(self.array)):
            if self.line_is_updated[i]:
                print(''.join(self.array[i]), end='')
                self.line_is_updated[i] = False
            print('\033[1B\r', end='')
        # print('\033[%sA\r%s\n\033[%sB' % (row_shift, ''.join(self.array[update_line]), row_shift), end='')

    def set_into_array(self, y: int, x: int, val: Any):
        if y < 0 or self.height <= y or x < 0 or self.width <= x:
            return None
        self.array[y][x] = val

    # def odakyu(self, pos: int = 0):
    #     """
    #     電車を位置 pos にセットする
    #     pos は，プラットフォーム上の停止位置を原点とした数直線

    #     （小田急っぽいカラーリング．作りかけ）
    #     """
    #     front_pos = self.platform_range[0] + 1 + pos
    #     for height_i in range(2, 7):  # 車体
    #         if height_i != 5:
    #             self.array[height_i][front_pos: front_pos + CAR_LENGTH] = [TEXTURE[TRAIN_BASE] for _ in range(CAR_LENGTH)]
    #     for height_i in range(3, 7):  # ドア
    #         for door_i in range(7, CAR_LENGTH, CAR_LENGTH // 3):
    #             self.array[height_i][front_pos + door_i: front_pos + door_i + 5] = [TEXTURE[TRAIN_DOOR] for _ in range(5)]
    #             self.array[height_i][front_pos + door_i + 2] = TEXTURE[GRAY_PARTS]
    #     # 帯
    #     self.array[5][front_pos: front_pos + CAR_LENGTH] = [TEXTURE[TRAIN_LINE] for _ in range(CAR_LENGTH)]
    #     # 窓
    #     for height_i in range(3, 5):  # ドア
    #         for glass_i in range(14, CAR_LENGTH * 2 // 3, CAR_LENGTH // 3):
    #             self.array[height_i][front_pos + glass_i: front_pos + glass_i + 8] = [TEXTURE[TRAIN_GLASS] for _ in range(8)]

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
            train.put(self, x)
            system('clear')
            print(self)
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
            train.put(self, x)
            system('clear')
            print(self)
            if x != to_x:
                t = (2 * -x / a) ** 0.5
                next_t = (2 * (-x+1) / a) ** 0.5
                sleep((next_t - t) * base_interval / 1000)
                t = next_t


def train():
    while True:
        width = shutil.get_terminal_size().columns
        width -= 1
        env = Environment(width)
        train = Keihan()
        env.stopping(50, train)
        sleep(2)
        env.leaving(-100, train)
        sleep(5)
        # system('clear')
        # print('\n' * shutil.get_terminal_size().lines)  # ターミナル画面の下に押し付けないと，カーソル移動による描画処理が正しく行われない
        # break


if __name__ == '__main__':
    train()
