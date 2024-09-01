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

        self.speed = 1
        # Velocity

    def RotateToPlayer(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        Px, Py = player.pos
        xDist = Px - x
        yDist = Py - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        velX = self.speed * math.cos(math.radians(self.angle))
        velY = self.speed * math.sin(math.radians(self.angle))
        self.direction = pygame.math.Vector2(velX, velY)
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        
    def Update(self):
        """ Update the position of the enemy """
        self.Move()
        self.RotateToPlayer()
        self.oldRect = self.hitboxRect.copy()
    
    def GetNeighbours(self, sourcePos, endPos, processedList, cellsToSearch):
        # STILL NEEDS WORK #
        # Takes the position of the source cell, and its g cost.
        # Gets the neighbour objects of the said cell and returns them.
        # Also returns a list containing -1 if the target is the neighbour. 
        # In the above case, the returned list also contains the target cell.
        northNPos = [sourcePos[0], sourcePos[1] - 1]
        northWestNPos = [sourcePos[0] + 1, sourcePos[1] - 1]
        westNPos = [sourcePos[0] + 1, sourcePos[1]]
        southWesthNPos = [sourcePos[0] + 1, sourcePos[1] + 1]
        southNPos = [sourcePos[0], sourcePos[1] + 1]
        southEastNPos = [sourcePos[0] - 1, sourcePos[1] + 1]
        eastNPos = [sourcePos[0] - 1, sourcePos[1]]
        northEastNPos = [sourcePos[0] - 1, sourcePos[1] - 1]
        neighboursPos = [northNPos, northWestNPos, westNPos, southWesthNPos, southNPos, southEastNPos, eastNPos, northEastNPos]
        neighbours = []
        for block in pathSprites:
            #print("neighbours pos:", neighboursPos)
            #print("block pos", block.pos)

            if self.localPathMap[block.pos][5] and block.pos in neighboursPos: # Checks if the target cell is a neighbour
                if self.CheckIfDiagonal(block.pos, sourcePos) == False: # Checks if the target cell is at a diagonal distance from the source 
                    block.connectedCell = sourcePos
                    return -1 # Returns -1, signifying that the target cell was found
            
            elif block.pos in neighboursPos and not block.hasObstacle and block not in processedList:
                costToN = sourcePos.g + sourcePos.GetDist(block.pos) # The g cost from the source cell
                
                if self.CheckIfDiagonal(block.pos, sourcePos) and self.localPathMap[block.pos][3] == True:
                    costToN += 1000

                if block not in cellsToSearch or costToN < block.g:
                    block.g = costToN
                    block.connectedCell = sourcePos

                    if block not in cellsToSearch:
                        block.h = block.GetDist(endPos)
                        cellsToSearch.append(block) 
                neighbours.append(block)
        return neighbours
    
    def CheckIfDiagonal(self, pos, sourcePos):
        # Checks if a block is diagonal to the player
        diagonalPos = [[pos[0] + 1, pos[1] + 1], [pos[0] - 1, pos[1] + 1], [pos[0] - 1, pos[1] - 1], [pos[0] + 1, pos[1] - 1]]
        for pos in diagonalPos:
            if pos == sourcePos:
                return True
        return False

    def Pathfind(self):
        pass
    
    def CreateLocalPathMap(self):
        self.localPathMap = {} # Dict structure works like so: cell position --> g cost, h cost, parent cell, if its next to a wall, if it has an obstacle, if its the target
        for sprite in pathSprites:
            self.localPathMap[sprite.pos] = (sprite.g, sprite.h, sprite.connectedCell, sprite.nextToWall, sprite.hasObstacle, sprite.isTarget)

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

        self.connectedCell = None
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

player = Player()
obstacle = Obstacle(20, 20, 300, 300)

allSprites.add(player)
allSprites.add(obstacle)
liveSprites.add(player)
obstacles.add(obstacle)

CreateObstacleMap()

for _ in range(5):
    enemy = Enemy(random.randint(1, screenW), random.randint(1, screenH))
    allSprites.add(enemy)
    liveSprites.add(enemy)
    print(enemy.pos)

for sprite in liveSprites:
    sprite.CreateLocalSprites(allSprites)
    if sprite != player:
        sprite.CreateLocalPathMap()

background = pygame.Surface(screen.get_size())

run = True

while run:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    for sprite in liveSprites:
        sprite.Update()
        pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
    
    for sprite in allSprites:
        screen.blit(sprite.image, sprite.rect)
        pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)

    for sprite in pathSprites:
        if sprite.hasObstacle:
            screen.blit(sprite.image, sprite.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
