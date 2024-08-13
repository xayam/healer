import search as Search
import evaluation as Eval
from helpers import *
from limits import *

# External
from sys import stdout
from threading import Thread
import chess


class UCI:
    def __init__(self) -> None:
        self.memory = []
        self.out = stdout
        self.board = chess.Board()
        self.search = Search.Search(self.memory, self.board)
        self.thread = None
        self.depth = 7

    def output(self, s) -> None:
        self.out.write(str(s) + "\n")
        self.out.flush()

    def stop(self) -> None:
        self.search.stop = True
        try:
            self.thread.join()
        except:
            pass

    def quit(self) -> None:
        self.search.stop = True
        try:
            self.thread.join()
        except:
            pass

    def uci(self) -> None:
        self.output("id name xasifaz")
        self.output("id author Alexey Belyanin, xayam@yandex.ru")
        self.output("")
        self.output("option name Move Overhead type spin default 5 min 0 max 5000")
        self.output("option name Ponder type check default false")
        self.output("uciok")

    def isready(self) -> None:
        self.output("readyok")

    def ucinewgame(self) -> None:
        pass

    def eval(self) -> None:
        pass
        # TODO
        # eval = Eval.Evaluation(self.memory)
        pv = self.search.absearch(MAX_PLY, -400, 400)
        # self.output(evaluate)

    def process_command(self, input: str) -> None:
        splitted = input.split(" ")
        command = splitted[0]
        if command == "quit":
            self.quit()
        elif command == "stop":
            self.stop()
            self.search.reset()
        elif command == "ucinewgame":
            self.ucinewgame()
            self.search.reset()
        elif command == "uci":
            self.uci()
        elif command == "isready":
            self.isready()
        elif command == "setoption":
            pass
        elif command == "position":
            self.search.reset()
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            movelist = []

            move_idx = input.find("moves")
            if move_idx >= 0:
                movelist = input[move_idx:].split()[1:]

            if splitted[1] == "fen":
                position_idx = input.find("fen") + len("fen ")

                if move_idx >= 0:
                    fen = input[position_idx:move_idx]
                else:
                    fen = input[position_idx:]

            self.board.set_fen(fen)
            self.search.hashHistory.clear()

            for move in movelist:
                self.board.push_uci(move)
                self.search.hashHistory.append(self.search.getHash())

        elif command == "print":
            print(self.board)
        elif command == "go":
            limits = Limits(0, MAX_PLY, 0)

            l = ["depth", "nodes"]
            for limit in l:
                if limit in splitted:
                    limits.limited[limit] = int(splitted[splitted.index(limit) + 1])

            ourTimeStr = "wtime" if self.board.turn == chess.WHITE else "btime"
            ourTimeIncStr = "winc" if self.board.turn == chess.WHITE else "binc"

            if ourTimeStr in input:
                limits.limited["time"] = (
                    int(splitted[splitted.index(ourTimeStr) + 1]) / 20
                )

            if ourTimeIncStr in input:
                limits.limited["time"] += (
                    int(splitted[splitted.index(ourTimeIncStr) + 1]) / 2
                )

            self.search.limit = limits

            self.thread = Thread(target=self.search.iterativeDeepening,
                                 kwargs={"ply": MAX_PLY})
            self.thread.start()

        elif command == "eval":
            return self.eval()
