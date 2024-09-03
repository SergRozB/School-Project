import pygame
import math
import random

pygame.init()

pygame.display.set_caption("Zombie Test")

screenW = 800
screenH = 600

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
screen = pygame.display.set_mode([screenW, screenH])
clock = pygame.time.Clock()

timeInterval = 1000 # Time interval for when to pathfind in miliseconds
canPathfind = False
allowPathfinding = pygame.USEREVENT+1 # Custom time event for controlling when pathfinding occurs

blockWidth = 20

class Player(pygame.sprite.Sprite):
    # Constructor. 
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.pos = pygame.math.Vector2(100, 100)
        self.prevPos = self.pos
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 2
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("C:\Python School Stuff\School Game\Code\SpriteImages\TestSquare.png").convert_alpha(), 0, 1)
        self.basePlayerImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
 
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()     

    def CheckControls(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0
    
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1*self.speed

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1*self.speed

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1*self.speed
 
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1*self.speed

        if self.direction.x != 0 and self.direction.y != 0:
            self.direction.x /= math.sqrt(self.speed)
            self.direction.y /= math.sqrt(self.speed)
        

    def RotateToMouse(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        Mx, My = pygame.mouse.get_pos()
        xDist = Mx - x
        yDist = My - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        self.image = pygame.transform.rotate(self.basePlayerImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)

    def Move(self):
        self.pos.x += self.direction.x * self.speed
        self.hitboxRect.x = round(self.pos.x)
        self.CheckCollision('horizontal')

        self.pos.y += self.direction.y * self.speed
        self.hitboxRect.y = round(self.pos.y)
        self.CheckCollision('vertical')

        self.rect.center = self.hitboxRect.center
        
    def Update(self):
        """ Update the position of the player """

        self.CheckControls()
        self.Move()
        self.RotateToMouse()
        self.oldRect = self.hitboxRect.copy()
    
    def GetVelocity(self):
        return [self.direction.x, self.direction.y]
    
    def CreateLocalSprites(self, sprites):
        self.localSprites = pygame.sprite.Group()
        for sprite in sprites:
            if sprite.hitboxRect != self.hitboxRect:
                self.localSprites.add(sprite)
    
    def CheckCollision(self, direction):
        collisionSprites = pygame.sprite.spritecollide(self, self.localSprites, False)
        for sprite in collisionSprites:
            if direction == 'horizontal':
                # If collision on the right
                if self.hitboxRect.right >= sprite.hitboxRect.left and self.oldRect.right <= sprite.oldRect.left:
                    self.hitboxRect.right = sprite.hitboxRect.left
                    self.pos.x = self.hitboxRect.x
                
                # If collision on the left
                if self.hitboxRect.left <= sprite.hitboxRect.right and self.oldRect.left >= sprite.oldRect.right:
                    self.hitboxRect.left = sprite.hitboxRect.right
                    self.pos.x = self.hitboxRect.x

            if direction == 'vertical':
                # If collision on the top
                if self.hitboxRect.bottom >= sprite.hitboxRect.top and self.oldRect.bottom <= sprite.oldRect.top:
                    self.hitboxRect.bottom = sprite.hitboxRect.top
                    self.pos.y = self.hitboxRect.y
                
                # If collision on the bottom
                if self.hitboxRect.top <= sprite.hitboxRect.bottom and self.oldRect.top >= sprite.oldRect.bottom:
                    self.hitboxRect.top = sprite.hitboxRect.bottom
                    self.pos.y = self.hitboxRect.y

    def Test(self):
        print("test") 

class Enemy(Player):
    # Constructor. 
    def __init__(self, x, y):
        # Call the parent class (Player) constructor
        super().__init__()

        self.pos = pygame.math.Vector2(x, y)
        self.direction = pygame.math.Vector2(0, 0)
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("C:\Python School Stuff\School Game\Code\SpriteImages\goomba.png").convert_alpha(), 0, 0.25)
        self.baseEnemyImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseEnemyImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
 
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        # Velocity
        self.speed = 1

        self.target = player

        self.path = []

    def RotateToTarget(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        Tx, Ty = self.target.pos
        xDist = Tx - x
        yDist = Ty - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        velX = self.speed * math.cos(math.radians(self.angle))
        velY = self.speed * math.sin(math.radians(self.angle))
        self.direction = pygame.math.Vector2(velX, velY)
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        
    def Update(self):
        """ Update the position of the enemy """
        print("target:", self.target, "|pos:", self.target.pos)
        if canPathfind:
            self.Pathfind()
        if len(self.path) > 0:
            self.FollowPath()
        self.RotateToTarget()
        self.Move()
        self.oldRect = self.hitboxRect.copy()
    
    def GetNeighbours(self, sourcePos, endPos, processedList, cellsToSearch):
        # GET NEIGHBOURS APPEARS FINISHED #
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
        for block in pathSprites:

            if self.FindCellInfo(block.pos, 'isTarget') and block.pos in neighboursPos: # Checks if the target cell is a neighbour
                if self.CheckIfDiagonal(block.pos, sourcePos) == False: # Checks if the target cell is at a diagonal distance from the source 
                    self.SetCellInfo(block.pos, 'parent', sourcePos)
                    return -1 # Returns -1, signifying that the target cell was found
            
            elif block.pos in neighboursPos and not self.FindCellInfo(block.pos, 'hasObstacle') and block.pos not in processedList:
                costToN = self.FindCellInfo(block.pos, 'g') + GetDist(sourcePos, block.pos) # The g cost from the source cell
                
                if self.CheckIfDiagonal(block.pos, sourcePos) and self.FindCellInfo(block.pos, 'nextToWall') == True:
                    costToN += 1000

                if block.pos not in cellsToSearch or costToN < self.FindCellInfo(block.pos, 'g'):
                    self.SetCellInfo(block.pos, 'g', costToN)
                    self.SetCellInfo(block.pos, 'parent', sourcePos)

                    if block.pos not in cellsToSearch:
                        self.SetCellInfo(block.pos, 'h', GetDist(block.pos, endPos))
                        cellsToSearch.append(block.pos) 
                neighbours.append(block.pos)
        return neighbours
    
    def CheckIfDiagonal(self, pos, sourcePos):
        # Checks if a block is diagonal to the player
        diagonalPos = [(pos[0] + 1, pos[1] + 1), (pos[0] - 1, pos[1] + 1), (pos[0] - 1, pos[1] - 1), (pos[0] + 1, pos[1] - 1)]
        for pos in diagonalPos:
            if pos == sourcePos:
                return True
        return False

    def Pathfind(self):
        endCellPos = self.GetRectCellPos(player.hitboxRect)
        startCellPos = self.GetRectCellPos(self.hitboxRect)
        self.SetCellInfo(endCellPos, 'isTarget', True)
        hasCompleted = False
        cellsToSearch = [startCellPos]
        processedCells = []
        neighbours = []
        while not hasCompleted:
            # Get best cell cost
            bestCellPos = cellsToSearch[0]
            for cellPos in cellsToSearch:
                if (self.FindCellInfo(cellPos, 'f') < self.FindCellInfo(bestCellPos, 'f') or (self.FindCellInfo(cellPos, 'f')
                 == self.FindCellInfo(bestCellPos, 'f') and self.FindCellInfo(cellPos, 'h') < self.FindCellInfo(bestCellPos, 'h'))):
                    bestCellPos = cellPos
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
                hasCompleted == True
                print("CANT COMPLETE PATH, ALL PROCESSED")
                return -1
    
    def CompilePath(self, startPos, endPos):
        # Follows the connected cells from start to end 
        # Creates a list of cells to go to
        self.path = [self.GetCell(endPos)]
        cellPos = endPos
        while cellPos != startPos:
            if self.FindCellInfo(cellPos, 'g') >= 1000:
                # If g cost bigger than 1000, must've done an illegal path
                print("CANT COMPLETE PATH, ILLEGAL PATH")
            cellPos = self.FindCellInfo(cellPos, 'parent') # Gets cell object of parent cell
            if cellPos != -1:
                cellObject = self.GetCell(cellPos)
                self.path.append(cellObject)
                showPathSprites.add(cellObject)
        self.CleanPath()
            
        # Reverses order of list since we follow it from end to start
        # in this code, but the enemy needs to follow it from start to end
        self.path.reverse()
    
    def FollowPath(self):
        # Removes a cell from the path list if collided with
        self.target = self.path[0]
        if self.hitboxRect.colliderect(self.path[0].rect):
            self.path.remove(self.path[0]) 
            self.target = self.path[0]   

    def GetCell(self, pos):
        for cell in pathSprites:
            if pos == cell.pos:
                return cell
        return 'no cell found'
    
    def CreateLocalPathMap(self):
        self.localPathMap = [] # 2D list structure works like so: cell position --> g cost, h cost, parent cell, if it's next to a wall, if it has an obstacle, if it's the target
        for sprite in pathSprites:
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
                else:
                    item[1][i] = False
    
    def FixEdges(self):
        positionList = []
        for i in self.localPathMap:
            position = i[0]
            positionList.append(position)
            if self.FindCellInfo(position, 'hasObstacle'):
                horizontalNPos = [(position[0] + 1, position[1]), (position[0], position[1] + 1), (position[0] - 1, position[1]), (position[0], position[1] - 1)]
                for pos in horizontalNPos:
                    if pos in positionList:
                        self.SetCellInfo(pos, 'nextToWall', True)
    
    def FindCellInfo(self, pos, wanted):
        # Finds cell information from local path map 
        for cell in self.localPathMap:
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
        return 'not found' 
                
    def SetCellInfo(self, pos, wanted, change):
        # Changes cell information from local path map 
        for cell in self.localPathMap:
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
    
    def GetRectCellPos(self, rect):
        # Gets the position of a cell colliding with the given rect
        for cell in pathSprites:
            if cell.rect.colliderect(rect):
                return cell.pos

class Obstacle(pygame.sprite.Sprite):
    # Obstacle sprite, can't move
    def __init__(self, width, height, x, y):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.pos = pygame.math.Vector2(x, y)

        self.width = width
        self.height = height

        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.hitboxRect = self.image.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

class Block(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        super().__init__()

        self.image = pygame.Surface([blockWidth, blockWidth])
        self.image.fill(white)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.pos = (0,0)
        self.g = 0
        self.h = 0

        self.connectedCell = -1 # -1 means no connected cell is assigned
        self.nextToWall = False
        self.hasObstacle = False
        self.isTarget = False
    
    def GetDist(self, targetPos):
        changeY = abs(self.pos[1] - targetPos[1]) 
        changeX = abs(self.pos[0] - targetPos[0])
        if changeX > changeY:
            dist = 14*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 14*(changeX) + 10*(abs(changeY - changeX))
        return dist
    
    def GetFCost(self):
        return self.g + self.h
    
    def changeColour(self, colour):
        self.image.fill(colour)

def GetDist(startPos, targetPos):
        changeY = abs(startPos[1] - targetPos[1]) 
        changeX = abs(startPos[0] - targetPos[0])
        if changeX > changeY:
            dist = 14*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 14*(changeX) + 10*(abs(changeY - changeX))
        return dist

def CreateObstacleMap():
    top = 0
    horizontalCount = math.ceil(screenW/blockWidth)
    verticalCount = math.ceil(screenH/blockWidth)
    y = 0
    for row in range(verticalCount):
        y += 1
        x = 0
        for column in range(0, horizontalCount):
            x += 1
            block = Block(column * (blockWidth), top)
            block.pos = (x,y)
            pathSprites.add(block)
        top += blockWidth
    
    for block in pathSprites:
        blockCollide = pygame.sprite.spritecollide(block, obstacles, False)
        if len(blockCollide) > 0:
            block.changeColour(red)
            block.hasObstacle = True

allSprites = pygame.sprite.Group() # Group of all Sprites. Must have a hitbox rect called 'hitboxRect'
liveSprites = pygame.sprite.Group() # Group of all 'living' sprites that need updating
obstacles = pygame.sprite.Group() # Group of all immobile sprites. Checked when pathfinding to note down obstacles. 
                                  # This group is needed as only non-moving sprites are recorded.
pathSprites = pygame.sprite.Group() # Group of sprites representing pathfinding script.
showPathSprites = pygame.sprite.Group()

player = Player()
obstacle = Obstacle(20, 20, 300, 300)

allSprites.add(player)
allSprites.add(obstacle)
liveSprites.add(player)
obstacles.add(obstacle)

CreateObstacleMap()

for _ in range(1):
    enemy = Enemy(random.randint(1, screenW), random.randint(1, screenH))
    allSprites.add(enemy)
    liveSprites.add(enemy)

for sprite in liveSprites:
    sprite.CreateLocalSprites(allSprites)
    if sprite != player:
        sprite.CreateLocalPathMap()

background = pygame.Surface(screen.get_size())

run = True

pygame.time.set_timer(allowPathfinding, timeInterval)

while run:
    screen.fill(black)
    canPathfind = False

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == allowPathfinding:
            canPathfind = True
            showPathSprites.empty()
    
    for sprite in liveSprites:
        sprite.Update()
        pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
    
    for sprite in allSprites:
        screen.blit(sprite.image, sprite.rect)
        pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)

    for sprite in showPathSprites:
            screen.blit(sprite.image, sprite.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
