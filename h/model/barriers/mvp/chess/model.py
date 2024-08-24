import sys

import winsound

from kan import *
from chess import *
import chess
import chess.syzygy
import itertools

from h.model.utils import utils_progress


class Model:
    def __init__(self):
        self.model = KAN(width=[129, 129, 1], grid=5, k=3, seed=0)
        # dataset = create_dataset(
        #     lambda xx: torch.exp(torch.sin(torch.pi * xx[:, [0]]) + xx[:, [1]] ** 2),
        #     n_var=129
        # )
        # print(dataset['train_input'].shape, dataset['train_label'].shape)
        # results = self.model.fit(dataset, opt="LBFGS",
        #                          steps=20, lamb=0.01,
        #                          lamb_entropy=10.)
        # print(results)

    @staticmethod
    def wdl(fen):
        try:
            with chess.syzygy.open_tablebase("E:/Chess/syzygy/3-4-5-wdl") as tablebase:
                board = chess.Board(fen)
                return tablebase.probe_wdl(board)
        except chess.syzygy.MissingTableError:
            try:
                with chess.syzygy.open_tablebase("E:/Chess/syzygy/6-wdl") as tablebase:
                    board = chess.Board(fen)
                    return tablebase.probe_wdl(board)
            except chess.syzygy.MissingTableError:
                pass
                # winsound.Beep(2500, 4000)
                # raise Exception(fen)


def generate_fen_positions():
    folders = [
        # 'E:/Chess/syzygy/3-4-5-wdl/',
        'E:/Chess/syzygy/6-wdl/'
    ]
    endings = [
        list(f[:-5].split("v")[0] + f[:-5].split("v")[1].lower())
        for folder in folders
        for f in os.listdir(folder) if f.endswith(".rtbw")
    ]
    # print(endings)
    # sys.exit()
    board = chess.Board()
    for ending in endings:
        for positions in itertools.permutations(range(64), len(ending)):
            board.clear()
            valid_position = True
            endgames = []
            for piece, pos in zip(ending, positions):
                if piece == '':
                    continue
                row, col = divmod(pos, 8)
                square = chess.square(col, row)
                if board.piece_at(square) is not None:
                    valid_position = False
                    break
                board.set_piece_at(square, chess.Piece.from_symbol(piece))
            board.turn = chess.WHITE
            if valid_position:
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    endgames.append(fen_positions)
            board.turn = chess.BLACK
            if valid_position:
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    endgames.append(fen_positions)
            board.turn = chess.WHITE
            for s in [A6, B6, C6, D6, E6, F6, G6, H6]:
                board.ep_square = s
                if valid_position:
                    fen_positions = board.fen()
                    if board.is_valid() and fen_positions not in endgames:
                        endgames.append(fen_positions)
            board.turn = chess.BLACK
            for s in [A3, B3, C3, D3, E3, F3, G3, H3]:
                board.ep_square = s
                if valid_position:
                    fen_positions = board.fen()
                    if board.is_valid() and fen_positions not in endgames:
                        endgames.append(fen_positions)
            yield endgames


if __name__ == "__main__":
    m = Model()
    count = 0
    for endgame in generate_fen_positions():
        for fen in endgame:
            count += 1
            utils_progress(f"{str(count).rjust(9, ' ')} | " +
                           f"{str(m.wdl(fen)).rjust(2, ' ')} | {fen}")
    winsound.Beep(2500, 4000)
