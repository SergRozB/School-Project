import pygame
import math
import random
import MapMaker
import Pathfinding

pygame.init()

pygame.display.set_caption("Zombie Test")

screenW = 800
screenH = 600

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
screen = pygame.display.set_mode([screenW, screenH])
clock = pygame.time.Clock()

timeInterval = 500 # Time interval for when to pathfind in miliseconds
canPathfind = False
allowPathfinding = pygame.USEREVENT+1 # Custom time event for controlling when pathfinding occurs

blockWidth = 40
horizontalCount = math.ceil(screenW/blockWidth) + 5
verticalCount = math.ceil(screenH/blockWidth) + 5

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
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\TestSquare.png").convert_alpha(), 0, 1)
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
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\goomba.png").convert_alpha(), 0, 0.25)
        self.baseEnemyImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseEnemyImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        self.closeRect = pygame.Rect(50, 50, 50, 50)
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        # Velocity
        self.speed = 1.2

        self.target = player

        self.override = False # Determins wether to override pathfinding

        self.rootNode = None

        self.pathFind = Pathfinding.Pathfinding((horizontalCount, verticalCount), showPathSprites, pathSprites)
        print("horizontalvert:", (horizontalCount, verticalCount))

    def RotateToTarget(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        Tx, Ty = self.target.rect.center
        #print("tx ty:", Tx, Ty)
        xDist = Tx - x
        yDist = Ty - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        velX = self.speed * math.cos(math.radians(self.angle))
        velY = self.speed * math.sin(math.radians(self.angle))
        self.direction = pygame.math.Vector2(velX, velY)
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        self.rect.center = self.hitboxRect.center
    
    def CreateLocalSprites(self, sprites):
        self.localSprites = pygame.sprite.Group()
        for sprite in sprites:
            if sprite.hitboxRect != self.hitboxRect and sprite not in enemySprites:
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

    def Move(self):
        self.pos.x += self.direction.x * self.speed
        self.hitboxRect.x = round(self.pos.x)
        self.CheckCollision('horizontal')

        self.pos.y += self.direction.y * self.speed
        self.hitboxRect.y = round(self.pos.y)
        self.CheckCollision('vertical')

        self.rect.center = self.hitboxRect.center    

    def FollowPath(self):
        # Removes a cell from the path list if collided with
        if len(self.pathFind.path) == 1 or self.override:
            self.target = player
        else:
            self.target = self.pathFind.path[0]
            if self.hitboxRect.colliderect(self.pathFind.path[0].rect):
                self.pathFind.path.remove(self.pathFind.path[0]) 
                self.target = self.pathFind.path[0]   

    def Update(self):
        """ Update the position of the enemy """

        if canPathfind:
            self.pathFind.Pathfind(self.hitboxRect, player.hitboxRect)
            self.override = self.pathFind.override

        if len(self.pathFind.path) > 0:
            self.FollowPath()
        self.RotateToTarget()
        self.Separate(0.05)
        self.Move()
        self.oldRect = self.hitboxRect.copy()
        self.closeRect.center = self.hitboxRect.center
        pygame.draw.rect(screen, white, self.closeRect)
    
    def Separate(self, factor):
        enemyClose = enemyRects[self.closeRect.collidelist(enemyRects)]
        x = self.pos.x - enemyClose.x
        y = self.pos.y - enemyClose.y
        self.direction.x += x*factor
        self.direction.y += y*factor
    
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

    def GetDist(startPos, targetPos):
        changeY = abs(startPos[1] - targetPos[1])
        changeX = abs(startPos[0] - targetPos[0])
        if changeX > changeY:
            dist = 14*(changeY) + 10*(abs(changeX - changeY))
            return dist
        dist = 14*(changeX) + 10*(abs(changeY - changeX))
        return dist

allSprites = pygame.sprite.Group() # Group of all Sprites. Must have a hitbox rect called 'hitboxRect'
liveSprites = pygame.sprite.Group() # Group of all 'living' sprites that need updating
obstacles = pygame.sprite.Group() # Group of all immobile sprites. Checked when pathfinding to note down obstacles. 
                                  # This group is needed as only non-moving sprites are recorded.
pathSprites = pygame.sprite.Group() # Group of sprites representing pathfinding script.
showPathSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group() # Group of enemy sprites.
enemyRects = [] # List of enemy rects

player = Player()
obstacle = Obstacle(20, 20, 300, 300)

allSprites.add(player)
allSprites.add(obstacle)
liveSprites.add(player)
obstacles.add(obstacle)

Pathfinding.CreateObstacleMap((horizontalCount, verticalCount), blockWidth, obstacles, pathSprites)

for _ in range(1):
    enemy = Enemy(random.randint(1, screenW-50), random.randint(1, screenH-50))
    allSprites.add(enemy)
    liveSprites.add(enemy)
    enemySprites.add(enemy)
    enemyRects.append(enemy.hitboxRect)
    enemy.CreateLocalSprites(allSprites)
    enemy.pathFind.CreateLocalPathMap()

player.CreateLocalSprites(allSprites)

background = pygame.Surface(screen.get_size())

run = True

pygame.time.set_timer(allowPathfinding, timeInterval)
MapMaker.CreateMap(MapMaker.map, screen)
for wall in MapMaker.wallList:
    allSprites.add(wall)
    
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

    #for sprite in showPathSprites:
            #screen.blit(sprite.image, sprite.rect)
    #for sprite in pathSprites:
        #screen.blit(sprite.image, sprite.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
