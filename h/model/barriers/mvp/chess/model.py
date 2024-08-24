import pickle
import datetime

from kan import *
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
        self.len_input = 11
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.dtype = torch.get_default_dtype()
        print(self.device, self.dtype)

        self.model = KAN(width=[self.len_input, 17, 1],
                         grid=31, k=3,
                         auto_save=True,
                         seed=0,
                         ckpt_path='./wdl_model')
        try:
            print("Loading ./ckpts...")
            self.model.loadckpt("./ckpts")
        except FileNotFoundError:
            pass

        self.train()
        # self.test_model()
        # self.predict()

    def train(self):
        results = []
        while True:
            self.dataset = self.get_data(
                fen_generator=self.fen_generator,
                get_score=self.get_wdl,
                limit=1000
            )
            result = self.model.fit(self.dataset,
                                    lamb=0.01, lamb_entropy=10,
                                    metrics=(self.train_acc, self.test_acc),
                                    steps=50)
            print(result['train_acc'][-1], result['test_acc'][-1])
            results.append([
                result['test_loss'][0] + result['test_loss'][1]
            ])
            results = sorted(results, key=lambda xx: xx[-1], reverse=True)
            utils_progress(f"results[-1][-1]={results[-1][-1]}")
            print("Saving ckpt...")
            self.model.saveckpt("./ckpts/wdl_model_" +
                                str(datetime.datetime.now()).\
                                replace(":", "-").replace(".", "-"). \
                                replace(" ", "-").replace("-", "_"))
            lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
            self.model.auto_symbolic(lib=lib)
            formula = self.model.symbolic_formula()[0][0]
            with open(f"wdl_formula_0.txt", encoding="UTF-8", mode="w") as p:
                p.write(str(formula).strip())

    def train_acc(self):
        return torch.mean((torch.round(self.model(self.dataset['train_input'])[:, 0]) ==
                           self.dataset['train_label'][:, 0]).type(self.dtype))

    def test_acc(self):
        return torch.mean((torch.round(self.model(self.dataset['test_input'])[:, 0]) ==
                           self.dataset['test_label'][:, 0]).type(self.dtype))

    def get_train(self, state):
        train_input = [[0., 0.] for _ in range(64)]
        for color in [False, True]:
            occupied = state.occupied_co[color]
            while occupied:
                square = lsb(occupied)
                piece = state.piece_type_at(square)
                train_input[square][0] = int(color)
                train_input[square][1] = piece
                occupied = poplsb(occupied)
        train_input = [j for i in train_input for j in i]
        if state.ep_square is None:
            train_input = [0.] + train_input
        else:
            train_input = [state.ep_square] + train_input
        train_input = [int(state.turn)] + train_input
        return train_input[:self.len_input]

    def get_data(self, fen_generator, get_score, limit):
        count = 0
        dataset = {}
        train_inputs = []
        train_labels = []
        test_inputs = []
        test_labels = []
        r = random.choice([0, 1])
        for endgame in fen_generator(get_score, limit):
            for fen in endgame:
                score = get_score(fen)
                if score is None:
                    continue
                count += 1
                self.last_fen = fen
                utils_progress(f"{str(count).rjust(9, ' ')} | " +
                               f"{str(get_score(fen)).rjust(2, ' ')} | {fen}")
                board = chess.Board()
                board.set_fen(fen)
                train_input = self.get_train(state=board)
                if count % 2 == r:
                    test_inputs.append(train_input)
                    test_labels.append([score])
                else:
                    train_inputs.append(train_input)
                    train_labels.append([score])
                if count % 2 == 0:
                    r = random.choice([0, 1])
        min_len = min(len(test_inputs), len(train_inputs))
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
        self.dataset = self.get_data(
            fen_generator=self.fen_generator,
            get_score=self.get_wdl,
            limit=50
        )
        fen = '8/K7/8/8/2k5/8/8/3r4 b - - 0 1'
        board = chess.Board()
        board.set_fen(fen)
        inp = self.get_train(state=board)
        print(inp)
        variable_values = {
            f"x_{i}": int(inp[i - 1])
            for i in range(self.len_input, 0, -1)
        }
        # print(variable_values)
        # sys.exit()
        result = self.model.fit(self.dataset, steps=2)
        print(result['test_loss'][0] + result['test_loss'][1])
        lib = ['x', 'x^2', 'x^3', 'x^4', 'exp', 'log', 'sqrt', 'tanh', 'sin', 'tan', 'abs']
        self.model.auto_symbolic(lib=lib)
        formula = self.model.symbolic_formula()[0][0]
        print(formula)
        for var, val in variable_values.items():
            formula = str(formula).replace(var, str(val))
        result = eval(formula)
        print(result)
        print(fen)


if __name__ == "__main__":
    Model()
