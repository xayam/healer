import chess
import numpy as np

str_stockfish = '../bin/stockfish-windows-x86-64-avx2.exe'

count_game = 1
epochs = 1
hidden_dim = 5
batch_size = 1
draw_barrier = 100
count_class = 2

squares_index = {
    'a': 0,
    'b': 1,
    'c': 2,
    'd': 3,
    'e': 4,
    'f': 5,
    'g': 6,
    'h': 7
}


def square_to_index(square):
    letter = chess.square_name(square)
    return 8 - int(letter[1]), squares_index[letter[0]]


def split_dims(myboard):
    board3d = np.zeros((8, 8, 16), dtype=np.float32)
    for piece in chess.PIECE_TYPES:
        for square in myboard.pieces(piece, chess.WHITE):
            idx = np.unravel_index(square, (8, 8))
            board3d[7 - idx[0]][idx[1]][piece - 1] = 1
        for square in myboard.pieces(piece, chess.BLACK):
            idx = np.unravel_index(square, (8, 8))
            board3d[7 - idx[0]][idx[1]][piece + 5] = 1
    aux = myboard.turn
    myboard.turn = chess.WHITE
    for move in myboard.legal_moves:
        ii, jj = square_to_index(move.to_square)
        board3d[ii][jj][12] = 1
    myboard.turn = chess.BLACK
    for move in myboard.legal_moves:
        ii, jj = square_to_index(move.to_square)
        board3d[ii][jj][13] = 1
    myboard.turn = aux
    if myboard.has_kingside_castling_rights(chess.WHITE):
        board3d[7][7][14] = 1
        board3d[7][4][14] = 1
    if myboard.has_queenside_castling_rights(chess.WHITE):
        board3d[7][0][14] = 1
        board3d[7][4][14] = 1
    if myboard.has_kingside_castling_rights(chess.BLACK):
        board3d[0][7][14] = 1
        board3d[0][4][14] = 1
    if myboard.has_queenside_castling_rights(chess.BLACK):
        board3d[0][0][14] = 1
        board3d[0][4][14] = 1
    if myboard.has_legal_en_passant():
        idx = np.unravel_index(myboard.ep_square, (8, 8))
        board3d[7 - idx[0]][idx[1]][15] = 1

    return board3d


def flip_fen(fen):
    split = fen.split()
    split[1] = "w"

    buf = ""
    replacer = {"-": "-",
                "Q": "q", "q": "Q",
                "K": "k", "k": "K"}
    for c in split[2]:
        buf += replacer[c]
    buf2 = ""
    if "K" in buf:
        buf2 += "K"
    if "Q" in buf:
        buf2 += "Q"
    if "k" in buf:
        buf2 += "k"
    if "q" in buf:
        buf2 += "q"
    if buf2 == "":
        buf2 = "-"
    split[2] = buf2

    if len(split[3]) == 2:
        split[3] = split[3][0] + '6'

    split[0] = split[0].replace("2", "11")
    split[0] = split[0].replace("3", "111")
    split[0] = split[0].replace("4", "1111")
    split[0] = split[0].replace("5", "11111")
    split[0] = split[0].replace("6", "111111")
    split[0] = split[0].replace("7", "1111111")
    split[0] = split[0].replace("8", "11111111")
    pos = split[0].split("/")
    for i in range(4):
        buf = pos[i]
        pos[i] = pos[7 - i]
        pos[7 - i] = buf
    split[0] = "/".join(pos)
    split[0] = split[0].replace("11111111", "8")
    split[0] = split[0].replace("1111111", "7")
    split[0] = split[0].replace("111111", "6")
    split[0] = split[0].replace("11111", "5")
    split[0] = split[0].replace("1111", "4")
    split[0] = split[0].replace("111", "3")
    split[0] = split[0].replace("11", "2")
    buf = ""
    replacer = {"1": "1", "2": "2", "3": "3", "4": "4",
                "5": "5", "6": "6", "7": "7", "8": "8", "/": "/",
                "P": "p", "p": "P",
                "N": "n", "n": "N",
                "B": "b", "b": "B",
                "R": "r", "r": "R",
                "Q": "q", "q": "Q",
                "K": "k", "k": "K"}
    for c in split[0]:
        buf += replacer[c]
    split[0] = buf
    fen = " ".join(split)
    return fen
