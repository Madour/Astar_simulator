# Author: Christian Careaga (christian.careaga7@gmail.com)
# A* Pathfinding in Python (2.7)
# Please give credit if used (2014)

# modified by Modar Nasser (2019)

from heapq import *

obstacles_list = [1, 'x', '@']

def heuristic(a, b):
    return (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2


def astar(array, start, goal, directions = 4):
    start = (start[1], start[0])
    goal = (goal[1], goal[0])

    neighbors = [(0,1),(0,-1),(1,0),(-1,0)]
    if directions == 8:
        neighbors += [(1,1),(1,-1),(-1,1),(-1,-1)]
    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []

    heappush(oheap, (fscore[start], start))
    
    while oheap:

        current = heappop(oheap)[1]

        if current == goal:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            result = []
            decrement = (0,0)
            data.reverse()
            for tuple in data:
                result.append((tuple[1] - start[1] - decrement[0], tuple[0] - start[0] - decrement[1]))
                decrement = (decrement[0] + tuple[1] - start[1] - decrement[0], decrement[1] + tuple[0] - start[0] - decrement[1])
            return result

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j            
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < len(array):
                if 0 <= neighbor[1] < len(array[0]):
                    if array[neighbor[0]][neighbor[1]] in obstacles_list:
                        # un mur
                        continue
                else:
                    # array bound y walls
                    continue
            else:
                # array bound x walls
                continue
                
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                continue
                
            if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1]for i in oheap]:
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heappush(oheap, (fscore[neighbor], neighbor))
                
    return False
