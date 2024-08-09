import init
from src.config import *
from src.model import *
import chess
import chess.engine
import random
import numpy as np
import os


# import matplotlib.pyplot as plt
# import pickle


def stockfish(myboard, depth):
    with chess.engine.SimpleEngine.popen_uci(str_stockfish) as sf:
        result = sf.analyse(myboard, chess.engine.Limit(depth=depth))
        s = result['score'].white().score()
        return s


with open("dataset.epdeval", mode="r") as f:
    epd = f.readlines()

board = chess.Board()


if os.path.exists("./models/last.ckpt"):
    model.load_ckpt(name="last.ckpt", folder="./models")
    print("Model loaded")
elif os.path.exists("../bin/models/last.ckpt"):
    model.load_ckpt(name="last.ckpt", folder="../bin/models")
    print("Model loaded")
else:
    pass
    # raise Exception("Model not found")
count = 0
win = 0
draw = 0
loss = 0

while True:
    white_train = []
    black_train = []
    white_evals_win = []
    white_evals_loss = []
    white_evals_draw = []
    black_evals_win = []
    black_evals_loss = []
    black_evals_draw = []

    count += 1
    print(f"Creating game {count}...")
    e = random.choice(epd)
    fen = " ".join(e.split(" ")[:-1])
    board.set_fen(fen=fen)
    while not board.is_game_over():
        flag = board.turn == chess.WHITE
        fen_old = board.fen()
        fen_curr = fen_old[:]
        if board.turn == chess.BLACK:
            flag = False
            fen_curr = flip_fen(fen_old)
            board.set_fen(fen=fen_curr)
        x_board1 = split_dims(board)
        moves = list(board.legal_moves)
        evals = []
        currs = []
        for m in moves:
            board.push(m)
            x_board2 = split_dims(board)
            x_input = np.asarray([[x_board1, x_board2]], dtype=np.int32)
            predict = ae.predict_on_batch(x_input)
            evaluate = predict[1][0]
            evals.append(evaluate)
            currs.append(m)
            board.pop()
        maximum = -1.
        index = 0
        for j in range(len(evals)):
            if evals[j][0] > maximum:
                maximum = evals[j][0]
                index = j
        board.set_fen(fen=fen_old)
        if len(str(currs[index])) == 5:
            promote = str(currs[index])[4]
        else:
            promote = ""
        black_move = str(currs[index])[0] + \
                     str(9 - int(str(currs[index])[1])) + \
                     str(currs[index])[2] + \
                     str(9 - int(str(currs[index])[3])) + promote
        board.set_fen(fen=fen_old)
        if flag:
            board.push(currs[index])
            white_train.append([x_board1, split_dims(board)])
            white_evals_win.append([1., .0, .0])
            white_evals_draw.append([.0, 1., .0])
            white_evals_loss.append([.0, .0, 1.])
        else:
            board.push(chess.Move.from_uci(black_move))
            black_train.append([x_board1, split_dims(board)])
            black_evals_win.append([1., .0, .0])
            black_evals_draw.append([.0, 1., .0])
            black_evals_loss.append([.0, .0, 1.])

    print(board)
    print(board.result())

    white_train = np.asarray(white_train, dtype=np.float32)
    black_train = np.asarray(black_train, dtype=np.float32)

    white_evals_win = np.asarray(white_evals_win, dtype=np.float32)
    white_evals_draw = np.asarray(white_evals_draw, dtype=np.float32)
    white_evals_loss = np.asarray(white_evals_loss, dtype=np.float32)
    black_evals_win = np.asarray(black_evals_win, dtype=np.float32)
    black_evals_draw = np.asarray(black_evals_draw, dtype=np.float32)
    black_evals_loss = np.asarray(black_evals_loss, dtype=np.float32)

    if board.result() == "1-0":
        win += 1
        ae.fit(white_train, [white_train, white_evals_win],
               epochs=epochs, batch_size=batch_size)
        ae.fit(black_train, [black_train, black_evals_loss],
               epochs=epochs, batch_size=batch_size)
    elif board.result() == "0-1":
        loss += 1
        ae.fit(white_train, [white_train, white_evals_loss],
               epochs=epochs, batch_size=batch_size)
        ae.fit(black_train, [black_train, black_evals_win],
               epochs=epochs, batch_size=batch_size)
    else:
        draw += 1
        ae.fit(white_train, [white_train, white_evals_draw],
               epochs=epochs, batch_size=batch_size)
        ae.fit(black_train, [black_train, black_evals_draw],
               epochs=epochs, batch_size=batch_size)

    model.save_ckpt(name="last.ckpt", folder="./models")
    model.save_ckpt(name="last.ckpt", folder="../bin/models")
    print("Model saved")

    print(f"WIN/DRAW/LOSS={win}/{draw}/{loss}")
