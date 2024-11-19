import pygame
import PathfindingBlock

white = (255, 255, 255)
red = (255, 0, 0)
purple = (128, 0, 128)

class VectorFieldPathfinding():
    def __init__(self, blockCount, targetRect, pathSprites):
        self.horizontalCount = blockCount[0]
        self.verticalCount = blockCount[1]
        self.targetRect = targetRect
        self.pathSprites = pathSprites
        self.pathRectList = []
        for cell in self.pathSprites:
            self.pathRectList.append(cell.rect)

    def CreateMap(self):
        self.targetPos = self.GetRectCellPos(self.targetRect)
        self.GenerateHeatMap(self.targetPos)
        self.GenerateVectorField()

    def GetDirection(self, rect):
        startPos = self.GetRectCellPos(rect)
        vector = self.FindCellInfo(startPos, "vector")
        return vector

    def GetNeighbours(self, sourcePos):
        # Takes the position of the source cell
        # Gets the neighbour objects of the said cell and returns them. 
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
                neighbours.append(pos)
        return neighbours
    

    def GenerateHeatMap(self, endPos):
        openList = [endPos]
        currentPos = endPos
        neighbourNodes = self.GetNeighbours(endPos)
        while len(openList) > 0: 
            #print("current pos:", currentPos, "| len open list:", len(openList))
            for pos in neighbourNodes:
                if not self.FindCellInfo(pos, "hasObstacle") and pos not in openList:
                    distFromTarget = self.GetDist(pos, endPos) + self.GetDist(pos, currentPos)
                    if self.FindCellInfo(pos, "visited"):
                        if distFromTarget < self.FindCellInfo(pos, "distToTarget"):
                            self.SetCellInfo(currentPos, "distToTarget", distFromTarget)
                    else:
                        self.SetCellInfo(currentPos, "distToTarget", distFromTarget)
                        self.SetCellInfo(currentPos, "visited", True)
                        openList.append(pos)
            openList.remove(currentPos)
            if len(openList) > 0:
                currentPos = openList[0]
                neighbourNodes = self.GetNeighbours(currentPos)
    
    def GenerateVectorField(self):
        for pos in self.posList:
            count = 0
            #print("pos:", pos)
            neighbours = self.GetNeighbours(pos)
            vectorConvolutionX = 0
            vectorConvolutionY = 0
            ownMagnitude = self.FindCellInfo(pos, "distToTarget")
            for npos in neighbours:
                magnitude = self.FindCellInfo(npos, "distToTarget")
                magnitude = abs(ownMagnitude - magnitude)
                if magnitude != 0:
                    nvector = pygame.math.Vector2(npos[0]-pos[0], npos[1]-pos[1])
                    #print("magnitude:", magnitude)
                    newMagnitude = 1/magnitude
                    nvector.scale_to_length(newMagnitude)
                    vectorConvolutionX += nvector.x
                    vectorConvolutionY += nvector.y
                else:
                    count += 1
                    #print("count:", count)
            print("new vector:", (vectorConvolutionX, vectorConvolutionY))
            newVector = pygame.math.Vector2(vectorConvolutionX, vectorConvolutionX)
            if newVector.magnitude() != 0:
                newVector = newVector.normalize()
            self.SetCellInfo(pos, "vector", newVector)
    
    def CreateLocalPathMap(self):
        self.localPathMap = [] # 2D list structure works like so: cell position --> g cost, h cost, parent cell, if it's next to a wall, if it has an obstacle, if it's the target
        self.posList = []
        for sprite in self.pathSprites:
            self.localPathMap.append([sprite.pos, [sprite.distToTarget, sprite.nextToWall, sprite.hasObstacle, sprite.visited, sprite.vector]])
            self.posList.append(sprite.pos)
        self.FixEdges()
    
    def FixEdges(self):
        for i in self.localPathMap:
            position = i[0]
            if self.FindCellInfo(position, 'hasObstacle'):
                horizontalNPos = [(position[0] + 1, position[1]), (position[0], position[1] + 1), (position[0] - 1, position[1]), (position[0], position[1] - 1)]
                for pos in horizontalNPos:
                    if self.FindCellInfo(pos, 'exists'):
                        self.SetCellInfo(pos, 'nextToWall', True)
                        cellObject = self.GetCell(pos)
                        if type(cellObject) != str:
                            if not cellObject.hasObstacle:
                                cellObject.changeColour(purple)
    
    def GetDist(self, startPos, targetPos):
        changeY = abs(startPos[1] - targetPos[1]) 
        changeX = abs(startPos[0] - targetPos[0])
        if changeX > changeY:
            dist = 14*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 14*(changeX) + 10*(abs(changeY - changeX))
        return dist

    def GetRectCellPos(self, rect):
        # Gets the position of a cell colliding with the given rect
        indices = rect.collidelistall(self.pathRectList)
        for i in indices:
            cell = self.pathSprites.sprites()[i]
            if not cell.hasObstacle:
                return cell.pos
    
    def FindCellInfo(self, pos, wanted):
        # Finds cell information from local path map
        if pos == -1 or type(pos) == str:
            print("ERROR: bad pos")
            return "no pos"
        y = pos[1]
        x = pos[0]
        #print("|Calculation:", (y-1)*self.horizontalCount + x-1,"| horizontal count", self.horizontalCount, "| vertical:", self.verticalCount, "|pos wanted:", pos)
        #print("len:", len(self.localPathMap))
        calculatedIndex = (y-1)*self.horizontalCount + x-1
        #print("index:", calculatedIndex, "| len:", len(self.localPathMap))
        if calculatedIndex >= len(self.localPathMap) and wanted == 'exists':
            return False
        cell = self.localPathMap[calculatedIndex]
        if cell[0] == pos:
            if wanted == 'distToTarget':
                return cell[1][0]
            if wanted == 'nextToWall':
                return cell[1][1]
            if wanted == 'hasObstacle':
                return cell[1][2]
            if wanted == 'visited':
                return cell[1][3]
            if wanted == 'vector':
                return cell[1][4]
            if wanted == 'exists':
                return True
        if cell[0] != pos:
            if wanted == 'exists':
                return False
        return 'not found' 
                
    def SetCellInfo(self, pos, wanted, change):
        # Changes cell information from local path map
        if pos == -1 or type(pos) == str:
            print("ERROR: bad pos")
            return "no pos"
        y = pos[1]
        x = pos[0]
        cell = self.localPathMap[(y-1)*self.horizontalCount + x-1]
        if cell[0] == pos:
            if wanted == 'distToTarget':
                cell[1][0] = change
            if wanted == 'nextToWall':
                cell[1][1] = change
            if wanted == 'hasObstacle':
                cell[1][2] = change
            if wanted == 'visited':
                cell[1][3] = change
            if wanted == 'vector':
                cell[1][4] = change
    
    def CleanPath(self):
        # Wipes information from the local path map for the next pathfind
        for item in self.localPathMap:
            item[1][3] = False
    
    def GetCell(self, pos):
        x = pos[0]
        y = pos[1]
        calculatedIndex = (y-1)*self.horizontalCount + x-1
        if calculatedIndex <= len(self.pathSprites):
            return self.pathSprites.sprites()[calculatedIndex]
        else:
            return 'no cell found'
    
    def DrawVectorMap(self, screen, camera):
        for pos in self.posList:
            cell = self.GetCell(pos)
            cellPosition = cell.rect.center
            cellX = (cellPosition[0] - camera.offset.x) * camera.zoomLevel
            cellY = (cellPosition[1] - camera.offset.y) * camera.zoomLevel
            vector = self.FindCellInfo(pos, "vector")
            pygame.draw.line(screen, 'green', (cellX, cellY), (cellX + vector.x * 5, cellY + vector.y* 5))
        
def CreateObstacleMap(blockCount, blockWidth, obstacles, pathSpritesGroup, top, firstWallIndex):
    # Needs to be used before pathfinding method
    # Block count needs to be array in form (horizontalCount, verticalCount)
    verticalCount = blockCount[1]
    horizontalCount = blockCount[0]
    top = top
    y = 0
    for row in range(verticalCount):
        y += 1
        x = 0
        for column in range(0, horizontalCount):
            x += 1
            block = PathfindingBlock.Block(column * (blockWidth) + firstWallIndex*blockWidth, top, blockWidth, white)
            block.pos = (x,y)
            pathSpritesGroup.add(block)
        top += blockWidth

    for block in pathSpritesGroup:
        blockCollide = pygame.sprite.spritecollide(block, obstacles, False)
        if len(blockCollide) > 0:
            block.changeColour(red)
            block.hasObstacle = True