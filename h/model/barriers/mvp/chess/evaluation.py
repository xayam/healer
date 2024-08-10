import pprint
import sys
import time
from typing import Tuple

from helpers import *
from psqt import *
# from config import *
import chess


class Evaluation:

    def __init__(self, memory):
        self.memory = memory

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

    def zmb_depth_eval(self, ply, depth, board: chess.Board) -> \
            Tuple[int, int]:
        zmb_value = [0, 28, 27, 26, 25, 24, 23]
        zmb_board = [
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        for color in [False, True]:
            occupied = board.occupied_co[color]
            while occupied:
                square = lsb(occupied)
                piece = board.piece_type_at(square)
                y = square // 8
                x = square % 8
                if color:
                    sign = -1
                else:
                    sign = 1
                zmb_board[y][x] = \
                    sign * zmb_value[piece]
                occupied = poplsb(occupied)
        for y in range(4):
           for x in range(8):
               if x % 2 == 0:
                   zmb_board[y][x] = -zmb_board[y][x]
        for y in range(4, 8):
           for x in range(8):
               if x % 2 == 1:
                   zmb_board[y][x] = -zmb_board[y][x]
        sums = 0
        result = []
        for y in range(4):
            for x in range(4):
                sums += zmb_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4):
            for x in range(4, 8):
                sums += zmb_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4, 8):
            for x in range(4):
                sums += zmb_board[y][x]
        result.append(sums)
        sums = 0
        for y in range(4, 8):
            for x in range(4, 8):
                sums += zmb_board[y][x]
        result.append(sums)
        operations = []
        for i in range(len(result)):
            operations.append([[result[i], 0],
                               *[[0, result[j]]
                                   for j in range(len(result))
                                 if i != j
                               ]
                               ])
        sum1 = 0
        sum2 = 0
        for i in range(len(operations)):
            for j in range(len(operations[i])):
                sum1 += operations[i][j][0]
                sum2 += operations[j][j][1]
        if sum1 == sum2:
            evaluate = 0
        else:
            evaluate = (abs(sum1) + abs(sum2))/(sum1 - sum2)
        return depth + 1, int(100 * evaluate)

    def evaluate(self, ply, alpha: int,
                 beta: int, board: chess.Board) -> list:
        variants = []
        moves = board.legal_moves
        shift = 0
        depth = 1
        shift = 2
        while shift < ply:
            variants.append([[None], [None], [None]])
            number = -1
            for move in moves:
                board.push(move)
                # number += 1
                shift += 1
                depth, eval = self.zmb_depth_eval(ply, depth, board)
                variants.append([depth, shift-number, board.copy(), move, eval])
                board.pop()
        self.memory.append(variants)
        pprint.pprint(variants, width=120)
        diffs = []
        for d in variants:
            if d[-1] not in diffs:
                diffs.append(d[-1])
        try:
            need_find = diffs[2]
        except IndexError:
            return []
        diffs = []
        index = 0
        for d in variants:
            if d[-1] not in diffs:
                diffs.append([d[-1], index])
            index += 1
        diffs = diffs[1:]
        shift = 0
        for d in diffs:
            if d[0] == need_find:
                shift = d[1]
        return self.memory
