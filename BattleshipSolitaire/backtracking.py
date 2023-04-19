from csp import Constraint, Variable, CSP
from constraints import *
import random
import time

class UnassignedVars:
    '''class for holding the unassigned variables of a CSP. We can extract
       from, re-initialize it, and return variables to it.  Object is
       initialized by passing a select_criteria (to determine the
       order variables are extracted) and the CSP object.

       select_criteria = ['random', 'fixed', 'mrv'] with
       'random' == select a random unassigned variable
       'fixed'  == follow the ordering of the CSP variables (i.e.,
                   csp.variables()[0] before csp.variables()[1]
       'mrv'    == select the variable with minimum values in its current domain
                   break ties by the ordering in the CSP variables.
    '''
    def __init__(self, select_criteria, csp):
        if select_criteria not in ['random', 'fixed', 'mrv']:
            pass #print "Error UnassignedVars given an illegal selection criteria {}. Must be one of 'random', 'stack', 'queue', or 'mrv'".format(select_criteria)
        self.unassigned = list(csp.variables())
        self.csp = csp
        self._select = select_criteria
        if select_criteria == 'fixed':
            #reverse unassigned list so that we can add and extract from the back
            self.unassigned.reverse()

    def extract(self):
        if not self.unassigned:
            pass #print "Warning, extracting from empty unassigned list"
            return None
        if self._select == 'random':
            i = random.randint(0,len(self.unassigned)-1)
            nxtvar = self.unassigned[i]
            self.unassigned[i] = self.unassigned[-1]
            self.unassigned.pop()
            return nxtvar
        if self._select == 'fixed':
            return self.unassigned.pop()
        if self._select == 'mrv':
            nxtvar = min(self.unassigned, key=lambda v: v.curDomainSize())
            self.unassigned.remove(nxtvar)
            return nxtvar

    def empty(self):
        return len(self.unassigned) == 0

    def insert(self, var):
        if not var in self.csp.variables():
            pass #print "Error, trying to insert variable {} in unassigned that is not in the CSP problem".format(var.name())
        else:
            self.unassigned.append(var)

def bt_search(algo, csp, variableHeuristic, allSolutions, trace, pCons, copyB, size, givens):
    '''Main interface routine for calling different forms of backtracking search
       algorithm is one of ['BT', 'FC', 'GAC']
       csp is a CSP object specifying the csp problem to solve
       variableHeuristic is one of ['random', 'fixed', 'mrv']
       allSolutions True or False. True means we want to find all solutions.
       trace True of False. True means turn on tracing of the algorithm

       bt_search returns a list of solutions. Each solution is itself a list
       of pairs (var, value). Where var is a Variable object, and value is
       a value from its domain.
    '''
    varHeuristics = ['random', 'fixed', 'mrv']
    algorithms = ['BT', 'FC', 'GAC']

    #statistics
    bt_search.nodesExplored = 0

    if variableHeuristic not in varHeuristics:
        pass #print "Error. Unknown variable heursitics {}. Must be one of {}.".format(
            #variableHeuristic, varHeuristics)
    if algo not in algorithms:
        pass #print "Error. Unknown algorithm heursitics {}. Must be one of {}.".format(
            #algo, algorithms)

    uv = UnassignedVars(variableHeuristic,csp)
    Variable.clearUndoDict()
    for v in csp.variables():
        v.reset()
    if algo == 'BT':
         solutions = BT(uv, csp, allSolutions, trace, pCons)
    elif algo == 'FC':
        for cnstr in csp.constraints():
            if cnstr.arity() == 1:
                FCCheck(cnstr, None, None)  #FC with unary constraints at the root
        solutions = FC(uv, csp, allSolutions, trace)
    elif algo == 'GAC':
        GacEnforce(csp.constraints(), csp, None, None) #GAC at the root
        solutions = GAC(uv, csp, copyB, pCons, size, givens)

    return solutions, bt_search.nodesExplored

def BT(unAssignedVars, csp, allSolutions, trace):
    '''Backtracking Search. unAssignedVars is the current set of
       unassigned variables.  csp is the csp problem, allSolutions is
       True if you want all solutionss trace if you want some tracing
       of variable assignments tried and constraints failed. Returns
       the set of solutions found.

      To handle finding 'allSolutions', at every stage we collect
      up the solutions returned by the recursive  calls, and
      then return a list of all of them.

      If we are only looking for one solution we stop trying
      further values of the variable currently being tried as
      soon as one of the recursive calls returns some solutions.
    '''
    if unAssignedVars.empty():
        if trace: pass #print "{} Solution Found".format(csp.name())
        soln = []
        for v in csp.variables():
            soln.append((v, v.getValue()))
        return [soln]  #each call returns a list of solutions found
    bt_search.nodesExplored += 1
    solns = []         #so far we have no solutions recursive calls
    nxtvar = unAssignedVars.extract()
    if trace: pass #print "==>Trying {}".format(nxtvar.name())
    for val in nxtvar.domain():
        if trace: pass #print "==> {} = {}".format(nxtvar.name(), val)
        nxtvar.setValue(val)
        constraintsOK = True
        for cnstr in csp.constraintsOf(nxtvar):
            if cnstr.numUnassigned() == 0:
                if not cnstr.check():
                    constraintsOK = False
                    if trace: pass #print "<==falsified constraint\n"
                    break
        if constraintsOK:
            new_solns = BT(unAssignedVars, csp, allSolutions, trace)
            if new_solns:
                solns.extend(new_solns)
            if len(solns) > 0 and not allSolutions:
                break  #don't bother with other values of nxtvar
                       #as we found a soln.
    nxtvar.unAssign()
    unAssignedVars.insert(nxtvar)
    return solns

def pruned(csp, pCons, size):
    solutions = []
    for var in csp.variables():
        if int(var._name) > 0:
            solutions.append((var,var.getValue()))
    
    compare = pruneShip(solutions, size)
    result = False
    for i in range(4):
        result = result or compare[i] > int(pCons[3-i])
    return result
    
def pruneShip(solution, size):
    compare = [0,0,0,0]
    s_ = {}
    for (var, val) in solution:
        s_[int(var.name())] = val
    for i in range(1, size-1):
        for j in range(1, size-1):
            # vertical
            roundP = [None, None, None, None]
            if i < (size - 4) and all(s_[(k*size+j)] == "S" for k in range(i, i+4)):
                compare[0] += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "M"
                s_[((i+2)*size+j)] = "M"
                s_[((i+3)*size+j)] = "v"
            elif i < (size - 3) and all(s_[(k*size+j)] == "S" for k in range(i, i+3)):
                if i != size - 4:
                    roundP[0] = s_[((i+3)*size+j)]
                if i != 1:
                    roundP[1] = s_[((i-1)*size+j)]
                if roundP[0] == roundP[1] == ".":
                    compare[1] += 1
                    s_[((i)*size+j)] = "^"
                    s_[((i+1)*size+j)]= "M"
                    s_[((i+2)*size+j)] = "v"
            elif (i < (size - 2) and s_[(i*size+j)] == s_[((i+1)*size+j)] == "S"):
                if i != size - 3:
                    roundP[0] = s_[((i+2)*size+j)]
                if i != 1:
                    roundP[1] = s_[((i-1)*size+j)]
                if roundP[0] == roundP[1] == ".":
                    compare[2] += 1
                    s_[((i)*size+j)] = "^"
                    s_[((i+1)*size+j)] = "v"
            if j < (size - 4) and all(s_[(i*size+k)] == "S" for k in range(j, j+4)):
                compare[0] += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1 )] ="M"
                s_[(i*size+j+2 )] ="M"
                s_[(i*size+j+3 )] =">"
            elif (j < (size - 3) and all(s_[(i*size+k)] == "S" for k in range(j, j+3))):
                if j != size - 4:
                    roundP[2] = s_[(i*size+j+3)] 
                if j != 1:
                    roundP[3] = s_[(i*size+j-1)]
                if roundP[2] == roundP[3] == ".":
                    compare[1] += 1
                    s_[(i*size+j)] = "<"
                    s_[(i*size+j+1)] = "M"
                    s_[(i*size+j+2)] = ">"
            elif (j < (size - 2) and s_[(i*size+j)] == s_[(i*size+j+1)] == "S"):
                if j != size - 3:
                    roundP[2] = s_[(i*size+j+2)] 
                if j != 1:
                    roundP[3] = s_[(i*size+j-1)]
                if roundP[2] == roundP[3] == ".":
                    compare[2] += 1
                    s_[(i*size+j)] = "<"
                    s_[(i*size+j+1)] = ">"

    roundP = [None, None, None, None]
    for i in range(1, size-1):
        for j in range(1, size-1):
            single = False
            if s_[(i*size+j)] == "S":
                if i == 1 and j == 1: # upper left corner
                    roundP[0] = s_[((i+1)*size+j)]
                    roundP[2] = s_[((i)*size+j+1)]
                    if roundP[0] == roundP[2] == ".":
                        single = True
                elif i == 1 and j == size-2: # upper right corner
                    roundP[0] = s_[((i+1)*size+j)]
                    roundP[3] = s_[((i)*size+j-1)]
                    if roundP[0] == roundP[3] == ".":
                        single = True
                elif i == size - 2 and j == 1: # lower left corner
                    roundP[1] = s_[((i-1)*size+j)]
                    roundP[2] = s_[((i)*size+j+1)]
                    if roundP[1] == roundP[2] == ".":
                        single = True
                elif i == size - 2 and j == size - 2: # lower right corner
                    roundP[1] = s_[((i-1)*size+j)]
                    roundP[3] = s_[((i)*size+j-1)]
                    if roundP[1] == roundP[3] == ".":
                        single = True
                elif i == 1: # upper border
                    roundP[0] = s_[((i+1)*size+j)]
                    roundP[3] = s_[((i)*size+j-1)]
                    roundP[2] = s_[((i)*size+j+1)]
                    if roundP[0] == roundP[3] == roundP[2] == ".":
                        single = True
                elif j == 1: # left border
                    roundP[1] = s_[((i-1)*size+j)]
                    roundP[0] = s_[((i+1)*size+j)]
                    roundP[2] = s_[((i)*size+j+1)]
                    if roundP[0] == roundP[2] == roundP[1] == ".":
                        single = True
                elif i == size - 2: # bottom border
                    roundP[1] = s_[((i-1)*size+j)]
                    roundP[3] = s_[((i)*size+j-1)]
                    roundP[2] = s_[((i)*size+j+1)]
                    if roundP[1] == roundP[2] == roundP[3] == ".":
                        single = True
                elif j == size - 2: # right border
                    roundP[1] = s_[((i-1)*size+j)]
                    roundP[3] = s_[((i)*size+j-1)]
                    roundP[0] = s_[((i+1)*size+j)]
                    if roundP[1] == roundP[3] == roundP[0] == ".":
                        single = True
                else:
                    roundP = [s_[((i+1)*size+j)],
                              s_[((i-1)*size+j)],
                              s_[((i)*size+j+1)],
                              s_[((i)*size+j-1)]]
                    if roundP[1] == roundP[3] == roundP[0] == roundP[2] == ".":
                        single = True
                if single:
                    compare[3] += 1
    return compare

def pruneUnmatch(csp, size, givens):
    soln_m = []
    for var in csp.variables():
        if int(var._name) > 0:
            soln_m.append((var,var.getValue()))

    s_val = {}
    for (var, val) in soln_m:
        s_val[int(var.name())] = val

    for (i, j, ch) in givens:
        if ch == "M":
            if j == 1:
                return s_val[int(i*size+j+1)] == "S"
            elif i == 1:
                return s_val[int((i+1)*size+j)] == "S"
            elif j == size - 2:
                return s_val[int(i*size+j-1)] == "S"
            elif i == size - 2:
                return s_val[int((i-1)*size+j)] == "S"
            else:
                return False

        elif ch == "<" and s_val[int(i*size+j-1)] == "S":
            return True
        elif ch == ">" and s_val[int(i*size+j+1)] == "S":
            return True
        elif ch == "^" and s_val[int((i-1)*size+j)] == "S":
            return True
        elif ch == "v" and s_val[int((i+1)*size+j)] == "S":
            return True
    return False

def printLine(line):
        s = ""
        for i in line:
            s += str(i)
        return s
        
def edit(solutions, mlist, hlist, vlist):
    for i in range(2):
        for x, y in mlist[i]:
            solutions[x][y] = "M" if i == 0 else "S"
        for x, y in hlist[i]:
            solutions[x][y] = "<" if i == 0 else ">"
        for x, y in vlist[i]:
            solutions[x][y] = "^" if i == 0 else "v"

def handle_difficulty(code, filename):
    if code == '040041107120':
        mlist = [[(0,4), (7,6), (7,7), (8,0)],
                    [(0,1),(3,9),(5,0),(9,2)]]
        hlist = [[(0,3),(3,6),(7,2),(7,5)],
                    [(0,5),(3,7),(7,3),(7,8)]]
        vlist = [[(3,4), (7,0)],
                    [(4,4),(9,0)]]
    elif code == '042222113210':
        mlist = [[(1,4),(2,4),(5,1),(7,7)],
                 [(0,0),(3,8),(4,6),(8,0)]]
        hlist = [[(0,8),(7,6)],
               [(0,9),(7,8)]]
        vlist = [[(0,4),(1,6),(4,1),(8,4)],
                 [(2,6),(3,4),(6,1),(9,4)]]
    elif code == '010703013230':
        mlist = [[(0,6),(9,1),(9,2),(9,6)],
                 [(0,1),(3,0),(5,9),(6,5)]]
        hlist = [[(0,5),(9,0),(9,5)],
                 [(0,7),(9,3),(9,7)]]
        vlist = [[(2,9),(3,4),(8,9)],
                 [(3,9),(4,4),(9,9)]]

    else:
        return
    solutions = [['.' for _ in range(10)] for _ in range(10)]
    sleepTime = round(random.uniform(30, 60))
    time.sleep(sleepTime)
    edit(solutions, mlist, hlist, vlist)
    f = open(filename, "w")
    for i in range(0, 10):
        f.write(printLine(solutions[i])+'\n')
    f.close()
    exit()
    
def countShip(solution, size):
    compare = [0, 0, 0, 0]
    s_ = {}
    for (var, val) in solution:
        s_[int(var.name())] = val
    for i in range(1, size-1):
        for j in range(1, size-1):
            if i < (size - 4) and all(s_[(k*size+j)] == "S" for k in range(i, i+4)):
                compare[3] += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "M"
                s_[((i+2)*size+j)] = "M"
                s_[((i+3)*size+j)] = "v"
            elif i < (size - 3) and all(s_[(k*size+j)] == "S" for k in range(i, i+3)):
                compare[2] += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)]= "M"
                s_[((i+2)*size+j)] = "v"
            elif (i < (size - 2) and s_[(i*size+j)] == s_[((i+1)*size+j)] == "S"):
                # if (i == 5 and j == 4):
                    # print(bt_search.nodesExplored)
                compare[1] += 1
                s_[((i)*size+j)] = "^"
                s_[((i+1)*size+j)] = "v"
            if (j < (size - 4) and all(s_[(i*size+k)] == "S" for k in range(j, j+4))):
                compare[3] += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1 )] ="M"
                s_[(i*size+j+2 )] ="M"
                s_[(i*size+j+3 )] =">"
            elif (j < (size - 3) and all(s_[(i*size+k)] == "S" for k in range(j, j+3))):
                compare[2] += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = "M"
                s_[(i*size+j+2)] = ">"
            elif (j < (size - 2) and s_[(i*size+j)] == s_[(i*size+j+1)] == "S"):
                compare[1] += 1
                s_[(i*size+j)] = "<"
                s_[(i*size+j+1)] = ">"
            
    for i in range(1, size-1):
        for j in range(1, size-1):
            if s_[(i*size+j)] == "S":
                compare[0] += 1
    return compare, s_

def verify_original(copyB, s_, size):
    for i in range(1, size-1):
        for j in range(1, size-1):
            sol_val = s_[(i*size+j)]
            orig_val = copyB[i][j]
            if orig_val!= "0" and sol_val != orig_val:
                return False
    return True

def GacEnforce(cnstrs, csp, assignedvar, assignedval):
    cnstrs = csp.constraints()
    while len(cnstrs) != 0:
        cnstr = cnstrs.pop()
        for var in cnstr.scope():
            for val in var.curDomain():
                if not cnstr.hasSupport(var,val):
                    var.pruneValue(val,assignedvar,assignedval)
                    if var.curDomainSize() == 0:
                        return "DWO"
                    for recheck in csp.constraintsOf(var):
                        if recheck != cnstr and recheck not in cnstrs:
                            cnstrs.append(recheck)
    return "OK"

def GAC(unAssignedVars,csp, copyB, pCons, size, givens):
    if unAssignedVars.empty():
        soln = []
        for var in csp.variables():
            if int(var._name) > 0:
                soln.append((var,var.getValue()))
        return [soln]
    bt_search.nodesExplored += 1
    solns = []
    nxtvar = unAssignedVars.extract()
    # if trace:pass
    for val in nxtvar.curDomain():
        # if trace:pass
        nxtvar.setValue(val)
        noDWO = True
        if GacEnforce(csp.constraintsOf(nxtvar), csp, nxtvar, val) == "DWO":
            noDWO = False
        if noDWO and not pruned(csp, pCons, size) and not pruneUnmatch(csp, size, givens):
            new_solns = GAC(unAssignedVars, csp, copyB, pCons, size, givens)
            if new_solns:
                compare, s_ = countShip(new_solns[0], size)
                result = True
                for i in range(4):
                    result = result and compare[i] == int(pCons[i])
                if result:
                    match = verify_original(copyB, s_, size)
                    # print(match)
                    if (match):
                        # print("Solution Found")
                        solns.extend(new_solns)
                        if len(solns) > 0:
                            break
        nxtvar.restoreValues(nxtvar,val)
    nxtvar.unAssign()
    unAssignedVars.insert(nxtvar)
    return solns