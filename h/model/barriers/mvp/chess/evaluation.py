import sys

from helpers import *
import chess

from model.barriers.mvp.chess.psqt import piece_values


def eval_material(board: chess.Board) -> int:
    material = 0
    occupied = board.occupied_co[False]
    while occupied:
        square = lsb(occupied)
        piece = board.piece_type_at(square)
        material -= piece_values[piece]
        occupied = poplsb(occupied)
    occupied = board.occupied_co[True]
    while occupied:
        square = lsb(occupied)
        piece = board.piece_type_at(square)
        material += piece_values[piece]
        occupied = poplsb(occupied)
    # print(board)
    # print(material)
    # input()
    return material


def eval_zmb(board: chess.Board) -> int:
    zmb_value = [0, 6, 5, 4, 3, 2, 1]
    # zmb_value = [0, 1, 2, 3, 4, 5, 6]
    # zmb_value = [0, 1, 2, 3, 5, 8, 13]
    # zmb_value = [0, 100, 100, 100, 100, 100, 100]
    # zmb_value = [0, 10, 32, 33, 50, 90, 1000]
    # zmb_value = [0, 1, 1, 1, 1, 1, 1]
    # zmb_value = [0, 28, 27, 26, 25, 24, 23]
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
            zmb_board[y][x] = sign * zmb_value[piece]
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
        return 0
    else:
        e = (abs(sum1) + abs(sum2)) / (sum2 - sum1)
    return int(100 * e)


def evaluate(board: chess.Board) -> int:
    e = eval_material(board) + eval_zmb(board)
    if board.turn == chess.BLACK:
        return -e
    return e
