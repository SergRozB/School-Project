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
        targetCell = self.GetCell(self.GetRectCellPos(self.targetRect))
        if targetCell:
            self.GenerateHeatMap(targetCell)
            self.GenerateVectorField()
        else:
            print("ERROR: NO NODE DETECTED - CREATE MAP FUNC")

    def GetDirection(self, rect):
        # Returns direction vector of node rect is colliding with
        startPos = self.GetRectCellPos(rect)
        node = self.GetCell(startPos)
        if node:
            return node.vector
        else:
            print("ERROR: NO NODE ON RECT")

    def GetNeighbours(self, sourceNode):
        # Takes the position of the source cell
        # Gets the neighbour objects of the said cell and returns them. 
        # In the above case, the returned list also contains the target cell.
        #print("source node:", sourceNode)
        sourcePos = sourceNode.pos
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
            node = self.GetCell(pos)
            if node:
                neighbours.append(node)
        return neighbours
    
    def GetHorzVertNeighbours(self, sourceNode):
        # Same as get neighbours but only 
        # horizontal and vertical neighbours
        sourcePos = sourceNode.pos
        northNPos = (sourcePos[0], sourcePos[1] - 1)
        westNPos = (sourcePos[0] + 1, sourcePos[1])
        southNPos = (sourcePos[0], sourcePos[1] + 1)
        eastNPos = (sourcePos[0] - 1, sourcePos[1])
        neighboursPos = [northNPos, southNPos, eastNPos, westNPos]
        neighbours = []
        for pos in neighboursPos:
            # Adds position regardless if it exists. 
            # Stored as 'False' in list if doesn't exist.
            neighbours.append(self.GetCell(pos))
        return neighbours

    def GenerateHeatMap(self, endNode):
        openList = [endNode]
        currentNode = endNode
        neighbourNodes = self.GetNeighbours(endNode)
        while len(openList) > 0: 
            for node in neighbourNodes:
                if not node.hasObstacle and node not in openList:
                    distFromTarget = self.GetDist(currentNode.pos, endNode.pos) + self.GetDist(node.pos, currentNode.pos)
                    if node.visited:
                        if distFromTarget < node.distToTarget:
                            node.distToTarget = distFromTarget
                    else:
                        node.distToTarget = distFromTarget
                        node.visited = True
                        openList.append(node)
            openList.remove(currentNode)
            if len(openList) > 0:
                currentNode = openList[0]
                neighbourNodes = self.GetNeighbours(currentNode)
    
    def GenerateVectorField(self):
        count = 0
        for node in self.pathSprites.sprites():
            count += 1
            #print("count:", count, "| len:", len(self.pathSprites.sprites()), "|horz vert:",(self.horizontalCount, self.verticalCount))
            #print("pos:", pos)
            horzVertNeighbours = self.GetHorzVertNeighbours(node)
            upNode, downNode, rightNode, leftNode = horzVertNeighbours
            #print("left:", self.FindCellInfo(leftPos, "distToTarget"))
            #print("right:", self.FindCellInfo(rightPos, "distToTarget"))
            if leftNode == False or rightNode == False:
                newVectorX = node.distToTarget
            else:
                newVectorX = leftNode.distToTarget - rightNode.distToTarget
            if upNode == False or downNode == False:
                newVectorY = node.distToTarget
            else:
                newVectorY = upNode.distToTarget - downNode.distToTarget
            #print("new vector:", (newVectorX, newVectorY))
            if pygame.math.Vector2(newVectorX, newVectorY).magnitude() != 0:
                node.vector = pygame.math.Vector2(newVectorX, newVectorY).normalize()
            else:
                node.vector = pygame.math.Vector2(newVectorX, newVectorY)
    
    def FixEdges(self):
        for node in self.pathSprites.sprites():
            if node.hasObstacle:
                position = node.pos
                horizontalNPos = [(position[0] + 1, position[1]), (position[0], position[1] + 1), (position[0] - 1, position[1]), (position[0], position[1] - 1)]
                for pos in horizontalNPos:
                    neighbourNode = self.GetCell(pos)
                    if neighbourNode:
                        neighbourNode.nextToWall = True
                        if not neighbourNode.hasObstacle:
                            neighbourNode.changeColour(purple)
    
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
    
    def CleanPath(self):
        # Wipes information from the local path map for the next pathfind
        for node in self.pathSprites.sprites():
            node.visited = False
    
    def GetCell(self, pos):
        # Returns the cell object from a position
        x = pos[0]
        y = pos[1]
        calculatedIndex = (y-1)*self.horizontalCount + x-1
        if calculatedIndex < len(self.pathSprites):
            return self.pathSprites.sprites()[calculatedIndex]
        else:
            return False
    
    def DrawVectors(self, screen, camera):
        for node in self.pathSprites:
            nodePosX = (node.rect.centerx - camera.offset.x) * camera.zoomLevel
            nodePosY = (node.rect.centery - camera.offset.y) * camera.zoomLevel
            pygame.draw.line(screen, 'green', (nodePosX, nodePosY), (nodePosX + node.vector.x * 10 , nodePosY + node.vector.y* 10))
        
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
