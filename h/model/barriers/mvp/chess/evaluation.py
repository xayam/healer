import pprint
import sys
import time
from helpers import *
from psqt import *
# from config import *
import chess


class Evaluation:
    def eval_side(self, board: chess.Board, color: chess.Color) -> int:
        occupied = board.occupied_co[color]

        material = 0
        psqt = 0

        # loop over all set bits
        while occupied:
            # find the least significant bit
            square = lsb(occupied)

            piece = board.piece_type_at(square)

            # add material
            material += piece_values[piece]

            # add piece square table value
            psqt += (
                list(reversed(psqt_values[piece]))[square]
                if color == chess.BLACK
                else psqt_values[piece][square]
            )

            # remove lsb
            occupied = poplsb(occupied)

        return material + psqt

    def eval_side_zmb(self, board: chess.Board) -> int:
        piece_change = [0, 1, 2, 3, 6, 12, 40]
        my_board = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        for color in [False, True]:
            occupied = board.occupied_co[color]
            while occupied:
                square = lsb(occupied)
                piece = board.piece_type_at(square)
                y = square // 8
                x = square % 8
                print(square, x, y, piece)
                if color:
                    sign = -1
                else:
                    sign = 1
                my_board[y][x] = \
                    sign * piece_change[piece]
                occupied = poplsb(occupied)
        for y in range(4):
           for x in range(8):
               if x % 2 == 0:
                   my_board[y][x] = -my_board[y][x]
        for y in range(4, 8):
           for x in range(8):
               if x % 2 == 1:
                   my_board[y][x] = -my_board[y][x]
        sums = 0
        result = []
        for y in range(4):
            for x in range(4):
                sums += my_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4):
            for x in range(4, 8):
                sums += my_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4, 8):
            for x in range(4):
                sums += my_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4, 8):
            for x in range(4, 8):
                sums += my_board[y][x]
        result.append(sums)

        # pprint.pprint(my_board)
        print(result)
        operations = []
        for i in range(len(result)):
            operations.append([[result[0], 0],
                               [0, result[1]],
                               [0, result[2]],
                               [0, result[3]],
                               ])
        sum1 = 0
        sum2 = 0
        for i in range(len(operations)):
            for j in range(len(operations[i])):
                sum1 += operations[i][j][0]
                sum2 += operations[j][j][1]
        evaluate = (abs(sum1) + abs(sum2))/(sum1 + sum2)
        # print(sum1, sum2, result)
        # sys.exit()
        return int(100 * evaluate)

    def evaluate(self, board: chess.Board) -> int:
        if board.turn:
            eval = self.eval_side_zmb(board)
        else:
            eval = - self.eval_side_zmb(board)
        # print(board)
        # print(board.turn, eval)
        # sys.exit()
        return eval
        # - \
        # self.eval_side(board, not board.turn)
