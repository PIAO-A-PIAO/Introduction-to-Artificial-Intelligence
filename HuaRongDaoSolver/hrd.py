from copy import deepcopy
from heapq import heappush, heappop, heapify
import time
import argparse
import sys
import os

#====================================================================================

char_goal = '1'
char_single = '2'
directions = ["up", "down", "left", "right"]
depth_limit = 10

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_goal, is_single, coord_x, coord_y, orientation):
        """
        :param is_goal: True if the piece is the goal piece and False otherwise.
        :type is_goal: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_goal = is_goal
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_goal, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = 5

        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_goal:
                self.grid[piece.coord_y][piece.coord_x] = char_goal
                self.grid[piece.coord_y][piece.coord_x + 1] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x] = char_goal
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = char_goal
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'

    def display(self):
        """
        Print out the current board.
        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()
    
    def text(self):
        output = ""
        for row in self.grid:
            for ch in row:
                output += ch
            output += '\n'
        return output + '\n'

    def getGoal(self):
        for piece in self.pieces:
            if piece.is_goal:
                return piece
        

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.f = f
        self.depth = depth
        self.parent = parent
        self.id = hash(board)  # The id for breaking ties.

    def __lt__(self, other):
        return self.f < other.f

def goalTest(board):
    """
    Return True if the puzzle reaches the goal state.
    Return False otherwise.
    """
    return board.grid[3][1] == board.grid[4][2] == char_goal

def canMove(board, piece, direction):
    if direction == "up":
            if piece.coord_y == 0:
                #nowhere to go
                return False
            if piece.is_goal or piece.orientation == 'h':
                #need to check two grids
                return board.grid[piece.coord_y-1][piece.coord_x] == board.grid[piece.coord_y-1][piece.coord_x+1] == '.'
            else:
                #not goal or vertical, check one grid only
                return board.grid[piece.coord_y-1][piece.coord_x] == '.'
    elif direction == "down":
            if piece.coord_y == 4:
                return False
            if piece.is_goal:
                return piece.coord_y < 3 and board.grid[piece.coord_y+2][piece.coord_x] == board.grid[piece.coord_y+2][piece.coord_x+1] == '.'
            if piece.orientation == 'h':
                return board.grid[piece.coord_y+1][piece.coord_x] == board.grid[piece.coord_y+1][piece.coord_x+1] == '.'
            if piece.orientation == 'v':
                return piece.coord_y <3 and board.grid[piece.coord_y+2][piece.coord_x] == '.'
            else:
                return board.grid[piece.coord_y+1][piece.coord_x] == '.'
    elif direction == "left":
            if piece.coord_x == 0:
                return False
            if piece.is_goal or piece.orientation == 'v':
                return board.grid[piece.coord_y][piece.coord_x-1] == board.grid[piece.coord_y+1][piece.coord_x-1] == '.'
            else:
                return board.grid[piece.coord_y][piece.coord_x-1] == '.'
    elif direction == "right":
            if piece.coord_x == 3:
                return False
            if piece.orientation == 'v':
                return board.grid[piece.coord_y][piece.coord_x+1] == board.grid[piece.coord_y+1][piece.coord_x+1] == '.'
            if piece.is_goal:
                return piece.coord_x < 2 and board.grid[piece.coord_y][piece.coord_x+2] == board.grid[piece.coord_y+1][piece.coord_x+2] == '.'
            if piece.orientation == 'h':
                return piece.coord_x < 2 and board.grid[piece.coord_y][piece.coord_x+2] == '.'
            else:
                return board.grid[piece.coord_y][piece.coord_x+1] == '.'
    return

def movePiece(piece, direction):
    if direction == "up":
        piece.coord_y -= 1
    elif direction == "down":
        piece.coord_y += 1
    elif direction == "left":
        piece.coord_x -= 1
    elif direction == "right":
        piece.coord_x += 1

def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: A loaded board
    :rtype: Board
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    g_found = False

    for line in puzzle_file:

        for x, ch in enumerate(line):

            if ch == '^': # found vertical piece
                pieces.append(Piece(False, False, x, line_index, 'v'))
            elif ch == '<': # found horizontal piece
                pieces.append(Piece(False, False, x, line_index, 'h'))
            elif ch == char_single:
                pieces.append(Piece(False, True, x, line_index, None))
            elif ch == char_goal:
                if g_found == False:
                    pieces.append(Piece(True, False, x, line_index, None))
                    g_found = True
        line_index += 1

    puzzle_file.close()

    board = Board(pieces)
    
    return board

def boardToCode(board):
    code = ""
    foundGoal = False
    for row in board.grid:
        for ch in row:
            if ch == '^':
                code += 'V'
            elif ch == '<':
                code += 'H'
            elif ch == char_single:
                code += 'S'
            elif ch == char_goal:
                if not foundGoal:
                    code += 'G'
                    foundGoal = True
            elif ch == '.':
                code += 'E'
    return code

def f(board, function=None, cost=None):
    if function == "dfs":
        return 0
    if function == "astar":
        goalPiece = board.getGoal()
        return (abs(goalPiece.coord_x - 1) + abs(goalPiece.coord_y - 3)) + cost

def dfsSuccessors(state, explored, frontier):
    frontier.pop()
    newDepth = state.depth + 1
    numP = len(state.board.pieces)
    for i in range(0, numP):
        for direction in directions:
            if canMove(state.board, state.board.pieces[i], direction):
                pieces = deepcopy(state.board.pieces)
                movePiece(pieces[i], direction)
                board = Board(pieces)
                code = boardToCode(board)
                mirrorCode = getMirrorCode(deepcopy(pieces))
                if code not in explored and mirrorCode not in explored:
                # if code not in explored:
                    frontier.append(State(board, 0, newDepth, state))
                    explored.add(code)
                if goalTest(board):
                    return
    return

def astarSuccessors(state, explored, frontier):
    newDepth = state.depth + 1
    numP = len(state.board.pieces)
    for i in range(0, numP):
        for direction in directions:
            if canMove(state.board, state.board.pieces[i], direction):
                pieces = deepcopy(state.board.pieces)
                movePiece(pieces[i], direction)
                board = Board(pieces)
                code = boardToCode(board)
                mirrorCode = getMirrorCode(deepcopy(pieces))
                if code not in explored and mirrorCode not in explored:
                    fValue = f(board, "astar", newDepth)
                    heappush(frontier, State(board, fValue, newDepth, state))
                    explored.add(code)
                if goalTest(board):
                    return
    return


def getMirrorCode(pieces):
    for piece in pieces:
        if piece.is_goal or piece.orientation == 'h':
            piece.coord_x = 2 - piece.coord_x
        else:
            piece.coord_x = 3 - piece.coord_x
    board = Board(pieces)
    return boardToCode(board)

def Solver(state, function=None):
    frontier = []
    if function == "astar":
        heapify(frontier)
        heappush(frontier, state)
    else:
        frontier.append(state)
    explored = set()
    explored.add(boardToCode(state.board))
    curr = state
    if function == "dfs":
        while not goalTest(curr.board):
            dfsSuccessors(curr, explored, frontier)
            if frontier == []:
                break
            curr = frontier[-1]
    elif function == "astar":
        while not goalTest(curr.board):
            astarSuccessors(curr, explored, frontier)
            if frontier == []:
                break
            curr = heappop(frontier)
    path = [curr.board]
    while curr.parent:
        path.insert(0, curr.parent.board)
        curr = curr.parent
    return path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzle."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()

    # read the board from the file
    board = read_from_file(args.inputfile)
    fValue = f(board, args.algo, 0)
    state = State(board, fValue, 0)
    result = Solver(state, args.algo)
    with open(args.outputfile, 'w') as f:
        for i in result:
            f.write(i.text())

    # board = read_from_file(os.path.join(os.path.dirname(__file__), "input0.txt"))
    # fValue = f(board, "dfs", 0)
    # state = State(board, fValue, 0)
    # result = Solver(state, "dfs")
    # print(len(result))
    # # for res in result:
    # #     res.display()
    # #     print('\n')