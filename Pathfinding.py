import BinaryTree
import PathfindingBlock
import pygame

white = (255, 255, 255)
red = (255, 0, 0)

class Pathfinding():

    def __init__(self, blockCount, showSpriteGroup, pathSprites):
        # Block count needs to be array in form (horizontalCount, verticalCount)
        self.horizontalCount = blockCount[0]
        self.verticalCount = blockCount[1]
        self.showSpriteGroup = showSpriteGroup
        self.pathSprites = pathSprites
        self.override = False
        self.path = []

    def GetNeighbours(self, sourcePos, endPos, processedList, cellsToSearch):
        # Takes the position of the source cell, and its g cost.
        # Gets the neighbour objects of the said cell and returns them.
        # Also returns a list containing -1 if the target is the neighbour. 
        # In the above case, the returned list also contains the target cell.
        northNPos = (sourcePos[0], sourcePos[1] - 1)
        northWestNPos = (sourcePos[0] + 1, sourcePos[1] - 1)
        westNPos = (sourcePos[0] + 1, sourcePos[1])
        southWesthNPos = (sourcePos[0] + 1, sourcePos[1] + 1)
        southNPos = (sourcePos[0], sourcePos[1] + 1)
        southEastNPos = (sourcePos[0] - 1, sourcePos[1] + 1)
        eastNPos = (sourcePos[0] - 1, sourcePos[1])
        northEastNPos = (sourcePos[0] - 1, sourcePos[1] - 1)
        neighboursPos = [northNPos, northWestNPos, westNPos, southWesthNPos, southNPos, southEastNPos, eastNPos, northEastNPos]
        neighbours = []
        for pos in neighboursPos:
            # Checks if the position exists
            if self.FindCellInfo(pos, 'exists'):

                if self.FindCellInfo(pos, 'isTarget'): # Checks if the target cell is a neighbour
                    if self.CheckIfDiagonal(pos, sourcePos) == False: # Checks if the target cell is at a diagonal distance from the source 
                        self.SetCellInfo(pos, 'parent', sourcePos)
                        return -1 # Returns -1, signifying that the target cell was found
                
                elif not self.FindCellInfo(pos, 'hasObstacle') and pos not in processedList:
                    costToN = self.FindCellInfo(pos, 'g') + self.GetDist(sourcePos, pos) # The g cost from the source cell
                    
                    if self.CheckIfDiagonal(pos, sourcePos) and self.FindCellInfo(pos, 'nextToWall') == True:
                        costToN += 1000

                    if pos not in cellsToSearch or costToN < self.FindCellInfo(pos, 'g'):
                        self.SetCellInfo(pos, 'g', costToN)
                        self.SetCellInfo(pos, 'parent', sourcePos)

                        if pos not in cellsToSearch:
                            self.SetCellInfo(pos, 'h', self.GetDist(pos, endPos))
                            cellsToSearch.append(pos) 
                    neighbours.append(pos)
        return neighbours
    
    def CheckIfDiagonal(self, pos, sourcePos):
        # Checks if a block is diagonal to the player
        diagonalPos = [(pos[0] + 1, pos[1] + 1), (pos[0] - 1, pos[1] + 1), (pos[0] - 1, pos[1] - 1), (pos[0] + 1, pos[1] - 1)]
        for pos in diagonalPos:
            if pos == sourcePos:
                return True
        return False

    def Pathfind(self, originRect, targetRect):
        # The target and origin objects MUST have a rect called "hitboxRect"
        endCellPos = self.GetRectCellPos(targetRect)
        startCellPos = self.GetRectCellPos(originRect)
        #print("Start cell pos:", startCellPos)
        self.SetCellInfo(endCellPos, 'isTarget', True)
        hasCompleted = False
        cellsToSearch = [startCellPos]
        processedCells = []
        neighbours = []
        while not hasCompleted:
            # Get best cell cost
            bestCellPos = cellsToSearch[0]
            bestF = self.FindCellInfo(bestCellPos, 'f')
            self.rootNode = BinaryTree.TreeNode(bestF, bestCellPos)

            for cellPos in cellsToSearch:
                self.rootNode.Insert(self.FindCellInfo(cellPos, 'f'), cellPos)
            lowest = self.rootNode.FindLowest()
            if lowest is None:
                self.rootNode.InorderTraversal()
            lowestF = lowest[0]
            lowestCellPos = lowest[1]

            if lowestF < bestF or (lowestF == bestF and self.FindCellInfo(lowestCellPos, 'h') < self.FindCellInfo(bestCellPos, 'h')):
                bestCellPos = lowestCellPos
            processedCells.append(bestCellPos)
            cellsToSearch.remove(bestCellPos)
            neighbours = self.GetNeighbours(bestCellPos, endCellPos, processedCells, cellsToSearch)
            if neighbours == -1:
                # The below colours the processed cells and cells to search. Doesn't work currently
                #for cellPos in processedCells:
                    #if cellPos != startCellPos:
                        #cell.image.fill(dark_green)
                #for cell in cellsToSearch:
                    #if cell != startCell:
                        #cell.image.fill(light_blue)

                self.CompilePath(startCellPos, endCellPos)
                hasCompleted = True
            if len(cellsToSearch) == 0:
                hasCompleted = True
                print("CANT COMPLETE PATH, ALL PROCESSED")
                return -1
    
    def CompilePath(self, startPos, endPos):
        # Follows the connected cells from start to end 
        # Creates a list of cells to go to
        self.path = [self.GetCell(endPos)]
        cellPos = endPos
        while cellPos != startPos:
            if type(self.FindCellInfo(cellPos, 'g')) == str:
                #If no parent, override pathfinding
                print("ERROR: No parent detected")
                self.override = True
                return
            elif self.FindCellInfo(cellPos, 'g') >= 1000:
                # If g cost bigger than 1000, must've done an illegal path
                print("CANT COMPLETE PATH, ILLEGAL PATH")
                self.override = True
            else:
                self.override = False
            cellPos = self.FindCellInfo(cellPos, 'parent') # Gets cell object of parent cell
            if cellPos != -1:
                cellObject = self.GetCell(cellPos)
                self.path.append(cellObject)
                self.showSpriteGroup.add(cellObject)
        self.CleanPath()
            
        # Reverses order of list since we follow it from end to start
        # in this code, but the enemy needs to follow it from start to end
        self.path.reverse()
    
    def FindCellInfo(self, pos, wanted):
        # Finds cell information from local path map
        if pos == -1 or type(pos) == str:
            print("ERROR: bad pos")
            return "no pos"
        y = pos[1]
        x = pos[0]
        for i in range(self.verticalCount):
            #print("|Calculation:", (y-1)*self.horizontalCount + x-1,"| horizontal count", self.horizontalCount, "|pos wanted:", pos, "Y:", y)
            #print("len:", len(self.localPathMap))
            cell = self.localPathMap[(y-1)*self.horizontalCount + x-1]
            #print("cell pos:", cell[0],"|Calculation:", (y-1)*self.horizontalCount + x-1,"| horizontal count", self.horizontalCount, "|pos wanted:", pos, "Y:", y)
            if cell[0] == pos:
                if wanted == 'g':
                    return cell[1][0]
                if wanted == 'h':
                    return cell[1][1]
                if wanted == 'parent':
                    return cell[1][2]
                if wanted == 'nextToWall':
                    return cell[1][3]
                if wanted == 'hasObstacle':
                    return cell[1][4]
                if wanted == 'isTarget':
                    return cell[1][5]
                if wanted == 'f':
                    f = cell[1][0] + cell[1][1]
                    return f
                if wanted == 'exists':
                    return True
        return 'not found' 
                
    def SetCellInfo(self, pos, wanted, change):
        # Changes cell information from local path map
        if pos == -1 or type(pos) == str:
            print("ERROR: bad pos")
            return "no pos"
        y = pos[1]
        x = pos[0]
        for cell in range(self.verticalCount):
            cell = self.localPathMap[(y-1)*self.horizontalCount + x-1]
            if cell[0] == pos:
                if wanted == 'g':
                    cell[1][0] = change
                if wanted == 'h':
                    cell[1][1] = change
                if wanted == 'parent':
                    cell[1][2] = change
                if wanted == 'nextToWall':
                    cell[1][3] = change
                if wanted == 'hasObstacle':
                    cell[1][4] = change
                if wanted == 'isTarget':
                    cell[1][5] = change

    def GetDist(self, startPos, targetPos):
        changeY = abs(startPos[1] - targetPos[1]) 
        changeX = abs(startPos[0] - targetPos[0])
        if changeX > changeY:
            dist = 14*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 14*(changeX) + 10*(abs(changeY - changeX))
        return dist
    
    def CreateLocalPathMap(self):
        self.localPathMap = [] # 2D list structure works like so: cell position --> g cost, h cost, parent cell, if it's next to a wall, if it has an obstacle, if it's the target
        for sprite in self.pathSprites:
            self.localPathMap.append([sprite.pos, [sprite.g, sprite.h, sprite.connectedCell, sprite.nextToWall, sprite.hasObstacle, sprite.isTarget]])
        self.FixEdges()
    
    def CleanPath(self):
        # Wipes information from the local path map for the next pathfind
        for item in self.localPathMap:
            for i in range(len(item[1])):
                if i < 2:
                    item[1][i] = 0
                elif i == 2:
                    item[1][i] = -1
                elif i != 4 and i != 3:
                    item[1][i] = False
    
    def GetCell(self, pos):
        for cell in self.pathSprites:
            if pos == cell.pos:
                return cell
        return 'no cell found'

    def FixEdges(self):
        for i in self.localPathMap:
            position = i[0]
            if self.FindCellInfo(position, 'hasObstacle'):
                horizontalNPos = [(position[0] + 1, position[1]), (position[0], position[1] + 1), (position[0] - 1, position[1]), (position[0], position[1] - 1)]
                for pos in horizontalNPos:
                    if self.FindCellInfo(pos, 'exists'):
                        self.SetCellInfo(pos, 'nextToWall', True)
    
    def GetRectCellPos(self, rect):
        # Gets the position of a cell colliding with the given rect
        for cell in self.pathSprites:
            if cell.rect.colliderect(rect):
                return cell.pos
    
def CreateObstacleMap(blockCount, blockWidth, obstacles, pathSpritesGroup):
    # Needs to be used before pathfinding method
    # Block count needs to be array in form (horizontalCount, verticalCount)
    verticalCount = blockCount[1]
    horizontalCount = blockCount[0]
    top = 0
    y = 0
    for row in range(verticalCount):
        y += 1
        x = 0
        for column in range(0, horizontalCount):
            x += 1
            block = PathfindingBlock.Block(column * (blockWidth), top, blockWidth, white)
            block.pos = (x,y)
            pathSpritesGroup.add(block)
        top += blockWidth

    for block in pathSpritesGroup:
        blockCollide = pygame.sprite.spritecollide(block, obstacles, False)
        if len(blockCollide) > 0:
            block.changeColour(red)
            block.hasObstacle = True
