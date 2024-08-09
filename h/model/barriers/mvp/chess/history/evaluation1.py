import sys
import time
from helpers import *
from psqt import *
from config import *
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

    def evaluate(self, board: chess.Board) -> int:
        if (ae_h5 is None) or (config_json is None) or (encoder_h5 is None):
            return self.eval_side(board, board.turn) - self.eval_side(board, not board.turn)

        if board.turn == chess.BLACK:
            board2 = chess.Board()
            board2.set_fen(flip_fen(board.fen()))
        else:
            board2 = board

        sdb = np.asarray([split_dims(board2)])
        t1 = time.perf_counter()
        pred = ae_h5.predict_on_batch(sdb)
        t2 = time.perf_counter()
        enc = encoder_h5.predict_on_batch(sdb)
        t3 = time.perf_counter()
        barrier = float(config_json["loss"]["max"]) + \
                  (float(config_json["win"]["min"]) - float(config_json["loss"]["max"])) / 2.
        maximum = max(pred[1][0])
        # print(f"t2-t1={t2 - t1}, t3-t2={t3 - t2}")
        # sys.exit()
        for j in range(len(pred[1][0])):
            if pred[1][0][j] == maximum:
                buf = enc[0][1] - barrier
                if buf < 0:
                    return int(100 * buf * float(config_json["win"]["max"]) / barrier)
                else:
                    return int(100 * (buf + float(config_json["win"]["max"]) - barrier))
