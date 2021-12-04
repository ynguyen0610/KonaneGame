import random
import copy

NEG_INF = -1000000000
POS_INF = 1000000000

class raiseError(AttributeError):
    """
    This class is used to indicate a problem in the konane game.
    """

class Konane:

    def __init__(self, n):
        self.size = n
        self.resetBoard()

    def resetBoard(self):
        """
        Resets the board state.
        """
        self.board = []
        value = 'X'
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(value)
                value = self.opponent(value)
            self.board.append(row)
            if self.size % 2 == 0:
                value = self.opponent(value)

    def __str__(self):
        result = "  "
        for i in range(self.size):
            result += str(i + 1) + " "
        result += "\n"
        for i in range(self.size):
            result += str(i + 1) + " "
            for j in range(self.size):
                result += str(self.board[i][j]) + " "
            result += "\n"
        return result

    def valid(self, row, col):
        """
        Returns true if the given row and column represent a valid location.
        """
        return row >= 0 and row < self.size and col >= 0 and col < self.size

    def contains(self, board, row, col, symbol):
        """
        Returns true if given row and column represent a valid location on
        the KonaneBoard board and that location contains the symbol representing the players.
        """
        return self.valid(row, col) and board[row][col] == symbol

    def countSymbol(self, board, symbol):
        count = 0
        for row in range(self.size):
            for col in range(self.size):
                if board[row][col] == symbol:
                    count += 1
        return count

    def opponent(self, player):
        if player == 'X':
            return 'O'
        else:
            return 'X'

    def makeMove(self, player, move):
        self.board = self.nextBoard(self.board, player, move)

    def nextBoard(self, board, player, move):
        r1 = (int)(move[0])
        c1 = (int)(move[1])
        r2 = (int)(move[2])
        c2 = (int)(move[3])
        next = copy.deepcopy(board)
        if not (self.valid(r1, c1) and self.valid(r2, c2)):
            raise raiseError
        if next[r1][c1] != player:
            raise raiseError

        dist = abs(r1-r2 + c1-c2) # calculates the distance between two points vertically/horizontally, not diagonally

        if dist == 0:
            if self.openingMove(board):
                next[r1][c1] = "."
                return next
            raise raiseError
        if next[r2][c2] != ".":
            raise raiseError
        jumps = (int)(dist/2)
        dr = (int)((r2 - r1)/dist)
        dc = (int)((c2 - c1)/dist)
        for i in range(jumps):
            if next[r1+dr][c1+dc] != self.opponent(player):
                raise raiseError
            next[r1][c1] = "."
            next[r1+dr][c1+dc] = "."
            r1 += 2*dr
            c1 += 2*dc
            next[r1][c1] = player
        return next

    def openingMove(self, board):
        return self.countSymbol(board, ".") <= 1

    def generateFirstMoves(self, board):
        moves = []
        moves.append([self.size/2-1]*4)
        return moves

    def generateSecondMoves(self, board):
        moves = []
        moves.append([self.size/2-1, self.size/2]*2)
        return moves

    def check(self, board, r, c, rd, cd, factor, opponent):
        """
        Checks to see if a jump is possible starting at (r,c) and going in the
        direction determined by the row delta, rd, and the column delta, cd.
        The factor recursively checks for multiple jumps.  
        Returns possible jumps.
        """
        if self.contains(board, r+factor*rd, c+factor*cd, opponent) and \
           self.contains(board, r+(factor+1)*rd, c+(factor+1)*cd, '.'):
            return [[r, c, r+(factor+1)*rd, c+(factor+1)*cd]] + \
                self.check(board, r, c, rd, cd, factor+2, opponent)
        else:
            return []

    def generateMoves(self, board, player):
        """
        Generates legal moves for the given player in
        current board state.
        """
        if self.openingMove(board):
            if player == 'X':
                return self.generateFirstMoves(board)
            else:
                return self.generateSecondMoves(board)
        else:
            moves = []
            rd = [-1, 0, 1, 0]
            cd = [0, 1, 0, -1]
            for r in range(self.size):
                for c in range(self.size):
                    if board[r][c] == player:
                        for i in range(len(rd)):
                            moves += self.check(board, r, c, rd[i], cd[i], 1,
                                                self.opponent(player))
            return moves

    def playOneGame(self, p1, p2, show):
        """
        Play out one game between 2 players. Returns 'X' if black wins, 'O' if
        white wins. When show is true, this functinos displays all the moves.
        """
        self.resetBoard()
        p1.initialize('X')
        p2.initialize('O')
        print(p1.name, "vs", p2.name)
        while True:
            if show:
                print(self)
                print("player X's turn")
            move = p1.getMove(self.board)
            if move == []:
                print("Game over")
                return 'O'
            try:
                self.makeMove('X', move)
            except raiseError:
                print("Game over: Invalid move by", p1.name)
                print(move)
                print(self)
                return 'O'
            if show:
                print(move)
                print
                print(self)
                print("player O's turn")
            move = p2.getMove(self.board)
            if move == []:
                print("Game over")
                return 'X'
            try:
                self.makeMove('O', move)
            except raiseError:
                print("Game over: Invalid move by", p2.name)
                print(move)
                print(self)
                return 'X'
            if show:
                print(move)
                print

    def playNGames(self, n, p1, p2, show):
        """
        Play n games between 2 players (alternating in rounds)
        """
        first = p1
        second = p2
        for i in range(n):
            print("Game", i)
            winner = self.playOneGame(first, second, show)
            if winner == 'X':
                first.won()
                second.lost()
                print(first.name, "wins")
            else:
                first.lost()
                second.won()
                print(second.name, "wins")
            first, second = second, first

class Player:
    """
    Base class for Konane players. 
    """
    name = "Player"
    wins = 0
    losses = 0

    def results(self):
        result = self.name
        result += " Wins:" + str(self.wins)
        result += " Losses:" + str(self.losses)
        return result

    def lost(self):
        self.losses += 1

    def won(self):
        self.wins += 1

    def reset(self):
        self.wins = 0
        self.losses = 0

    def initialize(self, side):
        abstract()

    def getMove(self, board):
        abstract()

class RandomPlayer(Konane, Player):
    """
    Chooses a random move.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Random"

    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        n = len(moves)
        print(n)
        if n == 0:
            return []
        else:
            return moves[random.randrange(0, n)]

class HumanPlayer(Konane, Player):
    """
    User can play as a human player.
    """
    def initialize(self, side):
        self.side = side
        self.name = "Human"

    def getMove(self, board):
        moves = self.generateMoves(board, self.side)
        while True:
            movesFrom1 = []
            for move in moves:
                moveBase1 = []
                for value in move:
                    value = (int)(value + 1)
                    moveBase1.append(value)
                movesFrom1.append(moveBase1)
            print("Possible moves:", movesFrom1)
            
            n = len(moves)
            if n == 0:
                print("Must concede")
                return []
            index = int(input("Enter index of chosen move (0-" + str(n-1) +
                              ") or -1 to concede: "))
            if index == -1:
                return []
            if 0 <= index <= (n-1):
                print("returning", moves[index])
                return moves[index]
            else:
                print("Invalid choice, try again.")

class MinimaxPlayer(Konane, Player):
    def __init__(self, size, depth, calculateEvals):
        Konane.__init__(self, size)
        self.depth = depth
        self.calculateEvals = calculateEvals
    
    def initialize(self, side):
        self.side = side
        self.name = "MinimaxPlayer Depth " + str(self.depth)

    def getMove(self, board):
        moves = self.generateMoves(board, self.side)

        bestVal = NEG_INF
        bestIndex = 0
        indexCount = 0

        if len(moves) == 0:
            return []

        for move in moves:
            val = (self.minimax(self.nextBoard(board, self.side, move), 0, self.opponent(self.side)))[0]
            if val == None:
                return []
            if val > bestVal:
                bestVal = val
                bestIndex = indexCount
            if indexCount != len(moves) -1:
                indexCount += 1

        return moves[bestIndex]

    def eval(self, board): 
        moves = self.generateMoves(board, self.side)
        oppMoves = self.generateMoves(board, self.opponent(self.side))
        # opponent loses
        if len(oppMoves) == 0:
            return POS_INF
        # opponent wins
        if len(moves) == 0:
            return NEG_INF
        return len(moves) - len(oppMoves) # take the available possible moves of players minus the available possible moves of opponents

    def minimax(self, board, depth, side):
        moves = self.generateMoves(board, side)
        
        if depth == 0 or len(moves) == 0:
            self.calculateEvals += 1
            print(self.calculateEvals)
            return self.eval(board), None

        # if len(moves) == 0:
        #     return POS_INF

        isMax = (depth % 2 == 0)

        if isMax:
            value = NEG_INF
            bestMove = None
            for eachMove in moves:
                newValue, _ = self.minimax(self.makeMove(self.side, eachMove), depth + 1, self.opponent(self.side))
                if newValue > value:
                    value = newValue
                    bestMove = eachMove
            return value, bestMove
        else:
            value = POS_INF
            bestMove = None
            for eachMove in moves:
                newValue, _ = self.minimax(self.makeMove(self.opponent(self.side), eachMove), depth + 1, self.side)
                if newValue < value:
                    value = newValue
                    bestMove = eachMove
            return value, bestMove

class minimaxAB(Konane, Player):
    def __init__(self, size, depth, calculateEvals):
        Konane.__init__(self, size)
        self.depth = depth
        self.calculateEvals = calculateEvals
    
    def initialize(self, side):
        self.side = side
        self.name = "ABPlayer Depth " + str(self.depth)

    def getMove(self, board):
        moves = self.generateMoves(board, self.side)

        bestVal = NEG_INF
        bestIndex = 0
        indexCount = 0

        if len(moves) == 0:
            return []

        for move in moves:
            val = (self.minimaxAB(self.nextBoard(board, self.side, move), 0, self.opponent(self.side), NEG_INF, POS_INF))[0]
            if val > bestVal:
                bestVal = val
                bestIndex = indexCount
            if indexCount != len(moves) -1:
                indexCount += 1

        return moves[bestIndex]

    def evaluation(self, board):
        """
        Evaluation function returns an estimate of the expected utility of current state
        """
        moves = self.generateMoves(board, self.side)
        opponent_moves = self.generateMoves(
            board, self.opponent(self.side))

        if len(opponent_moves) == 0:
            # opponent loses, MAX wins
            return float("inf")
        if len(moves) == 0:
            # opponent wins, MAX loses
            return -float("inf")
        return len(moves) - len(opponent_moves)

    def minimaxAB(self, board, depth, side, alpha, beta):
        """
        Make descision to move based on the minimax alpha beta Pruning rule
        """
        # possible moves
        moves = self.generateMoves(board, self.side)

        # If reach the depth limit or is terminal node
        if depth == self.depth:
            self.calculateEvals += 1
            print(self.calculateEvals)
            return (self.evaluation(board), None)

        # max node is at even depth, min node is at odd depth
        isMax = (depth % 2 == 0)

        if isMax:
            best_move = 0
            for move in moves:
                backedup_val = (self.minimaxAB(self.nextBoard(
                    board, side, move), depth + 1, self.opponent(self.side), alpha, beta))[0]
                if backedup_val > alpha:
                    alpha = backedup_val
                    best_move = move
                if alpha >= beta:
                    return beta, best_move
            return alpha, best_move
        else:
            best_move = 0
            for move in moves:
                backedup_val = (self.minimaxAB(self.nextBoard(
                    board, side, move), depth + 1, self.side, alpha, beta))[0]
                if backedup_val < beta:
                    beta = backedup_val
                    best_move = move
                if alpha >= beta:
                    return alpha, best_move
            return beta, best_move

    # def eval(self, board):
    #     moves = self.generateMoves(board, self.side)
    #     oppMoves = self.generateMoves(board, self.opponent(self.side))
    #     if len(oppMoves) == 0:
    #         return POS_INF
    #     if len(moves) == 0:
    #         return NEG_INF
    #     return len(moves) - len(oppMoves)

    # def minimaxAB(self, board, depth, isMax, side, alpha, beta):
    #     moves = self.generateMoves(board, side)
    #     if self.depth == depth:
    #         return (self.eval(board), None)

    #     if len(moves) == 0:
    #         return (POS_INF, None)

    #     if isMax:
    #         value = NEG_INF
    #         bestMove = None
    #         for eachMove in moves:
    #             value = max(value, self.minimaxAB(self.nextBoard(board, side, eachMove), depth+1, False, self.opponent(self.side), alpha, beta))
    #             alpha = max(alpha, value)
    #             if alpha > beta:
    #                 break
    #         return value, bestMove
    #     else:
    #         bestMove = None
    #         value = POS_INF
    #         for move in moves:
    #             value = min(value, self.minimaxAB(self.nextBoard(board, side, move), depth+1, True, self.side, alpha, beta))
    #             beta = min(beta, value)
    #             if alpha > beta:
    #                 break
    #         return value, bestMove

game = Konane(8)
game.playNGames(1, MinimaxPlayer(8, 2, 0), MinimaxPlayer(8, 2, 0), 0)

# game = Konane(8)
# game.playNGames(2, minimaxAB(8, 2, 0), minimaxAB(8, 1, 0), 0)

# game = Konane(8)
# game.playOneGame(RandomPlayer(8), RandomPlayer(8), True)

# game = Konane(8)
# game.playNGames(3, MinimaxPlayer(8, 2), MinimaxPlayer(8, 1), 1)

# game = Konane(8)
# game.playNGames(3, HumanPlayer(8), MinimaxPlayer(8, 4), 1)
