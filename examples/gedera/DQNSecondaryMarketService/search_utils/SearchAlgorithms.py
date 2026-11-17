#from sortedcontainers import SortedSet
from queue import PriorityQueue


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

def DFS(root, environment, maxSolutions = None):
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
            if maxSolutions is not None and len(completed) == maxSolutions:
                return completed
        else:
            branch = environment.step(current)
            for node in branch:
                stack.append(node)
    return completed

# TODO: REVISAR
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


def DFS_poda(root, environment, maxSolutions = None):
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
                # if maxSolutions is not None and len(completed) == maxSolutions:
                #     return completed
            else:
                branch = environment.step(current)
                for node in branch:
                    stack.append(node)
    return completed

def DFS_secundario(root, environment, maxSolutions = None):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the DFS search
    best = -float('inf')
    completed = []
    stack = [root]
    while stack:
        print(len(stack))
        current = stack.pop()
        if current._episode_ended and current.cumulative_price > best:
            completed.append(current)
            best = current.cumulative_price
            if maxSolutions is not None and len(completed) == maxSolutions:
                return completed
        elif not current._episode_ended:
            branch = environment.step(current)
            for node in branch:
                stack.append(node)
    return completed


# TODO: REVISAR
def LowestSearch_Poda(root, environment, maxSolutions):
# root is the starting node
# returns a list of the nodes of G in the order they were visited
# in the BFS search
    best = float('inf')
    completed = []
    queue = PriorityQueue()
    queue.put(root)
    while queue:
        current = queue.get()
        if current._episode_ended:
            if current.cumulative_price < best:
                print("Found new best solution with price {}".format(current.cumulative_price))
                best = current.cumulative_price
                completed.append(current)
                if len(completed) == maxSolutions:
                        return completed
        else:
            branch = environment.step(current)
            for node in branch:
                if node.cumulative_price < best:
                    #print(node)
                    queue.put(node)
    return completed


# TODO: REVISAR
# Same algorithm as above but modified to maximize price instead of minimize energy consumption
def HighestSearch_Poda(root, environment, maxSolutions = None):
# root is the starting node
    best = -float('inf')
    completed = []
    queue = PriorityQueue()
    queue.put(root)
    while queue:
        current = queue.get()
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