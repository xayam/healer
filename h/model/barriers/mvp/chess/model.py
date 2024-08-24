import pickle
import pprint
import random
import sys

import numpy
import winsound
from kan import *
import chess
import chess.syzygy

from h.model.utils import utils_progress
from helpers import poplsb, lsb


class Model:
    def __init__(self):
        self.model = None
        self.dataset = None
        # self.dataset = self.get_data()
        # self.train()
        self.test_model()

    def train(self):
        results = []
        minimum = 10 ** 10
        minimum_layers = 10 ** 10
        minimum_grid = 10 ** 10
        minimum_k = 10 ** 10
        while True:
            hidden_layers = random.choice(list(range(17, 18)))
            grid = random.choice(list(range(31, 32)))
            k = random.choice(list(range(3, 4)))
            self.model = KAN(width=[130, hidden_layers, 1], grid=grid, k=k,
                             seed=0, ckpt_path='./wdl_model')
            result = self.model.fit(self.dataset,
                                    # opt="LBFGS",
                                    steps=20,
                                    # lamb=0.01,
                                    # lamb_entropy=10.
                                    )
            results.append([
                hidden_layers, grid, k,
                result['test_loss'][0] + result['test_loss'][1]
            ])
            results = sorted(results, key=lambda x: x[-1], reverse=True)
            if results[-1][-1] < minimum:
                minimum = results[-1][-1]
                minimum_layers = hidden_layers
                minimum_grid = grid
                minimum_k = k
            utils_progress(f"hidden_layers={minimum_layers} " +
                           f"| grid={minimum_grid} | k={minimum_k} | {minimum}")
            break
        print(results)
        with open(f"wdl_results_0.pkl", mode="wb") as p:
            pickle.dump(results, p)
        lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
        self.model.auto_symbolic(lib=lib)
        formula = self.model.symbolic_formula()[0][0]
        print(formula)

    def get_data(self):  # , fen_position='7K/8/1PR5/8/b6P/8/k7/8 b - - 0 1'
        count = 0
        dataset = {}
        train_inputs = []
        train_labels = []
        test_inputs = []
        test_labels = []
        r = random.choice([0, 1])
        for endgame in self.fen_generator():
            for fen in endgame:
                wdl_score = self.get_wdl(fen)
                if wdl_score is None:
                    continue
                if wdl_score == -2:
                    wdl_score = -1.
                if wdl_score == 2:
                    wdl_score = 1.
                count += 1
                utils_progress(f"{str(count).rjust(9, ' ')} | " +
                               f"{str(self.get_wdl(fen)).rjust(2, ' ')} | {fen}")
                board = chess.Board()
                board.set_fen(fen)
                train_input = [[0., 0.] for _ in range(64)]
                for color in [False, True]:
                    occupied = board.occupied_co[color]
                    while occupied:
                        square = lsb(occupied)
                        piece = board.piece_type_at(square)
                        train_input[square][0] = int(color)
                        train_input[square][1] = piece
                        occupied = poplsb(occupied)
                train_input = [j for i in train_input for j in i]
                if board.ep_square is None:
                    train_input = [0.] + train_input
                else:
                    train_input = [board.ep_square] + train_input
                train_input = [int(board.turn)] + train_input
                if count % 2 == r:
                    test_inputs.append(train_input)
                    test_labels.append([wdl_score])
                else:
                    train_inputs.append(train_input)
                    train_labels.append([wdl_score])
                if count % 2 == 0:
                    r = random.choice([0, 1])
        min_len = min(len(test_inputs), len(train_inputs))
        test_inputs = test_inputs[:min_len]
        test_labels = test_labels[:min_len]
        train_inputs = train_inputs[:min_len]
        train_labels = train_labels[:min_len]
        dataset['train_input'] = torch.FloatTensor(train_inputs)
        dataset['train_label'] = torch.FloatTensor(train_labels)
        dataset['test_input'] = torch.FloatTensor(test_inputs)
        dataset['test_label'] = torch.FloatTensor(test_labels)
        return dataset

    @staticmethod
    def get_wdl(fen_position):
        with chess.syzygy.open_tablebase("E:/Chess/syzygy/3-4-5-get_wdl") as tablebase:
            board = chess.Board(fen_position)
            result = tablebase.get_wdl(board)
        if result is None:
            with chess.syzygy.open_tablebase("E:/Chess/syzygy/6-get_wdl") as tablebase:
                board = chess.Board(fen_position)
                result = tablebase.get_wdl(board)
        return result

    def set_piece(self, state, piece):
        while True:
            pos = random.choice(list(range(64)))
            row, col = divmod(pos, 8)
            sq = chess.square(col, row)
            if state.piece_at(sq) is not None:
                continue
            state.set_piece_at(sq, chess.Piece.from_symbol(piece))
            break
        return state

    def fen_generator(self):
        board = chess.Board()
        count = 0
        while True:
            board.clear()
            endgames = []
            pieces = ['P', 'p', 'N', 'n', 'B', 'b', 'R', 'r', 'Q', 'q']
            for king in ['K', 'k']:
                board = self.set_piece(state=board, piece=king)
            c = random.choice([1, 2, 3, 4])
            for _ in range(c):
                piece = random.choice(pieces)
                board = self.set_piece(state=board, piece=piece)
            board.turn = chess.WHITE
            fen_positions = board.fen()
            if board.is_valid() and fen_positions not in endgames:
                if self.get_wdl(fen_positions) is not None:
                    count += 1
                    endgames.append(fen_positions)
            board.turn = chess.BLACK
            fen_positions = board.fen()
            if board.is_valid() and fen_positions not in endgames:
                if self.get_wdl(fen_positions) is not None:
                    count += 1
                    endgames.append(fen_positions)
            board.turn = chess.WHITE
            for s in [chess.A6, chess.B6, chess.C6, chess.D6,
                      chess.E6, chess.F6, chess.G6, chess.H6]:
                board.ep_square = s
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    if self.get_wdl(fen_positions) is not None:
                        count += 1
                        endgames.append(fen_positions)
            board.turn = chess.BLACK
            for s in [chess.A3, chess.B3, chess.C3, chess.D3,
                      chess.E3, chess.F3, chess.G3, chess.H3]:
                board.ep_square = s
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    if self.get_wdl(fen_positions) is not None:
                        count += 1
                        endgames.append(fen_positions)
            yield endgames
            if count > 10000:
                break

    def test_model(self):
        hidden_layers = 17
        grid = 31
        k = 3
        self.model = KAN(width=[130, hidden_layers, 1], grid=grid, k=k,
                         seed=0, ckpt_path='./wdl_model')
        formula = self.model.symbolic_formula()[0][0]
        print(formula)
        # lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
        # self.model.auto_symbolic(lib=lib)


if __name__ == "__main__":
    m = Model()
    # count = 0
    # for endgame in fen_generator():
    #     for fen in endgame:
    #         count += 1
    #         utils_progress(fen_position"{str(count).rjust(9, ' ')} | " +
    #                        fen_position"{str(m.get_wdl(fen)).rjust(2, ' ')} | {fen}")
    # winsound.Beep(2500, 4000)
