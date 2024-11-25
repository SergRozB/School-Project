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
        self.targetPos = 0
        for cell in self.pathSprites:
            self.pathRectList.append(cell.rect)

    def CreateMap(self):
        self.CleanPath()
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
    
    def GetHorzVertNeighbours(self, sourcePos):
        # Same as get neighbours but only 
        # horizontal and vertical neighbours
        northNPos = (sourcePos[0], sourcePos[1] - 1)
        westNPos = (sourcePos[0] + 1, sourcePos[1])
        southNPos = (sourcePos[0], sourcePos[1] + 1)
        eastNPos = (sourcePos[0] - 1, sourcePos[1])
        neighboursPos = [northNPos, southNPos, eastNPos, westNPos]
        neighbours = []
        for pos in neighboursPos:
            # Checks if the position exists
            if not self.FindCellInfo(pos, 'exists') or self.FindCellInfo(pos, 'hasObstacle'):
                pos = False
            neighbours.append(pos)
        return neighbours

    def GenerateHeatMap(self, endPos):
        openList = [endPos]
        currentPos = endPos
        neighbourNodes = self.GetNeighbours(endPos)
        #print("endpos dist:", self.FindCellInfo(endPos, "distToTarget"))
        self.SetCellInfo(endPos, "visited", True)
        while len(openList) > 0: 
            #print("current pos:", currentPos, "| len open list:", len(openList))
            currentPosDist = self.FindCellInfo(currentPos, "distToTarget")
            for pos in neighbourNodes:
                if not self.FindCellInfo(pos, "hasObstacle"):
                    distToCurrent = self.GetDist(currentPos, pos)
                    #print("currentpos:", currentPos, "| pos:", pos, "| get dist:", distToCurrent)
                    distFromTarget = currentPosDist + distToCurrent
                    #if distToCurrent == 14 and self.FindCellInfo(pos, "nextToWall") and self.FindCellInfo(currentPos, "nextToWall"):
                        #distFromTarget += 1000
                    if self.FindCellInfo(pos, "visited"):
                        if distFromTarget < self.FindCellInfo(pos, "distToTarget"):
                            self.SetCellInfo(pos, "distToTarget", distFromTarget)
                    else:
                        self.SetCellInfo(pos, "distToTarget", distFromTarget)
                        self.SetCellInfo(pos, "visited", True)
                        openList.append(pos)
            openList.remove(currentPos)
            if len(openList) > 0:
                currentPos = openList[0]
                neighbourNodes = self.GetNeighbours(currentPos)
    
    def GenerateVectorField(self):
        for pos in self.posList:
            if not self.FindCellInfo(pos, 'hasObstacle'):
                #print("pos:", pos)
                horzVertNeighbours = self.GetHorzVertNeighbours(pos)
                upPos, downPos, rightPos, leftPos = horzVertNeighbours
                #print("left:", self.FindCellInfo(leftPos, "distToTarget"))
                #print("right:", self.FindCellInfo(rightPos, "distToTarget"))
                posDistToTarget = self.FindCellInfo(pos, "distToTarget")
                leftDist = 0
                rightDist = 0
                upDist = 0
                downDist = 0
                if leftPos != False:
                    leftDist = self.FindCellInfo(leftPos, "distToTarget")
                if rightPos != False:
                    rightDist = self.FindCellInfo(rightPos, "distToTarget")
                if upPos != False:
                    upDist = self.FindCellInfo(upPos, "distToTarget")
                if downPos != False:
                    downDist = self.FindCellInfo(downPos, "distToTarget")

                if rightPos == False and leftPos != False:
                    newVectorX = posDistToTarget - leftDist
                elif leftPos == False and rightPos != False:
                    newVectorX = rightDist - posDistToTarget
                elif leftPos == False and rightPos == False:
                    newVectorX = 0
                else:
                    newVectorX = rightDist - leftDist

                if upPos == False and downPos != False:
                    newVectorY = posDistToTarget - downDist
                elif downPos == False and upPos != False:
                    newVectorY = upDist - posDistToTarget
                elif downPos == False and upPos == False:
                    newVectorY = 0
                else:
                    newVectorY = upDist - downDist
                #print("new vector:", (newVectorX, newVectorY))
                newVector = pygame.math.Vector2(newVectorX, newVectorY)
                if newVectorX != 0 or newVectorY != 0:
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
            elif wanted == 'nextToWall':
                return cell[1][1]
            elif wanted == 'hasObstacle':
                return cell[1][2]
            elif wanted == 'visited':
                return cell[1][3]
            elif wanted == 'vector':
                return cell[1][4]
            elif wanted == 'exists':
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
            item[1][0] = 0 # Sets dist to 0
            item[1][3] = False # Sets 'has visited' to False
    
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
            textInput = str(self.FindCellInfo(pos, "distToTarget"))
            text = font.render(textInput, True, colour)
            node = self.GetCell(pos)
            nodeX = (node.rect.centerx - camera.offset.x) * camera.zoomLevel
            nodeY = (node.rect.centery - camera.offset.y) * camera.zoomLevel
            textRect = text.get_rect(center=(nodeX, nodeY))
            screen.blit(text, textRect)
        
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