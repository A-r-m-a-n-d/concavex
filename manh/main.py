

def distance(la, lb):
    ax,ay = la
    bx,by = lb
    return abs(bx - ax) + abs(by - ay)


def main(maze, playerLocation, opponentLocation):

    closest_poc = (-1,-1)
    best_distance = len(maze)+len(maze[0])
    piecesOfCheese=[]
    for i in range(len(maze)):
        
        for j in range(len(maze[i])):
            
            if maze[i][j]=='$':
                piecesOfCheese.append([j,i])
    a=opponentLocation


    for poc in piecesOfCheese:
        ax, ay = poc
        bx, by = playerLocation
        y= abs(bx - ax) + abs(by - ay)
        if y < best_distance:
            best_distance = y
            closest_poc = poc
    ax, ay = playerLocation
    bx, by = closest_poc
    if bx > ax and maze[playerLocation[0]][playerLocation[1] + 1]!="#":
        return 'D'
    if bx < ax and maze[playerLocation[0]][playerLocation[1] - 1]!="#":
        return 'G'
    if by > ay and maze[playerLocation[0] - 1][playerLocation[1]]!="#":
        return 'H'
    if by < ay and maze[playerLocation[0] + 1][playerLocation[1]]!="#":
        return 'B'
    pass
