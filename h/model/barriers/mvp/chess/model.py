import os.path
import pickle
import datetime
import random

import torch
from kan import *
import chess.engine
import chess
import chess.syzygy

from h.model.utils import utils_progress
from helpers import poplsb, lsb


class Model:
    COUNT_FEN_LIMIT = 5000

    def __init__(self):
        self.model = None
        self.dataset = None
        self.last_fen = None
        self.state_model = "model.pth"
        self.file_formula = "model_formula_0.txt"
        self.lib = ['x', 'x^2', 'x^3', 'x^4', 'exp',
                    'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs'
                   ]
        self.len_input = 772
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.get_default_dtype()
        print(self.device, self.dtype)

        self.model = KAN(
            width=[self.len_input, 91, 1],
            grid=40, k=3, auto_save=False, seed=0)
        if os.path.exists(self.state_model):
            self.model.load_state_dict(torch.load(self.state_model))


    def start(self):
        self.search_params()
        # self.train()
        # self.test_model()
        # self.predict()
    def train(self):
        results = []
        while True:
            self.dataset = self.get_data(
                fen_generator=self.get_fen,
                get_score=self.get_score,
                limit=5000
            )
            result = self.model.fit(self.dataset,
                                    lamb=0.01, lamb_entropy=10,
                                    # metrics=(self.train_acc, self.test_acc),
                                    steps=5)
            print(result['train_acc'][-1], result['test_acc'][-1])
            results.append([
                result['test_loss'][0] + result['test_loss'][1]
            ])
            results = sorted(results, key=lambda xx: xx[-1], reverse=True)
            utils_progress(f"results[-1][-1]={results[-1][-1]}")
            print("Saving ckpt...")
            self.model.saveckpt("./ckpts/wdl_model_" +
                                str(datetime.datetime.now()).
                                replace(":", "-").replace(".", "-").
                                replace(" ", "-").replace("-", "_"))
            lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
            self.model.auto_symbolic(lib=lib)
            formula = self.model.symbolic_formula()[0][0]
            with open(f"wdl_formula_0.txt", encoding="UTF-8", mode="w") as p:
                p.write(str(formula).strip())
            break

    def search_params(self):
        self.dataset = self.get_data(
            fen_generator=self.get_fen,
            get_score=self.get_score,
            limit=48 // 4
        )
        results = []
        maxi = 10 ** 10
        maximum_layer = 10 ** 10
        maximum_grid = 10 ** 10
        maximum_k = 10 ** 10
        while True:
            rnd = random.SystemRandom(0)
            hidden_layer1 = rnd.choice(list(range(91, 92)))
            grid1 = rnd.choice(list(range(40, 41)))
            k1 = rnd.choice(list(range(3, 4)))
            self.model = KAN(
                width=[self.len_input, hidden_layer1, 1],
                grid=grid1, k=k1, auto_save=False, seed=0)
            self.model.load_state_dict(torch.load(self.state_model))
            result = self.model.fit(self.dataset,
                                    loss_fn=self.loss_fn,
                                    metrics=(self.train_acc, self.test_acc),
                                    steps=2)
            self.model.auto_symbolic(lib=self.lib)
            formula = self.model.symbolic_formula()[0][0]
            with open(self.file_formula, encoding="UTF-8", mode="w") as p:
                p.write(str(formula).strip())
            torch.save(self.model.state_dict(), self.state_model)
            # print(result['test_loss'])
            results.append([hidden_layer1, grid1, k1,
                            result['test_loss'][0]
            ])
            if result['test_acc'][-1] < maxi:
                maxi = result['test_acc'][-1]
                maximum_layer = hidden_layer1
                maximum_grid = grid1
                maximum_k = k1
            print()
            print(result['train_acc'][-1], result['test_acc'][-1])
            print(f"hidden_layer={maximum_layer}, grid={maximum_grid}, k={maximum_k}, " +
                  f"{maxi}"
                  )
            print(f"hidden_layer={hidden_layer1}, grid={grid1}, k={k1}, {results[-1][-1]}")
            break


    def loss_fn(self, x, y):
        return torch.abs(torch.mean(x) - torch.mean(y))

    def train_acc(self):
        return torch.mean(
            torch.abs(
             self.model(self.dataset['train_input'])[:, 0] -
             self.dataset['train_label'][:, 0]
            ))

    def test_acc(self):
        return torch.mean(
            torch.abs(
                self.model(self.dataset['test_input'])[:, 0] -
                self.dataset['test_label'][:, 0]
            ))

    def get_train(self, state1, state2):
        return self.get_state_data(state1) + self.get_state_data(state2)

    def get_state_data(self, state):
        train_input = [[0.] * 64 for _ in range(12)]
        for piece in chess.PIECE_TYPES:
            for square in state.pieces(piece, chess.BLACK):
                train_input[piece - 1][square] = -piece
                for move in state.pseudo_legal_moves:
                    if move.from_square == square:
                        train_input[piece - 1][move.to_square] = -piece
        for piece in chess.PIECE_TYPES:
            for square in state.pieces(piece, chess.WHITE):
                train_input[piece + 5][square] = piece
                for move in state.pseudo_legal_moves:
                    if move.from_square == square:
                        train_input[piece + 5][move.to_square] = piece
        train_input = [j for i in train_input for j in i]
        if state.has_kingside_castling_rights(state.turn):
            train_input = [1.] + train_input
        else:
            train_input = [0.] + train_input
        if state.has_kingside_castling_rights(state.turn):
            train_input = [1.] + train_input
        else:
            train_input = [0.] + train_input
        if state.ep_square is None:
            train_input = [0.] + train_input
        else:
            train_input = [state.ep_square] + train_input
        train_input = [int(state.turn)] + train_input
        return train_input[:self.len_input // 2]

    def get_data(self, fen_generator, get_score, limit):
        count = 0
        count2 = 0
        dataset = {}
        train_inputs = []
        train_labels = []
        test_inputs = []
        test_labels = []
        board = chess.Board()
        for fen in fen_generator(get_score, limit):
            scores = []
            boards = []
            try:
                board.set_fen(fen)
                score = get_score(board)
                if score is None:
                    continue
            except chess.engine.EngineError:
                continue
            except chess.IllegalMoveError:
                continue
            scores.append(score)
            boards.append(board.copy())
            count += 1
            moves = board.legal_moves
            for move in moves:
                try:
                    board.push(move)
                    score = get_score(board)
                    if score is None:
                        board.pop()
                        continue
                except chess.engine.EngineError:
                    break
                except chess.IllegalMoveError:
                    break
                scores.append(score)
                boards.append(board.copy())
                count2 += 1
                utils_progress(
                    f"{str(count).rjust(5, ' ')} | " +
                    f"{str(count2).rjust(5, ' ')} | " +
                    f"{str(scores[-1]).rjust(2, ' ')} | {board.fen()}")
                board.pop()
            if count % 2 == 0:
                for i in range(1, len(boards)):
                    test_input = self.get_train(state1=boards[0], state2=boards[i])
                    test_inputs.append(test_input)
                    test_labels.append([scores[i] - scores[0]])
                    test_input = self.get_train(state1=boards[i], state2=boards[0])
                    test_inputs.append(test_input)
                    test_labels.append([scores[0] - scores[i]])
            else:
                for i in range(1, len(boards)):
                    train_input = self.get_train(state1=boards[0], state2=boards[i])
                    train_inputs.append(train_input)
                    train_labels.append([scores[i] - scores[0]])
                    train_input = self.get_train(state1=boards[i], state2=boards[0])
                    train_inputs.append(train_input)
                    train_labels.append([scores[0] - scores[i]])
        print()
        min_len = min(len(test_inputs), len(train_inputs),
                      len(test_labels), len(train_labels),
                      )
        test_inputs = test_inputs[:min_len]
        test_labels = test_labels[:min_len]
        train_inputs = train_inputs[:min_len]
        train_labels = train_labels[:min_len]
        dataset['train_input'] = \
            torch.FloatTensor(train_inputs).type(self.dtype).to(self.device)
        dataset['train_label'] = \
            torch.FloatTensor(train_labels).type(self.dtype).to(self.device)
        dataset['test_input'] = \
            torch.FloatTensor(test_inputs).type(self.dtype).to(self.device)
        dataset['test_label'] = \
            torch.FloatTensor(test_labels).type(self.dtype).to(self.device)
        return dataset

    @staticmethod
    def get_wdl(fen_position):
        with chess.syzygy.open_tablebase("E:/Chess/syzygy/3-4-5-wdl") as tablebase:
            board = chess.Board(fen_position)
            result = tablebase.get_wdl(board)
        if result is None:
            with chess.syzygy.open_tablebase("E:/Chess/syzygy/6-wdl") as tablebase:
                board = chess.Board(fen_position)
                result = tablebase.get_wdl(board)
        return result

    @staticmethod
    def set_piece(state, piece):
        while True:
            pos = random.choice(list(range(64)))
            row, col = divmod(pos, 8)
            sq = chess.square(col, row)
            if state.piece_at(sq) is not None:
                continue
            state.set_piece_at(sq, chess.Piece.from_symbol(piece))
            break
        return state

    @staticmethod
    def get_score(state, depth=10):
        str_stockfish = 'D:/Work2/PyCharm/SmartEval2/github/src/poler/poler/bin' + \
                        '/stockfish-windows-x86-64-avx2.exe'
        with chess.engine.SimpleEngine.popen_uci(str_stockfish) as sf:
            result = sf.analyse(state, chess.engine.Limit(depth=depth))
            # if state.turn == chess.WHITE:
            score = result['score'].white().score()
            # else:
            #     score = result['score'].black().score()
            return score


    def get_fen(self, get_score, limit):
        with open("dataset.epdeval", mode="r") as f:
            dataevals = f.readlines()
        fens = []
        for _ in range(limit):
            for _ in range(4):
                dataeval = str(random.choice(dataevals)).strip()
                spl = dataeval.split(" ")
                fen = " ".join(spl[:-1])
                fens.append(fen)
        return fens


    def fen_generator(self, get_score, limit):
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
                if get_score(fen_positions) is not None:
                    count += 1
                    endgames.append(fen_positions)
            board.turn = chess.BLACK
            fen_positions = board.fen()
            if board.is_valid() and fen_positions not in endgames:
                if get_score(fen_positions) is not None:
                    count += 1
                    endgames.append(fen_positions)
            board.turn = chess.WHITE
            for s in [chess.A6, chess.B6, chess.C6, chess.D6,
                      chess.E6, chess.F6, chess.G6, chess.H6]:
                board.ep_square = s
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    if get_score(fen_positions) is not None:
                        count += 1
                        endgames.append(fen_positions)
            board.turn = chess.BLACK
            for s in [chess.A3, chess.B3, chess.C3, chess.D3,
                      chess.E3, chess.F3, chess.G3, chess.H3]:
                board.ep_square = s
                fen_positions = board.fen()
                if board.is_valid() and fen_positions not in endgames:
                    if get_score(fen_positions) is not None:
                        count += 1
                        endgames.append(fen_positions)
            yield endgames
            if count > limit:
                break

    def test_model(self):
        hidden_layers = 17
        grid = 31
        k = 3
        self.model = KAN(width=[130, hidden_layers, 1], grid=grid, k=k,
                         seed=0, ckpt_path='./wdl_model')
        print("Loading formula...")
        with open(f"wdl_formula_0.txt", encoding="UTF-8", mode="r") as p:
            formula1 = p.read()
        print("Loading state...")
        with open(f"wdl_state_0.pkl", mode="rb") as p:
            self.model.__setstate__(pickle.load(p))
        self.dataset = self.get_data(
            fen_generator=self.fen_generator,
            get_score=self.get_wdl,
            limit=100
        )
        self.model.fit(self.dataset, steps=2)
        lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
        self.model.auto_symbolic(lib=lib)
        formula2 = self.model.symbolic_formula()[0][0]
        print(str(formula1 == formula2))
        with open(f"wdl_formula_1.txt", encoding="UTF-8", mode="w") as p:
            p.write(formula2)

    def predict(self):
        fens = list(self.get_fen(get_score=self.get_score, limit=1))
        board1 = chess.Board()
        board1.set_fen(fens[0])
        board2 = chess.Board()
        board2.set_fen(fens[1])
        inp = self.get_train(state1=board1, state2=board2)
        variable_values = {
            f"x_{i}": inp[i - 1]
            for i in range(self.len_input, 0, -1)
        }
        if not os.path.exists(self.file_formula):
            raise f"Path not exists: '{self.file_formula}'"
        else:
            with open(self.file_formula, encoding="UTF-8", mode="r") as p:
                formula = str(p.read()).strip()
        print(formula)
        for var, val in variable_values.items():
            formula = str(formula).replace(var, str(val))
        result = eval(formula)
        print(result)
        print(self.get_score(board2) - self.get_score(board1))
        print(fens[0], fens[1])


if __name__ == "__main__":
    model = Model()
    model.start()
