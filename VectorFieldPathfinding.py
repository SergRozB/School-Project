import pygame
import PathfindingBlock
import cProfile

white = (255, 255, 255)
red = (255, 0, 0)
purple = (128, 0, 128)
posLookUp = {}
vertCount = 0
horzCount = 0

class VectorFieldPathfinding():
    def __init__(self, blockCount, targetRect, pathSprites):
        self.horizontalCount = blockCount[0]
        self.verticalCount = blockCount[1]
        self.targetRect = targetRect
        self.pathSprites = pathSprites
        self.pathRectList = []
        self.targetPos = 0

        for cell in self.pathSprites:
            self.pathRectList.append(cell.rect)

        self.wantedDict = {
            'distToTarget' : 0,
            'nextToWall' : 1,
            'hasObstacle' : 2,
            'visited' : 3,
            'vector' : 4
        }
    
    def ResetTarget(self, targetRect):
        self.targetRect = targetRect

    def CreateMap(self):
        self.CleanPath()
        self.targetPos = self.GetRectCellPos(self.targetRect)
        self.GenerateHeatMap(self.targetPos)
        #cProfile.runctx('self.GenerateHeatMap(self.targetPos)', globals(), locals(), sort='tottime')
        self.GenerateVectorField()
        #cProfile.runctx('self.GenerateVectorField()', globals(), locals(), sort='tottime')

    def GetDirection(self, rect):
        startPos = self.GetRectCellPos(rect)
        vector = self.localPathMap[startPos][self.vectorI]
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
            if self.CheckExist(pos):
                #print("herfhefe")
                neighbours.append(pos)
        return neighbours
    
    def GetHorzVertDist(self, sourcePos, sourceDist):
        # Same as get neighbours but only 
        # horizontal and vertical neighbours
        northNPos = (sourcePos[0], sourcePos[1] - 1)
        westNPos = (sourcePos[0] + 1, sourcePos[1])
        southNPos = (sourcePos[0], sourcePos[1] + 1)
        eastNPos = (sourcePos[0] - 1, sourcePos[1])
        neighboursPos = [northNPos, southNPos, eastNPos, westNPos]
        neighboursDist = []
        dist = 0
        for pos in neighboursPos:
            # Checks if the position exists
            if not self.CheckExist(pos) or self.localPathMap[pos][self.obstacleI]:
                neighboursDist.append(sourceDist)
            else:
                dist = self.localPathMap[pos][self.distToTargetI]
                neighboursDist.append(dist)
        return neighboursDist

    def GenerateHeatMap(self, endPos):
        openList = [endPos]
        currentPos = endPos
        neighbourNodes = self.GetNeighbours(endPos)
        #print("endpos dist:", self.FindCellInfo(endPos, "distToTarget"))
        oldArray = self.localPathMap[endPos]
        self.localPathMap[endPos] = (oldArray[0], oldArray[1], oldArray[2], True, oldArray[4])
        while len(openList) > 0: 
            #print("current pos:", currentPos, "| len open list:", len(openList))
            currentPosDist = self.localPathMap[currentPos][self.distToTargetI]
            for pos in neighbourNodes:
                if not self.localPathMap[pos][self.obstacleI]:
                    distToCurrent = self.GetDist(currentPos, pos)
                    #print("currentpos:", currentPos, "| pos:", pos, "| get dist:", distToCurrent)
                    distFromTarget = currentPosDist + distToCurrent
                    #if distToCurrent == 14 and self.localPathMap[pos][self.nextToWallI] and self.localPathMap[currentPos][self.nextToWallI]:
                    #    distFromTarget += 10000
                    if self.localPathMap[pos][self.visitedI]:
                        if distFromTarget < self.localPathMap[pos][self.distToTargetI]:
                            oldArray = self.localPathMap[endPos]
                            self.localPathMap[pos] = (distFromTarget, oldArray[1], oldArray[2], oldArray[3], oldArray[4])
                    else:
                        oldArray = self.localPathMap[endPos]
                        self.localPathMap[pos] = (distFromTarget, oldArray[1], oldArray[2], True, oldArray[4])
                        openList.append(pos)
            openList.remove(currentPos)
            if len(openList) > 0:
                currentPos = openList[0]
                neighbourNodes = self.GetNeighbours(currentPos)
    
    def GenerateVectorField(self):
        for pos in self.posList:
            if not self.localPathMap[pos][self.obstacleI]:
                #print("pos:", pos)
                posDistToTarget = self.localPathMap[pos][self.distToTargetI]
                upDist, downDist, rightDist, leftDist = self.GetHorzVertDist(pos, posDistToTarget)
                #print("left:", self.FindCellInfo(leftPos, "distToTarget"))
                #print("right:", self.FindCellInfo(rightPos, "distToTarget"))
                # leftDist = 0
                # rightDist = 0
                # upDist = 0
                # downDist = 0
                newVectorX = rightDist - leftDist
                newVectorY = upDist - downDist

                # if rightPos == False and leftPos != False:
                #     newVectorX = posDistToTarget - leftDist
                # elif leftPos == False and rightPos != False:
                #     newVectorX = rightDist - posDistToTarget
                # elif leftPos == False and rightPos == False:
                #     newVectorX = 0
                # else:
                #     newVectorX = rightDist - leftDist

                # if upPos == False and downPos != False:
                #     newVectorY = posDistToTarget - downDist
                # elif downPos == False and upPos != False:
                #     newVectorY = upDist - posDistToTarget
                # elif downPos == False and upPos == False:
                #     newVectorY = 0
                # else:
                #     newVectorY = upDist - downDist

                #print("new vector:", (newVectorX, newVectorY))

                newVector = pygame.math.Vector2(newVectorX, newVectorY)
                if newVectorX != 0 or newVectorY != 0:
                    newVector = newVector.normalize()
                oldArray = self.localPathMap[pos]
                self.localPathMap[pos] = (oldArray[0], oldArray[1], oldArray[2], oldArray[3], newVector)

    def CreateLocalPathMap(self):
        self.localPathMap = {} # dictionary structure works like so: cell position --> dist to target, if next to wall, if has obstacle, if visited, vector
        self.posList = []
        # Variables containing indexes of where information is located in the array for easier referencing
        self.distToTargetI = 0
        self.nextToWallI = 1
        self.obstacleI = 2
        self.visitedI = 3
        self.vectorI = 4
        self.localPathSize = 0
        for sprite in self.pathSprites:
            self.localPathMap[sprite.pos] = (sprite.distToTarget, sprite.nextToWall, sprite.hasObstacle, sprite.visited, sprite.vector)
            self.posList.append(sprite.pos)
            self.localPathSize += 1
        self.FixEdges()
    
    # def FixEdges(self):
    #     for position in self.posList:
    #         if self.localPathMap[position][self.obstacleI]:
    #             horizontalNPos = [(position[0] + 1, position[1]), (position[0], position[1] + 1), (position[0] - 1, position[1]), (position[0], position[1] - 1)]
    #             for pos in horizontalNPos:
    #                 if position in list(self.localPathMap.keys()):
    #                     oldArray = self.localPathMap[position]
    #                     self.localPathMap[position] = (oldArray[0], True, oldArray[2], oldArray[3], oldArray[4])
    #                     cellObject = self.GetCell(pos)
    #                     if type(cellObject) != str:
    #                         if not cellObject.hasObstacle:
    #                             cellObject.changeColour(purple)

    def FixEdges(self):
        for cellPos in self.posList:
            if self.localPathMap[cellPos][self.obstacleI]:
                up = (cellPos[0], cellPos[1] - 1)
                upRight = (cellPos[0] - 1, cellPos[1] - 1)
                right = (cellPos[0] - 1, cellPos[1])
                downRight = (cellPos[0] - 1, cellPos[1] + 1)
                down = (cellPos[0], cellPos[1] + 1)
                downLeft = (cellPos[0] + 1, cellPos[1] + 1)
                left = (cellPos[0] + 1, cellPos[1])
                upLeft = (cellPos[0] + 1, cellPos[1] - 1)

                if self.CheckExist(up):
                    if not self.localPathMap[up][self.obstacleI]:
                        if self.CheckExist(right):
                            if not self.localPathMap[right][self.obstacleI]:
                                self.SetCellInfo(upRight, "nextToWall", True)
                                self.SetColour(upRight, purple)
                        if self.CheckExist(left):
                            if not self.localPathMap[left][self.obstacleI]:
                                self.SetCellInfo(upLeft, "nextToWall", True)
                                self.SetColour(upLeft, purple)

                if self.CheckExist(down):
                    if not self.localPathMap[down][self.obstacleI]:
                        if self.CheckExist(right):
                            if not self.localPathMap[right][self.obstacleI]:
                                self.SetCellInfo(downRight, "nextToWall", True)
                                self.SetColour(downRight, purple)
                        if self.CheckExist(left):
                            if not self.localPathMap[left][self.obstacleI]:
                                self.SetCellInfo(downLeft, "nextToWall", True)
                                self.SetColour(downLeft, purple)

    def SetCellInfo(self, pos, wantToChange, change):
        # Sets the cell information if it exists
        if self.CheckExist(pos):
            array = list(self.localPathMap[pos])
            array[self.wantedDict[wantToChange]] = change
            self.localPathMap[pos] = tuple(array)
        else:
            return False
    
    def SetColour(self, pos, colour):
        # Colour must be in RGB list from, i.e. (R, G, B)
        if self.CheckExist(pos):
            cell = self.GetCell(pos)
            cell.changeColour(colour)
    
    def GetDist(self, startPos, targetPos):
        changeY = abs(startPos[1] - targetPos[1]) 
        changeX = abs(startPos[0] - targetPos[0])
        if changeX > changeY:
            dist = 20*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 20*(changeX) + 10*(abs(changeY - changeX))
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
        y = pos[1]
        x = pos[0]
        #print("|Calculation:", (y-1)*self.horizontalCount + x-1,"| horizontal count", self.horizontalCount, "| vertical:", self.verticalCount, "|pos wanted:", pos)
        #print("len:", len(self.localPathMap))
        calculatedIndex = (y-1)*self.horizontalCount + x-1
        #print("index:", calculatedIndex, "| len:", len(self.localPathMap))
        if calculatedIndex >= len(self.localPathMap):
            return False
        elif wanted == 'exists':
            return True
        cell = self.localPathMap[calculatedIndex]
        return cell[1][self.wantedDict[wanted]]

    def CheckExist(self, pos):
        """calculatedIndex = (pos[1]-1)*self.horizontalCount + pos[0]-1
        if calculatedIndex >= len(self.localPathMap):
            return False
        elif self.posList[calculatedIndex] == pos:
            return True
        else:
            return False"""
        if pos in posLookUp:
            return True
        else:
            return False
                
    # def SetCellInfo(self, pos, wanted, change):
    #     # Changes cell information from local path map
    #     if pos == -1 or type(pos) == str:
    #         print("ERROR: bad pos")
    #         return "no pos"
    #     cell = self.localPathMap[(pos[1]-1)*self.horizontalCount + pos[0]-1]
    #     if cell[0] == pos:
    #         cell[1][self.wantedDict[wanted]] = change
    
    def CleanPath(self):
        # Wipes information from the local path map for the next pathfind
        for pos in self.posList:
            oldArray = self.localPathMap[pos]
            self.localPathMap[pos] = (0, oldArray[1], oldArray[2], False, oldArray[4]) # Sets dist to 0, sets 'has visited' to False
    
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
            vector = self.localPathMap[pos][self.vectorI]
            pygame.draw.line(screen, 'green', (cellX, cellY), (cellX + vector.x * 7, cellY + vector.y* 7))
            pygame.draw.circle(screen, 'red', (cellX, cellY), 1)
    
    def DrawHeatMap(self, screen, camera):
        font = pygame.font.SysFont("cambria", 10)
        for pos in self.posList:
            if pos == self.targetPos:
                colour = "red"
                #print("end dist:", self.FindCellInfo(pos, "distToTarget"))
            else:
                colour = "white"
            textInput = str(self.localPathMap[pos][self.distToTargetI])
            text = font.render(textInput, True, colour)
            node = self.GetCell(pos)
            nodeX = (node.rect.centerx - camera.offset.x) * camera.zoomLevel
            nodeY = (node.rect.centery - camera.offset.y) * camera.zoomLevel
            textRect = text.get_rect(center=(nodeX, nodeY))
            screen.blit(text, textRect)
        
def CreateObstacleMap(blockCount, blockWidth, obstacles, pathSpritesGroup, top, firstWallIndex):
    # Needs to be used before pathfinding method
    # Block count needs to be array in form (horizontalCount, verticalCount)
    global vertCount
    global horzCount
    verticalCount = blockCount[1]
    horizontalCount = blockCount[0]
    vertCount = blockCount[1]
    horzCount = blockCount[0]
    top = top
    y = 0
    count = 0
    for row in range(verticalCount):
        y += 1
        x = 0
        for column in range(0, horizontalCount):
            x += 1
            block = PathfindingBlock.Block(column * (blockWidth) + firstWallIndex*blockWidth, top, blockWidth, white)
            block.pos = (x,y)
            pathSpritesGroup.add(block)
            posLookUp[(x,y)] = count
            count += 1
        top += blockWidth

    for block in pathSpritesGroup:
        blockCollide = pygame.sprite.spritecollide(block, obstacles, False)
        if len(blockCollide) > 0:
            block.changeColour(red)
            block.hasObstacle = True