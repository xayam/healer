import sys

import search as Search
from evaluation import evaluate
from helpers import *
from limits import *

# External
from sys import stdout
from threading import Thread
import chess

from model.barriers.mvp.chess.mctsearch import mcts_best


class UCI:
    def __init__(self) -> None:
        self.out = stdout
        self.board = chess.Board()
        self.search = Search.Search(self.board)
        self.thread: None

    def output(self, s) -> None:
        self.out.write(str(s) + "\n")
        self.out.flush()

    def stop(self) -> None:
        self.search.stop = True
        if self.thread is not None:
            try:
                self.thread.join()
            except:
                pass

    def quit(self) -> None:
        self.search.stop = True
        if self.thread is not None:
            try:
                self.thread.join()
            except:
                pass

    def uci(self) -> None:
        self.output("id name xasifaz")
        self.output("id author Aleksey Belyanin, xayam@yandex.ru")
        self.output("")
        self.output("option name Move Overhead type spin default 5 min 0 max 5000")
        self.output("option name Ponder type check default false")
        self.output("uciok")

    def isready(self) -> None:
        self.output("readyok")

    def ucinewgame(self) -> None:
        pass

    def eval(self) -> None:
        _, score = mcts_best(self.board)
        self.output(score)

    def processCommand(self, input: str) -> None:
        splitted = input.split(" ")
        if splitted[0] == "quit":
            self.quit()
        elif splitted[0] == "stop":
            self.stop()
            self.search.reset()
        elif splitted[0] == "ucinewgame":
            self.ucinewgame()
            self.search.reset()
        elif splitted[0] == "uci":
            self.uci()
        elif splitted[0] == "isready":
            self.isready()
        elif splitted[0] == "setoption":
            pass
        elif splitted[0] == "position":
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
        elif splitted[0] == "print":
            print(self.board)
        elif splitted[0] == "go":
            # limits = Limits(0, MAX_PLY, 0)
            #
            # l = ["depth", "nodes"]
            # for limit in l:
            #     if limit in splitted:
            #         limits.limited[limit] = int(splitted[splitted.index(limit) + 1])
            #
            # ourTimeStr = "wtime" if self.board.turn == chess.WHITE else "btime"
            # ourTimeIncStr = "winc" if self.board.turn == chess.WHITE else "binc"
            #
            # if ourTimeStr in input:
            #     limits.limited["time"] = (
            #         int(splitted[splitted.index(ourTimeStr) + 1]) / 20
            #     )
            #
            # if ourTimeIncStr in input:
            #     limits.limited["time"] += (
            #         int(splitted[splitted.index(ourTimeIncStr) + 1]) / 2
            #     )
            # self.search.limit = limits
            # self.thread = Thread(target=self.search.iterativeDeepening)
            # self.thread.start()
            bestmove, _ = mcts_best(self.board)
            # stdout.write("info " + str(score) + "\n")
            stdout.write("bestmove " + str(bestmove) + "\n")
            stdout.flush()
        elif splitted[0] == "eval":
            return self.eval()
