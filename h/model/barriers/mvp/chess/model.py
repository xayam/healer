import json
import os.path

from kan import *

import chess
import chess.engine
import chess.syzygy

from h.model.utils import utils_progress


class Model:

    def __init__(self):
        self.random = None
        self.model = None
        self.dataset = None
        self.last_fen = None
        self.state_model = None
        self.file_formula = None
        self.pre_model_json = None
        self.model_json = None
        self.model_option = None
        self.lib = None
        self.str_stockfish = None
        self.syzygy = None
        self.epdeval = None
        self.len_input = None
        self.limit = None
        self.device = None
        self.dtype = None
        self.formula = None

        self.init_model()

    def init_model(self):
        self.random = random.SystemRandom(0)
        self.state_model = "model.pth"
        self.file_formula = "model_formula_0.txt"
        self.pre_model_json = "pre_model.json"
        self.model_json = "model.json"
        self.lib = ['x', 'x^2', 'x^3', 'x^4', 'exp',
                    'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs'
                    ]
        self.str_stockfish = 'D:/Work2/PyCharm/SmartEval2/github/src/poler/poler/bin' + \
                             '/stockfish-windows-x86-64-avx2.exe'
        self.syzygy = {
            "wdl345": "E:/Chess/syzygy/3-4-5-wdl",
            "wdl6": "E:/Chess/syzygy/6-wdl",
        }
        self.epdeval = "dataset.epdeval"
        self.len_input = 64 * 12 + 4
        self.limit = 48 // 4
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.get_default_dtype()

        print(str(self.device).upper(), self.dtype)

        self.formula = self.load_model()

    def start(self):
        commands = {
            1: {"call": self.search_params, "desc": "Search params"},
            2: {"call": self.finetune_model, "desc": "Fine-Tune model"},
            3: {"call": self.test_model, "desc": "Test model"},
            4: {"call": self.make_predict, "desc": "Make predict"},
        }
        print("Available commands:")
        for key, value in commands.items():
            print(f"   {key}. {value['desc']}")
        try:
            command = int(input("Choice command [default 1]: "))
        except ValueError:
            command = 1
        if command not in commands.keys():
            command = 1

        commands[command]["call"]()

    def save_model(self):
        torch.save(self.model.state_dict(), self.state_model)
        self.model.auto_symbolic(lib=self.lib)
        formula = self.model.symbolic_formula()[0][0]
        with open(self.file_formula, encoding="UTF-8", mode="w") as p:
            p.write(str(formula).strip())

    def load_model(self):
        print("Loading model...")
        self.model_option = {
            "hidden_layer": 91,
            "grid": 40,
            "k": 3,
        }
        if os.path.exists(self.model_json):
            with open(self.model_json, "r") as f:
                self.model_option = json.load(f)
        else:
            with open(self.model_json, "w") as f:
                json.dump(self.model_option, f)
        self.model = KAN(
            width=[self.len_input, self.model_option["hidden_layer"], 1],
            grid=self.model_option["grid"],
            k=self.model_option["k"], auto_save=False, seed=0)
        if os.path.exists(self.state_model):
            self.model.load_state_dict(torch.load(self.state_model))
        if not os.path.exists(self.file_formula):
            return None
        else:
            with open(self.file_formula, encoding="UTF-8", mode="r") as p:
                return str(p.read()).strip()

    def finetune_model(self):
        print("self.finetune_model() starting...")
        while True:
            self.dataset = self.get_data(
                fen_generator=self.get_fen,
                get_score=self.get_score,
                _limit=self.limit
            )
            result = self.model.fit(self.dataset,
                                    loss_fn=self.loss_func,
                                    metrics=(self.train_acc, self.test_acc),
                                    steps=20)
            print(result['train_acc'][-1], result['test_acc'][-1])
            utils_progress(f"result['test_loss'][0]={result['test_loss'][0]}")
            self.save_model()


    def search_params(self):
        print("self.search_params() starting...")
        self.dataset = self.get_data(
            fen_generator=self.get_fen,
            get_score=self.get_score,
            _limit=self.limit
        )
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
            result = self.model.fit(self.dataset,
                                    loss_fn=self.loss_func,
                                    metrics=(self.train_acc, self.test_acc),
                                    steps=2)
            if result['test_acc'][-1] < maxi:
                maxi = result['test_acc'][-1]
                maximum_layer = hidden_layer1
                maximum_grid = grid1
                maximum_k = k1
                with open(self.pre_model_json, "w") as f:
                    data = {"hidden_layer": maximum_layer,
                            "grid": maximum_grid,
                            "k": maximum_k}
                    json.dump(data, f)
            print()
            print(result['train_acc'][-1], result['test_acc'][-1])
            print(f"hidden_layer={maximum_layer}, grid={maximum_grid}, k={maximum_k}, " +
                  f"maxi_test_acc={maxi}")
            print(f"hidden_layer={hidden_layer1}, grid={grid1}, " +
                  f"k={k1}, test_loss={result['test_loss'][0]}")
            hidden_layer1 = self.random.choice(list(range(5, 101)))
            grid1 = self.random.choice(list(range(5, 51)))
            k1 = self.random.choice(list(range(3, 26)))


    @staticmethod
    def loss_func(x, y):
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

    def get_data(self, fen_generator, get_score, _limit):
        count = 0
        count2 = 0
        dataset = {}
        train_inputs = []
        train_labels = []
        test_inputs = []
        test_labels = []
        board = chess.Board()
        for fen in fen_generator(get_score, _limit):
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


    def get_wdl(self, fen_position):
        with chess.syzygy.open_tablebase(self.syzygy["wdl345"]) as tablebase:
            board = chess.Board(fen_position)
            result = tablebase.get_wdl(board)
        if result is None:
            with chess.syzygy.open_tablebase(self.syzygy["wdl6"]) as tablebase:
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
        with chess.engine.SimpleEngine.popen_uci(self.str_stockfish) as sf:
            result = sf.analyse(state, chess.engine.Limit(depth=depth))
            # if state.turn == chess.WHITE:
            score = result['score'].white().score()
            # else:
            #     score = result['score'].black().score()
            return score


    def get_fen(self, get_score, _limit):
        with open(self.epdeval, mode="r") as f:
            dataevals = f.readlines()
        fens = []
        for _ in range(_limit):
            for _ in range(4):
                dataeval = str(self.random.choice(dataevals)).strip()
                spl = dataeval.split(" ")
                fen = " ".join(spl[:-1])
                fens.append(fen)
        return fens


    def fen_random_generator(self, get_score, _limit):
        board = chess.Board()
        count = 0
        endgames = []
        pieces = ['P', 'p', 'N', 'n', 'B', 'b', 'R', 'r', 'Q', 'q']
        for _ in range(_limit):
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
            utils_progress(f"{count}/{limit} | {fen_positions}")
        return endgames

    def test_model(self):
        print("self.test_model() starting...")
        # self.dataset = self.get_data(
        #     fen_generator=self.fen_random_generator,
        #     get_score=self.get_wdl,
        #     _limit=4
        # )
        print(self.formula)

    def make_predict(self):
        print("self.make_predict() starting...")
        fens = list(self.get_fen(get_score=self.get_score, _limit=1))
        board1 = chess.Board()
        board1.set_fen(fens[0])
        board2 = chess.Board()
        board2.set_fen(fens[1])
        inp = self.get_train(state1=board1, state2=board2)
        variable_values = {
            f"x_{i}": inp[i - 1]
            for i in range(self.len_input, 0, -1)
        }
        formula = self.load_model()
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
