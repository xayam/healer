import json
import os.path
from multiprocessing import Process
from time import sleep
import concurrent.futures as pool
# import keyboard
from pynput import keyboard
import chess
import chess.engine
import chess.syzygy

from kan import *

from h.model.utils import utils_progress, utils_print


class Model:

    def __init__(self):
        self.stop = None
        self.job = None
        self.params = None
        self.listener = None
        self.process = None
        self.thread = None
        self.commands = None
        self.random = None
        self.model = None
        self.dataset = None
        self.last_fen = None
        self.file_model = None
        self.file_formula = None
        self.pre_model_json = None
        self.model_json = None
        self.model_option = None
        self.lib_formula = None
        self.engine_stockfish = None
        self.syzygy_endgame = None
        self.epd_eval = None
        self.len_input = None
        self.count_limit = None
        self.device = None
        self.dtype = None
        self.formula = None

        self.model_init()

    def model_init(self):
        self.commands = {
            0: {"call": None, "desc": "Exit"},
            1: {"call": self.model_params, "desc": "Search hyperparameters"},
            2: {"call": self.model_finetune, "desc": "Fine-Tune model"},
            3: {"call": self.save_formula, "desc": "Save formula"},
            4: {"call": self.model_test, "desc": "Test model"},
            5: {"call": self.make_predict, "desc": "Make predict"},
        }
        self.stop = False
        self.random = random.SystemRandom(0)
        self.model_option = {
            "hidden_layer": 91,
            "grid": 40,
            "k": 3,
        }
        self.file_model = "model.pth"
        self.file_formula = "model_formula_0.txt"
        self.pre_model_json = "pre_model.json"
        self.model_json = "model.json"
        self.lib_formula = [
            'x', 'x^2', 'x^3', 'x^4', 'exp',
            'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs',
        ]
        self.engine_stockfish = \
            'D:/Work2/PyCharm/SmartEval2/github/src/poler/poler/bin' + \
            '/stockfish-windows-x86-64-avx2.exe'
        self.syzygy_endgame = {
            "wdl345": "E:/Chess/syzygy_endgame/3-4-5-wdl",
            "wdl6": "E:/Chess/syzygy_endgame/6-wdl",
        }
        self.epd_eval = "dataset.epdeval"
        self.len_input = 64 * 12 + 4
        self.count_limit = 48
        self.device = torch.device(
            'cuda' if torch.cuda.is_available() else 'cpu'
        )
        self.dtype = torch.get_default_dtype()

        print(str(self.device).upper(), self.dtype)

        self.formula = self.model_load()

    def start(self):
        while True:
            print("Available commands:")
            for key, value in self.commands.items():
                print(f"   {key}. {value['desc']}")
            try:
                command = int(input("Input command [default 0]: "))
            except ValueError:
                command = 0
            if command not in self.commands.keys():
                command = 0
            if command == 0:
                break
            self.job = self.commands[command]["call"]
            self.params = {}
            self.job()
        # self.process = Process(target=self.executor)
        self.listener = keyboard.Listener(on_release=self.key_release)
        self.listener.start()
        # self.process.start()

    def key_release(self, key):
        if key == keyboard.Key.esc:
            print(key)
            self.stop = True
            return False

    def executor(self):
        with pool.ThreadPoolExecutor(max_workers=1) as e:
            print("123")
            e.submit(self.job, **self.params)
            e.shutdown()

    def save_model(self):
        torch.save(self.model.state_dict(), self.file_model)

    def save_formula(self):
        self.model.auto_symbolic(lib=self.lib_formula)
        formula = self.model.symbolic_formula()[0][0]
        with open(self.file_formula, encoding="UTF-8", mode="w") as p:
            p.write(str(formula).strip())

    def model_load(self):
        print("Loading model...")
        # if os.path.exists(self.model_json):
        #     with open(self.model_json, "r") as f:
        #         self.model_option = json.load(f)
        # else:
        #     with open(self.model_json, "w") as f:
        #         json.dump(self.model_option, f)
        self.model = KAN(
            width=[self.len_input, 13, 8, 4, 2, 1, 1],
            grid=5, k=3, auto_save=False, seed=0
        )
        if os.path.exists(self.file_model):
            self.model.load_state_dict(torch.load(self.file_model))
        if not os.path.exists(self.file_formula):
            return None
        else:
            with open(self.file_formula, encoding="UTF-8", mode="r") as p:
                return str(p.read()).strip()

    def model_finetune(self):
        utils_print("self.model_finetune() starting...")
        while True:
            self.dataset = self.get_data(
                fen_generator=self.get_fen_epd,
                get_score=self.get_score,
                count_limit=self.count_limit
            )
            result = self.model.fit(
                self.dataset, loss_fn=self.loss_function, steps=5,
                metrics=(
                    self.train_accuracy,
                    self.test_accuracy
                )
            )
            utils_print(result['train_accuracy'][-1], result['test_accuracy'][-1])
            utils_print(f"result['test_loss'][0]={result['test_loss'][0]}")
            model.save_model()

    def model_params(self):
        print("self.model_params() starting...")
        self.dataset = self.get_data(
            fen_generator=self.get_fen_epd,
            get_score=self.get_score,
            count_limit=self.count_limit
        )
        if os.path.exists(self.pre_model_json):
            with open(self.pre_model_json, "r") as f:
                self.model_option = json.load(f)
        hidden_layer1 = self.model_option["hidden_layer"]
        grid1 = self.model_option["grid"]
        k1 = self.model_option["k"]
        maxi = 10 ** 10
        maximum_layer = 10 ** 10
        maximum_grid = 10 ** 10
        maximum_k = 10 ** 10
        while True:
            self.model = KAN(
                width=[self.len_input, hidden_layer1, 1],
                grid=grid1, k=k1, auto_save=False, seed=0)
            result = self.model.fit(
                self.dataset, loss_fn=self.loss_function, steps=2,
                metrics=(
                    self.train_accuracy,
                    self.test_accuracy
                )
            )
            if result['test_accuracy'][-1] < maxi:
                maxi = result['test_accuracy'][-1]
                maximum_layer = hidden_layer1
                maximum_grid = grid1
                maximum_k = k1
                with open(self.pre_model_json, "w") as f:
                    data = {"hidden_layer": maximum_layer,
                            "grid": maximum_grid,
                            "k": maximum_k}
                    json.dump(data, f)

            print(result['train_accuracy'][-1], result['test_accuracy'][-1])
            print(f"hidden_layer={maximum_layer}, grid={maximum_grid}, " +
                  f"k={maximum_k}, maxi_test_acc={maxi}")
            print(f"hidden_layer={hidden_layer1}, grid={grid1}, " +
                  f"k={k1}, test_loss={result['test_loss'][0]}")
            # if self.stop:
            #     self.save_model()
            #     break
            hidden_layer1 = self.random.choice(list(range(5, 101)))
            grid1 = self.random.choice(list(range(5, 51)))
            k1 = self.random.choice(list(range(3, 26)))

    @staticmethod
    def loss_function(x, y):
        return torch.abs(torch.mean(x) - torch.mean(y))

    def train_accuracy(self):
        return torch.mean(
            torch.abs(
                self.model(self.dataset['train_input'])[:, 0] -
                self.dataset['train_label'][:, 0]
            ))

    def test_accuracy(self):
        return torch.mean(
            torch.abs(
                self.model(self.dataset['test_input'])[:, 0] -
                self.dataset['test_label'][:, 0]
            ))

    def get_train(self, state1, state2):
        return self.get_input(state1) + self.get_input(state2)

    def get_input(self, state):
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

    def get_data(self, fen_generator, get_score, count_limit):
        count = 0
        count2 = 0
        dataset = {}
        train_inputs = []
        train_labels = []
        test_inputs = []
        test_labels = []
        board = chess.Board()
        for fen in fen_generator(get_score, count_limit):
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
                    f"{str(scores[-1]).rjust(2, ' ')} " +
                    f"| {board.fen()}")
                board.pop()
            if count % 2 == 0:
                for i in range(1, len(boards)):
                    test_input = self.get_train(
                        state1=boards[0], state2=boards[i]
                    )
                    test_inputs.append(test_input)
                    test_labels.append([scores[i] - scores[0]])
                    test_input = self.get_train(
                        state1=boards[i], state2=boards[0]
                    )
                    test_inputs.append(test_input)
                    test_labels.append([scores[0] - scores[i]])
            else:
                for i in range(1, len(boards)):
                    train_input = self.get_train(
                        state1=boards[0], state2=boards[i]
                    )
                    train_inputs.append(train_input)
                    train_labels.append([scores[i] - scores[0]])
                    train_input = self.get_train(
                        state1=boards[i], state2=boards[0]
                    )
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

    def get_wdl(self, fen_position):
        with chess.syzygy.open_tablebase(
                self.syzygy_endgame["wdl345"]
        ) as tablebase:
            board = chess.Board(fen_position)
            result = tablebase.get_wdl(board)
        if result is None:
            with chess.syzygy.open_tablebase(
                    self.syzygy_endgame["wdl6"]
            ) as tablebase:
                board = chess.Board(fen_position)
                result = tablebase.get_wdl(board)
        return result

    def set_piece(self, state, piece):
        while True:
            pos = self.random.choice(list(range(64)))
            row, col = divmod(pos, 8)
            sq = chess.square(col, row)
            if state.piece_at(sq) is not None:
                continue
            state.set_piece_at(sq, chess.Piece.from_symbol(piece))
            break
        return state

    def get_score(self, state, depth=10):
        with chess.engine.SimpleEngine.popen_uci(self.engine_stockfish) as sf:
            result = sf.analyse(state, chess.engine.Limit(depth=depth))
            # if state.turn == chess.WHITE:
            score = result['score'].white().score()
            # else:
            #     score = result['score'].black().score()
            return score

    def get_fen_epd(self, get_score, count_limit):
        with open(self.epd_eval, mode="r") as f:
            dataevals = f.readlines()
        fens = []
        for _ in range(count_limit):
            dataeval = str(self.random.choice(dataevals)).strip()
            spl = dataeval.split(" ")
            fen = " ".join(spl[:-1])
            fens.append(fen)
        return fens

    def get_fen_random(self, get_score, count_limit):
        board = chess.Board()
        count = 0
        endgames = []
        pieces = ['P', 'p', 'N', 'n', 'B', 'b', 'R', 'r', 'Q', 'q']
        for _ in range(count_limit):
            board.clear()
            for king in ['K', 'k']:
                board = self.set_piece(state=board, piece=king)
            c = self.random.choice([1, 2, 3, 4])
            for _ in range(c):
                piece = self.random.choice(pieces)
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
            utils_progress(f"{count}/{count_limit} | {fen_positions}")
        return endgames

    def model_test(self):
        print("self.model_test() starting...")
        # self.dataset = self.get_data(
        #     fen_generator=self.get_fen_random,
        #     get_score=self.get_wdl,
        #     count_limit=4
        # )
        print(self.formula)

    def make_predict(self):
        print("self.make_predict() starting...")
        fens = list(self.get_fen_epd(
            get_score=self.get_score, count_limit=1
        ))
        board1 = chess.Board()
        board1.set_fen(fens[0])
        board2 = chess.Board()
        board2.set_fen(fens[1])
        inp = self.get_train(state1=board1, state2=board2)
        variable_values = {
            f"x_{i}": inp[i - 1]
            for i in range(self.len_input, 0, -1)
        }
        formula = self.model_load()
        print(formula)
        for _var, _val in variable_values.items():
            formula = str(formula).replace(_var, str(_val))
        result = eval(formula)
        print(result)
        print(self.get_score(board2) - self.get_score(board1))
        print(fens[0])
        print(fens[1])


if __name__ == "__main__":
    model = Model()
    model.start()
