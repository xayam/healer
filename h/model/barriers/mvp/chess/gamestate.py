
TYPE_PAWN = 1
TYPE_KNIGHT = 2
TYPE_BISHOP = 3
TYPE_ROOK = 4
TYPE_QUEEN = 5
TYPE_KING = 6


WHITE_FIELD = [1, 1]
BLACK_FIELD = [0, 0]
WHITE_PAWN = [TYPE_PAWN, 0]
BLACK_PAWN = [0, TYPE_PAWN]
WHITE_KNIGHT = [TYPE_KNIGHT, 0]
BLACK_KNIGHT = [0, TYPE_KNIGHT]
WHITE_BISHOP = [TYPE_BISHOP, 0]
BLACK_BISHOP = [0, TYPE_BISHOP]
WHITE_ROOK = [TYPE_ROOK, 0]
BLACK_ROOK = [0, TYPE_ROOK]
WHITE_QUEEN = [TYPE_QUEEN, 0]
BLACK_QUEEN = [0, TYPE_QUEEN]
WHITE_KING = [TYPE_KING, 0]
BLACK_KING = [0, TYPE_KING]

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
