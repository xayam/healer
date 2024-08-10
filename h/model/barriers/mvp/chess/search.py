import time
from typing import Tuple

import tt as TT
import evaluation as Eval
import psqt as PQST

# External
import chess
import chess.polyglot
from helpers import *
from limits import *
from sys import stdout


class Search:
    def __init__(self, memory, board: chess.Board) -> None:
        self.memory = memory
        self.board = board
        self.transposition_table = TT.TranspositionTable()
        self.eval = Eval.Evaluation(self.memory)

        self.pvLength = [0] * MAX_PLY
        self.pvTable = [[chess.Move.null()] * MAX_PLY for _ in range(MAX_PLY)]

        self.nodes = 0
        self.searchStartTime = 0

        self.limit = Limits(0, MAX_PLY, 0)

        self.stop = False
        self.checks = CHECK_RATE

        self.hashHistory = []

        # History Table
        self.htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)]

    # def qsearch(self, ply: int, depth, alpha: int, beta: int) -> int:
    #     if self.stop or self.checkTime():
    #         return 0
    #     return self.eval.evaluate(self.memory, ply, depth, self.board)


    def absearch(self, ply: int, alpha: int, beta: int) -> Tuple[int, int]:
        if self.checkTime():
            return 0, 0
        return self.eval.evaluate(ply, alpha, beta, self.board)


    def iterativeDeepening(self, memory, ply) -> None:
        self.nodes = 0
        score = -400
        bestmove = chess.Move.null()
        self.t0 = time.time_ns()
        for p in range(1, ply):
            bestmove, score = self.absearch(p, -score, score)
            if self.stop or self.checkTime(True):
                break
            # Save bestmove
            bestmove = self.pvTable[0][0]
            # print info
            now = time.time_ns()
            stdout.write(self.stats(p, score, now - self.t0) + "\n")
            stdout.flush()
        # last attempt to get a bestmove
        if bestmove == chess.Move.null():
            bestmove = self.pvTable[0][0]
        # print bestmove
        stdout.write("bestmove " + str(bestmove) + "\n")
        stdout.flush()

    # Detect a repetition
    def isRepetition(self, key: int, draw: int = 1) -> bool:
        count = 0
        size = len(self.hashHistory)

        for i in range(size - 1, -1, -2):
            if i >= size - self.board.halfmove_clock:
                if self.hashHistory[i] == key:
                    count += 1
                if count == draw:
                    return True

        return False

    # Most Valuable Victim - Least Valuable Aggressor
    def mvvlva(self, move: chess.Move) -> int:
        mvvlva = [
            [0, 0, 0, 0, 0, 0, 0],
            [0, 105.0, 104.0, 103.0, 102.0, 101.0, 100.0],
            [0, 205.0, 204.0, 203.0, 202.0, 201.0, 200.0],
            [0, 305.0, 304.0, 303.0, 302.0, 301.0, 300.0],
            [0, 405.0, 404.0, 403.0, 402.0, 401.0, 400.0],
            [0, 505.0, 504.0, 503.0, 502.0, 501.0, 500.0],
            [0, 605.0, 604.0, 603.0, 602.0, 601.0, 600.0],
        ]

        from_square = move.from_square
        to_square = move.to_square
        attacker = self.board.piece_type_at(from_square)
        victim = self.board.piece_type_at(to_square)

        # En passant
        if victim is None:
            victim = 1
        return mvvlva[victim][attacker]

    # assign a score to moves in qsearch
    def scoreQMove(self, move: chess.Move) -> int:
        return self.mvvlva(move)

    # assign a score to normal moves
    def scoreMove(self, move: chess.Move, ttMove: chess.Move) -> int:
        if move == ttMove:
            return 1_000_000
        elif self.board.is_capture(move):
            # make sure captures are ordered higher than quiets
            return 32_000 + self.mvvlva(move)
        return self.htable[self.board.turn][move.from_square][move.to_square]

    def getHash(self) -> int:
        return chess.polyglot.zobrist_hash(self.board)

    def checkTime(self, iter: bool = False) -> bool:
        if self.stop:
            return True

        if (
            self.limit.limited["nodes"] != 0
            and self.nodes >= self.limit.limited["nodes"]
        ):
            return True

        if self.checks > 0 and not iter:
            self.checks -= 1
            return False

        self.checks = CHECK_RATE

        if self.limit.limited["time"] == 0:
            return False

        timeNow = time.time_ns()
        if (timeNow - self.t0) / 1_000_000 > self.limit.limited["time"]:
            return True

    # Build PV
    def getPV(self) -> str:
        pv = ""

        for i in range(0, self.pvLength[0]):
            pv += " " + str(self.pvTable[0][i])

        return pv

    # Convert mate scores
    def convert_score(self, score: int) -> str:
        if score >= VALUE_MATE_IN_PLY:
            return "mate " + str(
                ((VALUE_MATE - score) // 2) + ((VALUE_MATE - score) & 1)
            )
        elif score <= VALUE_MATED_IN_PLY:
            return "mate " + str(
                -((VALUE_MATE + score) // 2) + ((VALUE_MATE + score) & 1)
            )
        else:
            return "cp " + str(score)

    # Print uci info
    def stats(self, depth: int, score: int, time: int) -> str:
        time_in_ms = int(time / 1_000_000)
        time_in_seconds = max(1, time_in_ms / 1_000)
        info = (
            "info depth "
            + str(depth)
            + " score "
            + str(self.convert_score(score))
            + " nodes "
            + str(self.nodes)
            + " nps "
            + str(int(self.nodes / time_in_seconds))
            + " time "
            + str(round(time / 1_000_000))
            + " pv"
            + self.getPV()
        )
        return info

    # Reset search stuff
    def reset(self) -> None:
        self.pvLength[0] = 0
        self.nodes = 0
        self.t0 = 0
        self.stop = False
        self.checks = CHECK_RATE
        self.hashHistory = []
        self.htable = [[[0 for x in range(64)] for y in range(64)] for z in range(2)]


# Run search.py instead of main.py if you want to profile it!
if __name__ == "__main__":
    memory = [[0] * 7] * 7
    board = chess.Board()
    search = Search(memory, board)

    search.limit.limited["depth"] = 7
    search.iterativeDeepening()
