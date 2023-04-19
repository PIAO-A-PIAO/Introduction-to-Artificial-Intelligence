import argparse
from copy import deepcopy
from heapq import heappush, heappop, heapify
import math
import sys
import time
import os

cache = {} # you can use this to implement state caching!
explored = set()
DIRECTIONS = [(-1,-1), (-1,1), (1,1),(1,-1)]
LIMIT = 13

class State:
    # This class is used to represent a state.
    # board : a list of lists that represents the 8*8 board
    def __init__(self, board, depth = 0, left = -math.inf, right = math.inf):
        self.depth = depth
        self.children = []
        self.child = None
        self.board = board
        self.value = -math.inf if depth%2==0 else math.inf
        self.left = -math.inf
        self.right = math.inf
        self.evaluate = evaluate(board, self.depth)

    def __lt__(self, other):
        return self.value < other.value

    def display(self):
        for i in self.board:
            for j in i:
                print(j, end="")
            print("")
        print("")
    
    def text(self):
        text = ""
        for i in range(8):
            for j in range(8):
                text += self.board[i][j]
            text += '\n'
        return text

def hashBoard(board,depth):
    code = "r" if depth%2==0 else "b"
    for i in range(8):
        for j in range(8):
            code += board[i][j]
    return code

def get_opp_char(player):
    if player in ['b', 'B']:
        return ['r', 'R']
    else:
        return ['b', 'B']

def get_next_turn(curr_turn):
    if curr_turn == 'r':
        return 'b'
    else:
        return 'r'

def read_from_file(filename):

    f = open(filename)
    lines = f.readlines()
    board = [[str(x) for x in l.rstrip()] for l in lines]
    f.close()

    return board

def Solve(state):
    if endGame(state.board, state.depth):
        # print("found")
        state.value = 200
        return

    if state.depth == LIMIT:
        state.value = evaluate(state.board, state.depth)
        return

    group = ['r', 'R'] if state.depth%2 == 0 else ['b', 'B']
    getSuccessor(state, group)
    pruning = -1
    if state.children == []:
        state.value == 0
        return

    if not state.child:
        state.child = state.children[0]

    for child in state.children:
        child.left = state.left
        child.right = state.right
        Solve(child)
        # if child.value == 200:
        #     state.child = child
        #     state.value = 200
        #     return
        if state.depth%2 == 0:
            if child.value > state.right:
                # print("pruning happend")
                pruning = child.value
                break
            else:
                state.child = max(state.child, child)
                state.value = max(child.value, state.value)
                state.left = max(state.left, state.value)
        else:
            if child.value < state.left:
                # print("pruning happened")
                pruning = child.value
                break
            else:
                state.child = min(state.child, child)
                state.value = min(child.value, state.value)
                state.right = min(state.right, state.value)
    if pruning != -1:
        state.value = pruning
    # print(state.left, state.right)
    return

def evaluate(board, depth):
    count = 50
    enemy = set()
    red = depth%2 == 0
    for i in range(8):
        for j in range(8):
            ch = board[i][j]
            if ch == 'r':
                count += 3+(7-i)
                if jump(board, (i,j)) != []:
                    count += 1
            elif ch == 'b':
                count -= 3+i
                enemy.add((i,j))
                for tup in [(i-2,j),(i+2,j),(i,j-2),(i,j+2),(i-2,j-2),(i-2,j+2),(i+2,j-2),(i+2,j+2)]:
                    if tup in enemy:
                        count += 1
            elif ch == 'R':
                count += 6
                if jump(board, (i,j)) != []:
                    count += 1
            elif ch == 'B':
                count -= 6
                enemy.add((i,j))
                for tup in [(i-2,j),(i+2,j),(i,j-2),(i,j+2),(i-2,j-2),(i-2,j+2),(i+2,j-2),(i+2,j+2)]:
                    if tup in enemy:
                        count += 1
    return count

def endGame(board, depth):
    red = True if depth%2 ==0 else False
    blue = 0
    for i in range(8):
        for j in range(8):
            ch = board[i][j]
            if ch in ['b', 'B']:
                blue += 1
                if not red and move(board, (i,j)) == [] and keepJumping(board, (i,j)):
                    blue -= 1
    return blue == 0

def getSuccessor(state, group):
    temp = []
    jump = False
    for i in range(8):
        for j in range(8):
            if state.board[i][j] in group:
                jumpResult = keepJumping(state.board, (i,j))
                for result in jumpResult:
                    code = hashBoard(result[0],state.depth+1)
                    if code not in explored:
                        explored.add(code)
                        state.children.append(State(result[0], state.depth+1,state.left,state.right))
                        jump = True
                if not jump:
                    moveResult = move(state.board, (i,j))
                    for res in moveResult:
                        code = hashBoard(res,state.depth+1)
                        if code not in explored:
                            explored.add(code)
                            temp.append(State(res, state.depth+1,state.left,state.right))
    if not jump:
        state.children += temp
    if state.depth%2 == 0:
        sorted(state.children, key=lambda x:x.evaluate, reverse=True)
    else:
        sorted(state.children, key=lambda x:x.evaluate)

def keepJumping(board, coord):
    result = jump(board, coord)
    if result == []:
        return []
    final = []
    i = 0
    for i in range(len(result)):
        new = keepJumping(result[i][0],result[i][1])
        if new != []:
            result[i] = (0,0)
            final += new
    for res in result:
        if res != (0,0):
            final.append(res)
    return final

def jump(b, coord):
    result = []
    ch = b[coord[0]][coord[1]]
    king = False
    for direction in DIRECTIONS:
        if canJump(b, coord, direction): 
            board = deepcopy(b)
            board[coord[0]][coord[1]], board[coord[0]+2*direction[0]][coord[1]+2*direction[1]] =\
            board[coord[0]+2*direction[0]][coord[1]+2*direction[1]], board[coord[0]][coord[1]]
            board[coord[0]+direction[0]][coord[1]+direction[1]] = '.'
            if ch == 'r' and coord[0]+2*direction[0] == 0:
                king = True
                board[coord[0]+2*direction[0]][coord[1]+2*direction[1]] = 'R'
            elif ch == 'b' and coord[0]+2*direction[0] == 7:
                king = True
                board[coord[0]+2*direction[0]][coord[1]+2*direction[1]] = 'B'
            newCoord = (-1, -1) if king else (coord[0]+2*direction[0],coord[1]+2*direction[1])
            result.append((board, newCoord))
    return result

def move(b, coord):
    result = []
    for direction in DIRECTIONS:
        if canMove(b, coord, direction):
            board = deepcopy(b)
            ch = board[coord[0]][coord[1]]
            board[coord[0]][coord[1]], board[coord[0]+direction[0]][coord[1]+direction[1]] =\
            board[coord[0]+direction[0]][coord[1]+direction[1]], board[coord[0]][coord[1]]
            if ch == 'r' and coord[0]+direction[0] == 0:
                board[coord[0]+direction[0]][coord[1]+direction[1]] = 'R'
            elif ch == 'b' and coord[0]+direction[0] == 7:
                board[coord[0]+direction[0]][coord[1]+direction[1]] = 'B'
            result.append(board)
    return result

def canMove(board, coord, direction):
        ch = board[coord[0]][coord[1]]
        if ch == 'r' and direction[0] == 1:
            return False
        if ch == 'b' and direction[0] == -1:
            return False
        
        row = coord[0] + direction[0]
        col = coord[1] + direction[1]
        if row < 0 or row > 7 or col < 0 or col > 7:
            return False
        
        return board[coord[0]+direction[0]][coord[1]+direction[1]] == '.'

def canJump(board, coord, direction):
    ch = board[coord[0]][coord[1]]
    if ch == 'r' and direction[0] == 1:
            return False
    if ch == 'b' and direction[0] == -1:
        return False
    
    row = coord[0] + 2 * direction[0]
    col = coord[1] + 2 * direction[1]
    if row < 0 or row > 7 or col < 0 or col > 7:
        return False
    
    return board[coord[0]+direction[0]][coord[1]+direction[1]] in get_opp_char(ch) and board[coord[0]+2*direction[0]][coord[1]+2*direction[1]] == '.'
    

if __name__ == '__main__':
    board = read_from_file(os.path.join(os.path.dirname(__file__), "input1.txt"))
    state = State(board)
    Solve(state)
    curr = state
    while curr:
        print(curr.text()+'\n')
        curr = curr.child
    # parser = argparse.ArgumentParser()
    # parser.add_argument(
    #     "--inputfile",
    #     type=str,
    #     required=True,
    #     help="The input file that contains the puzzles."
    # )
    # parser.add_argument(
    #     "--outputfile",
    #     type=str,
    #     required=True,
    #     help="The output file that contains the solution."
    # )
    # args = parser.parse_args()

    # initial_board = read_from_file(args.inputfile)
    # state = State(initial_board)
    # turn = 'r'
    # ctr = 0
    # Solve(state)
    # with open(args.outputfile, 'w') as f:
    #     curr = state
    #     while curr:
    #         f.write(curr.text()+'\n')
    #         curr = curr.child

    # sys.stdout = open(args.outputfile, 'w')

    # sys.stdout = sys.__stdout__


