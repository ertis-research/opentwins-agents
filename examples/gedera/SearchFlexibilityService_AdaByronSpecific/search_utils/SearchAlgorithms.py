#from sortedcontainers import SortedSet
from queue import PriorityQueue
import datetime

def BFS(root, environment):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the BFS search
    completed = []
    queue = [root]
    while queue:
        current = queue.pop(0)
        print(current.day_step)
        if current._episode_ended:
            completed.append(current)
        else:
            branch = environment.step(current)
            for node in branch:
                queue.append(node)
    return completed

def DFS(root, environment):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the DFS search
    completed = []
    stack = [root]
    while stack:
        current = stack.pop()
        print(len(stack))
        if current._episode_ended:
            completed.append(current)
            if len(completed) == 1:
                return completed
        else:
            branch = environment.step(current)
            for node in branch:
                stack.append(node)
    return completed

def BFS_poda(root, environment):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the BFS search
    best = float('inf')
    completed = []
    queue = [root]
    while queue:
        current = queue.pop(0)
        
        if current.cumulative_price < best:
            if current._episode_ended:
                completed.append(current)
                best = current.cumulative_price
            else:
                branch = environment.step(current)
                for node in branch:
                    queue.append(node)
    return completed

def DFS_poda(root, environment):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the DFS search
    best = float('inf')
    completed = []
    stack = [root]
    while stack:
        current = stack.pop()
        
        if current.cumulative_price < best:
            if current._episode_ended:
                completed.append(current)
                best = current.cumulative_price
                if len(completed) == 20:
                    return completed
            else:
                branch = environment.step(current)
                for node in branch:
                    stack.append(node)
    return completed

def checkIfSimilar(state):
    actions = []
    best_solution = [0,0,0,0,0,0,0,6,3,15,0,0,0,0,0,0,6,3,15,0,0,0,0,0]
    while state.father is not None:
        actions.append(state.actions["bateria1"])
        state = state.father
    actions.reverse()
    
    
    if len(actions) == len(best_solution):
        for i in range(len(actions)):
            if actions[i] != best_solution[i]:
                #print("Only {} actions are similar".format(i))
                return False
    
        print("Solution is similar to the best solution")
        return True
    else:
        return False

def LowestSearch_Poda(root, environment, maxSolutions, verbose = False):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the BFS search
    hour = datetime.datetime.now()
    max_time = datetime.timedelta(minutes=15)
    best = float('inf')
    completed = []
    best_solution = None
    queue = PriorityQueue()
    queue.put(root)
    
    while queue._qsize() > 0:
        current = queue.get()
        #checkIfSimilar(current)

        if current._episode_ended:
            if current.cumulative_price < best:
                if verbose:
                    print("Found new best solution with price {}".format(current.cumulative_price))
                print("Found new best solution with price {}".format(current.cumulative_price))
                
                best = current.cumulative_price
                completed.append(current)
                best_solution = current
                if len(completed) == maxSolutions:
                        return completed, best_solution
        else:
            branch = environment.step(current)
            for node in branch:
                if node.cumulative_price < best:
                    #print(node)
                    queue.put(node)
                    
        hour2 = datetime.datetime.now()        
        difference = hour2 - hour
        
        if difference >= max_time:
            print("Time limit reached, returning best solution found")
            return completed, best_solution
    print("Can't expand more nodes")
    return completed, best_solution

# Same algorithm as above but modified to maximize price instead of minimize energy consumption
def HighestSearch_Poda(root, environment, maxSolutions = None):
# root is the starting node
    best = -float('inf')
    completed = []
    queue = PriorityQueue()
    queue.put(root)
    contador = 0
    maxPosibleStates = 17**24
    while queue:
        current = queue.get()
        contador += 1
        print(f'{contador}/{maxPosibleStates}', end='\r')
        if current._episode_ended:
            if current.cumulative_price > best:
                print("Found new best solution with price {}".format(current.cumulative_price))
                best = current.cumulative_price
                completed.append(current)
                
                if len(completed) == maxSolutions:
                        return completed
        else:
            branch = environment.step(current)
            for node in branch:
                queue.put(node)
    return completed

def DinamicPrograming(root, environment):
    # pago = [0 for i in n]
    # estados = [root]
    # n = list(range(0, len(environment.consumption_curve)))
    # n.reverse()
    # resolverBottomUp()
    
    
    # def resolverBottomUp():      
    #     for i in n:
    #         pago[i] = resuelve(i)
            
    # def resuelve(i):
    #     if i == len(environment.consumption_curve)-1:
    #         sol = 
    #         return sol
    #     tm = pago[i+1] + estimacion[i]*tarifaMegas
    #     tf = pago[i+permanencia] + permanencia*tarifaPlana
    #     sol = min(tm, tf)
    return 0