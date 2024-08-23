import io
import pstats
import math
import random
import sys
from collections import deque
import time
import cProfile
from typing import Tuple

import chess
from mcnode import MCTSNode


class MCTS:
    def __init__(self, state: chess.Board, iterations: int,
                 exploration_constant: float = math.sqrt(2),
                 depth_limit: int = None, use_opening_book: bool = False,
                 cnn=None):
        """ Initialize the MCTS object
        :param state: The initial state of the game
        :param iterations: The number of iterations to run the algorithm
        :param exploration_constant: The exploration constant to use in
               the UCB1 algorithm
        :param depth_limit: The depth limit to use in the algorithm
        :param use_opening_book: Whether to use the opening book """
        self.iterations = iterations  # The number of iterations to perform
        # The exploration constant, sqrt(2) by default
        self.exploration_constant = exploration_constant
        self.root = MCTSNode(state)
        self.current_node = self.root
        self.depth_limit = depth_limit
        self.use_opening_book = use_opening_book
        self.cnn = cnn

    def set_current_node(self, state: chess.Board):
        """ Set the current node to the one corresponding to the given state

         :param state: The state to set the current node to"""
        # First look in the children of the current node
        for child in self.current_node.children:
            if child.state == state:
                self.current_node = child
                # print(self.current_node.state())
                return
        # If it's not in the children of the node, look in the entire tree
        queue = deque([self.root])
        while queue:
            node = queue.popleft()
            if node.state == state and node != self.root and node != self.current_node:
                self.current_node = node
                # print(self.current_node.state())
                return
            queue.extend(node.children)
        if not self.current_node.state == state:
            self.current_node = MCTSNode(state)

    def _select(self, node: MCTSNode, depth: int) -> MCTSNode:
        """ Select the next node to explore using the UCB1 algorithm
         :param node: The node to select from
         :param depth: The depth of the node
         :return: The selected node """
        while not node.state.is_game_over():
            if node.not_fully_expanded():
                return node
            if self.depth_limit and depth >= self.depth_limit:
                return node
            children = node.children
            children = [child for child in children if child.alpha <= node.beta]
            if len(children) == 0:
                return node
            node = max(children, key=lambda c: c.ucb1(self.exploration_constant))
            depth += 1
        return node

    @staticmethod
    def _expand(node: MCTSNode) -> MCTSNode:
        """ Expand the selected node by creating new children
         :param node: The node to expand
         :return: The new child node """
        next_state = node.state.copy()
        moves = list(next_state.legal_moves)
        moving = random.choice(moves)
        next_state.push(moving)
        if next_state.is_game_over():
            return node
        new_node = MCTSNode(next_state, parent=node,
                            alpha=node.alpha, beta=node.beta,
                            move=moving, cnn=None)
        node.children.append(new_node)
        return new_node

    @staticmethod
    def _simulate(node: MCTSNode) -> int:
        """ Simulate the game to a terminal state and return the result

         :param node: The node to simulate from
         :return: The result of the simulation """
        state = node.state.copy()
        # start = time.time()
        r = {"1-0": 1, "0-1": 0, "1/2-1/2": 0.5}
        while not state.is_game_over():
            # hashtable_result = self.hashtable.lookup(state.fen())
            # if hashtable_result:
            #     value, move = hashtable_result
            #     if state.board.turn == "w":
            #         if value >= node.beta:
            #             return -1
            #         node.alpha = max(node.alpha, value)
            #     else:
            #         if value <= node.alpha:
            #             return 1
            #         node.beta = min(node.beta, value)
            # else:
            moves = list(state.legal_moves)
            moving = random.choice(moves)
            state.push(moving)
            if state.is_game_over():
                return r[state.result()]
        # end = time.time()
        # print(end - start)
        return r[state.result()]

    @staticmethod
    def _backpropagate(node: MCTSNode, result: int):
        """ Backpropagate the result of the
            simulation from the terminal node to the root node
         :param node: The terminal node
         :param result: The result of the simulation"""
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def select_move(self, state: chess.Board) -> Tuple[str, float]:
        """ Perform the MCTS algorithm and select the best move
         :return: The best move """
        self.set_current_node(state)
        for _ in range(self.iterations):
            node = self._select(self.current_node, 0)
            if node.not_fully_expanded():
                node = self._expand(node)
            result = self._simulate(node)
            self._backpropagate(node, result)
        if not self.current_node.children:
            return "", 0.0
        best_child = max(self.current_node.children, key=lambda c: c.ucb1(self.exploration_constant))
        self.current_node = best_child
        return best_child.move, best_child.ucb1(self.exploration_constant)


def mcts_best(chess_state: chess.Board):
    mcts = MCTS(chess_state, iterations=20)
    moves = chess_state.legal_moves
    move_scores = []
    for move in moves:
        chess_state.push(move)
        _, score = mcts.select_move(chess_state)
        chess_state.pop()
        move_scores.append([score, move])
    # if chess_state.turn == chess.WHITE:
    best = max(move_scores, key=lambda x: x[0])
    # else:
    #     best = min(move_scores, key=lambda x: x[0])
    print(move_scores)
    return best[0], best[1]


if __name__ == "__main__":
    chess_state = chess.Board()
    mcts = MCTS(chess_state, iterations=10)
    start = time.time()
    move = ""
    while not chess_state.is_game_over():
        pr = cProfile.Profile()
        pr.enable()
        move, score = mcts.select_move(chess_state)
        pr.disable()
        s = io.StringIO()
        sort_by = 'tottime'
        ps = pstats.Stats(pr, stream=s).sort_stats(sort_by)
        ps.print_stats()
        # print(s.getvalue())
        # print(move)
        # print(f"\nTime taken on average/game: {(time.time() - start)/20}")
        # print(move)
        print()
        print(chess_state)
        move = str(move).strip()
        if move:
            m = chess.Move.from_uci(move)
            chess_state.push(m)
            mcts.set_current_node(chess_state)
        else:
            break
        print(move, score)
        # sys.exit()
    result = chess_state.result()
    if not move:
        result = "1/2-1/2"
    print()
    print(result)
