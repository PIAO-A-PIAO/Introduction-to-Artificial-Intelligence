from oldcsp import Constraint, Variable, CSP
from oldconstraints import *
from backtracking import bt_search, handle_difficulty
import sys
import argparse
import time
ti = time.time()
def print_solution(s, size):
    s_ = {}
    for (var, val) in s:
        s_[int(var.name())] = val

    for i in range(1, size-1):
        for j in range(1, size-1):
            # SSSS
            if j < (size - 3) and s_[(i*size+j)] == "S" and s_[(i*size+j+1)] == "S" and s_[(i*size+j+2)] == "S" and s_[(i*size+j+3)] == "S":
                # four += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1 )] ="M"
                s_[(i*size+j+2 )] ="M"
                s_[(i*size+j+3 )] =">"
            elif j < (size - 2) and s_[(i*size+j)] == "S" and s_[(i*size+j+1)] == "S" and s_[(i*size+j+2)] == "S":
                # three += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = "M"
                s_[(i*size+j+2)] = ">"
            elif j < (size - 1) and s_[(i*size+j)] == "S" and s_[(i*size+j+1)] == "S":
                # two += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = ">"
            if i < (size - 3) and s_[(i*size+j)] == "S" and s_[((i+1)*size+j)] == "S" and s_[((i+2)*size+j)] == "S" and s_[((i+3)*size+j)] == "S":
                # four += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "M"
                s_[((i+2)*size+j)] = "M"
                s_[((i+3)*size+j)] = "v"
            elif i < (size - 2) and s_[(i*size+j)] == "S" and s_[((i+1)*size+j)] == "S" and s_[((i+2)*size+j)] == "S":
                # three += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)]= "M"
                s_[((i+2)*size+j)] = "v"
            elif i < (size - 1) and s_[(i*size+j)] == "S" and s_[((i+1)*size+j)] == "S":
                # two += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "v"
        
    for i in range(1, size-1):
        for j in range(1, size-1):
            if s_[(i*size+j)] == None:
                print("0",end="")
            else:
                print(s_[(i*size+j)],end="")
        print('')

def output(filename, sol, size):
    f = open(filename, "a")
    f.seek(0)
    f.truncate()

    s_ = {}
    for (var, val) in sol:
        s_[int(var.name())] = val

    for i in range(1, size-1):
        for j in range(1, size-1):
            if j < (size - 3) and all(s_[(i*size+k)] == "S" for k in range(j, j+4)):
                # four += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1 )] ="M"
                s_[(i*size+j+2 )] ="M"
                s_[(i*size+j+3 )] =">"
            elif j < (size - 2) and all(s_[(i*size+k)] == "S" for k in range(j, j+3)):
                # three += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = "M"
                s_[(i*size+j+2)] = ">"
            elif j < (size - 1) and s_[(i*size+j)] == s_[(i*size+j+1)] == "S":
                # two += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = ">"
            if i < (size - 3) and all(s_[(k*size+j)] == "S" for k in range(i, i+4)):
                # four += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "M"
                s_[((i+2)*size+j)] = "M"
                s_[((i+3)*size+j)] = "v"
            elif i < (size - 2) and all(s_[(k*size+j)] == "S" for k in range(i, i+3)):
                # three += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)]= "M"
                s_[((i+2)*size+j)] = "v"
            elif i < (size - 1) and s_[(i*size+j)] == s_[((i+1)*size+j)] == "S":
                # two += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "v"
        
    for i in range(1, size-1):
        for j in range(1, size-1):
            f.write(s_[(i*size+j)])
        if i != (size-2):
            f.write("\n")
    f.close()

# parser = argparse.ArgumentParser()
# parser.add_argument(
#     "--inputfile",
#     type=str,
#     required=True,
#     help="The input file that contains the puzzle."
# )
# parser.add_argument(
#     "--outputfile",
#     type=str,
#     required=True,
#     help="The output file that contains the solution."
# )

# args = parser.parse_args()


inputfile = "/Users/user/Documents/UofT/4/CSC384/newA3/mid3.txt"

# file = open(args.inputfile, 'r')
file = open(inputfile, 'r')

b = file.read()
b2 = b.split()
piece_constraint = b2[2]
size = len(b2[0])
size = size + 2
b3 = []
b3 += ['0' + b2[0] + '0']
b3 += ['0' + b2[1] + '0']
b3 += [b2[2] + ('0' if len(b2[2]) == 3 else '')]
b3 += ['0' * size]
for i in range(3, len(b2)):
    b3 += ['0' + b2[i] + '0']
b3 += ['0' * size]
board = "\n".join(b3)

varList = []
varn = {}
conList = []

givens = []

copyB = board.split()[3:]
#1/0 variables
for i in range(0,size):
    for j in range(0, size):
        v = None
        if i == 0 or i == size-1 or j == 0 or j == size-1:
            v = Variable(str(-1-(i*size+j)), [0])
        else:
            ch = copyB[i][j]
            v = Variable(str(-1-(i*size+j)), [0,1])
            if ch != "0":
                givens.append((i,j,ch))

        varList.append(v)
        varn[str(-1-(i*size+j))] = v


#make 1/0 variables match board info
ii = 0
for i in board.split()[3:]:
    jj = 0
    for j in i:
        if j != '0' and j != '.':
            conList.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[1]]))
        elif j == '.':
            conList.append(TableConstraint('boolean_match', [varn[str(-1-(ii*size+jj))]], [[0]]))
        jj += 1
    ii += 1

#row and column constraints on 1/0 variables
rowCons = []
for i in board.split()[0]:
    rowCons += [int(i)]
for row in range(0,size):
    conList.append(NValuesConstraint('row', [varn[str(-1-(row*size+col))] for col in range(0,size)], [1], rowCons[row], rowCons[row]))

colConst = []
for i in board.split()[1]:
    colConst += [int(i)]
for col in range(0,size):
    conList.append(NValuesConstraint('col', [varn[str(-1-(col+row*size))] for row in range(0,size)], [1], colConst[col], colConst[col]))

#diagonal constraints on 1/0 variables
for i in range(1, size-1):
    for j in range(1, size-1):
        for k in range(9):
            conList.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j-1)))]], [1], 0, 1))
            conList.append(NValuesConstraint('diag', [varn[str(-1-(i*size+j))], varn[str(-1-((i-1)*size+(j+1)))]], [1], 0, 1))

for i in range(0, size):
    for j in range(0, size):
        v = Variable(str(i*size+j), ['.', 'S'])
        varList.append(v)
        varn[str(i*size+j)] = v
        conList.append(TableConstraint('connect', [varn[str(-1-(i*size+j))], varn[str(i*size+j)]], [[0,'.'],[1,'S']]))


#find all solutions and check which one has right ship #'s
csp = CSP('battleship', varList, conList)
# handle_difficulty(b3[0], args.outputfile)
ts = time.time()
solutions, num_nodes = bt_search('GAC', csp, 'mrv', False, False, piece_constraint, copyB, size, givens)
for i in range(len(solutions)):
    # output(filename=args.outputfile, sol=solutions[i], size=size)
    print_solution(solutions[i], size)
te = time.time()
print(te-ts)
print(ts-ti)
