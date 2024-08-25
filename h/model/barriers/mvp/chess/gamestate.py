E = 0
P = 1
N = 2
B = 3
R = 4
Q = 5
K = 6


FIELD = [[E, E],
         [E, E]]
WHITE_PAWN = [[P, 0],
              [0, P]]
BLACK_PAWN = [[0, P],
              [P, 0]]
WHITE_KNIGHT = [[N, 0],
                [0, N]]
BLACK_KNIGHT = [[0, N],
                [N, 0]]
WHITE_BISHOP = [[B, 0],
                [0, B]]
BLACK_BISHOP = [[0, B],
                [B, 0]]
WHITE_ROOK = [[R, 0],
              [0, R]]
BLACK_ROOK = [[0, R],
              [R, 0]]
WHITE_QUEEN = [[Q, 0],
               [0, Q]]
BLACK_QUEEN = [[0, Q],
               [Q, 0]]
WHITE_KING = [[K, 0],
              [0, K]]
BLACK_KING = [[0, K],
              [K, 0]]

BLACK = False
WHITE = True


class Field:
    def __init__(self, square):
        self.position = square
        self.links = {}

    def add_link(self, from_link, to_link):
        self.links[from_link] = to_link



class GameState:

    def __init__(self, board):
        self.state = None
        self.fields = {}
        self.init(board=board)

    def init(self, board):
        self.state = board
        for square in range(64):
            self.add_field(square)

    def clear(self):
        self.board = None
        self.state = None
        self.fields = {}

    def add_field(self, square):
        self.fields[square] = Field(square=square)
