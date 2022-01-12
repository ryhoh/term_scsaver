from typing import List, Tuple

class PartialWriter:
    """
    標準出力上での部分的な書き換えに対応するクラス
    """
    def __init__(self, height: int, width: int):
        # 部分書き込み用
        # 書き換え対象行の，対象範囲を (begin, end) で入れる
        self.line_updated_range = [None for _ in range(height)]
        self.height = height
        self.width = width
        self.array: List[List[str]]

    def partial_write(self):
        print('\033[%sA\r' % (self.height + 1), end='')
        for row_i in range(len(self.array)):
            if self.line_updated_range[row_i] is not None:
                begin, end = self.line_updated_range[row_i]
                # array の範囲外アクセス対策
                begin, end = max(min(begin, self.width - 1), 0), max(min(end, self.width - 1), 0)
                # 書き換え箇所の終わりにカーソル移動
                print('\033[%sC' % end, end='')
                print('\b' * (end - begin), end='')
                print(''.join(self.array[row_i][begin: end]), end='')
                self.line_updated_range[row_i] = None
            print('\033[1B\r', end='')
        print('\033[1B\r', end='')

    def set_line_updated_range(self, row_i: int, update_range: Tuple[int, int]):
        row_i = row_i % self.height
        if self.line_updated_range[row_i] is None:  # その行の更新がまだないなら
            self.line_updated_range[row_i] = update_range
            return None
        # その行に他の更新があるなら，両方の更新の範囲を含む最小の範囲を設定する
        prev_begin, prev_end = self.line_updated_range[row_i]
        self.line_updated_range[row_i] = (min(update_range[0], prev_begin), max(update_range[1], prev_end))
