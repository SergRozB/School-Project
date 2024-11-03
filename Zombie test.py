import pygame
import math
import random
import MapMaker
import Pathfinding
import time

pygame.init()

pygame.display.set_caption("Zombie Test")

blockWidth = 15
widthOfMap = 0
for i in MapMaker.map[0]:
        widthOfMap += 1

screenW = 32*widthOfMap
screenH = 32*len(MapMaker.map)
print("ScreenW:", widthOfMap, "|ScreenH:", len(MapMaker.map))

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
screen = pygame.display.set_mode([screenW, screenH])
clock = pygame.time.Clock()

timeInterval = 500 # Time interval for when to pathfind in miliseconds
canPathfind = False
allowPathfinding = pygame.USEREVENT+1 # Custom time event for controlling when pathfinding occurs

horizontalCount = math.ceil(screenW/blockWidth) + 5
verticalCount = math.ceil(screenH/blockWidth) + 5

dt = 0

class MoveObject(pygame.sprite.Sprite):
    # Where movement is handled
    def __init__(self, startingPos, speed):
        super().__init__()
        self.pos = pygame.math.Vector2(startingPos[0], startingPos[1])
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = speed

        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\TestSquare.png").convert_alpha(), 0, 3)
        self.baseImage = self.image
        self.hitboxRect = self.baseImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        
        self.isColliding = False
    
    def CheckCollision(self, direction):
        collisionList = self.hitboxRect.collidedictall(self.localRects)
        if len(collisionList) > 0:
            self.isColliding = True
            if direction == 'horizontal':
                for sprite, rect in collisionList:
                        # If collision on the right
                        if self.hitboxRect.right >= rect.left and self.oldRect.right <= sprite.oldRect.left:
                            self.hitboxRect.right = rect.left
                            self.pos.x = self.hitboxRect.centerx
                        
                        # If collision on the left
                        if self.hitboxRect.left <= rect.right and self.oldRect.left >= sprite.oldRect.right:
                            self.hitboxRect.left = rect.right 
                            self.pos.x = self.hitboxRect.centerx

            if direction == 'vertical':
                for sprite, rect in collisionList:
                    # If collision on the bottom
                    if self.hitboxRect.bottom >= rect.top and self.oldRect.bottom <= sprite.oldRect.top:
                        self.hitboxRect.bottom = rect.top 
                        self.pos.y = self.hitboxRect.centery
                    
                    #print("self old right:", self.oldRect.right, "|other old left:", self.oldRect.left)
                    # If collision on the top
                    if self.hitboxRect.top <= rect.bottom and self.oldRect.top >= sprite.oldRect.bottom:
                        self.hitboxRect.top = rect.bottom
                        self.pos.y = self.hitboxRect.centery
        else:
            self.isColliding = False

    def Move(self, check):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt
        self.hitboxRect.centerx = self.pos.x
        if check:
            self.CheckCollision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt
        self.hitboxRect.centery = self.pos.y
        if check:
            self.CheckCollision('vertical')

        self.rect.center = self.hitboxRect.center
    
    def CreateLocalRects(self, sprites):
        self.localRects = {}
        for sprite in sprites:
            if sprite != self:
                self.localRects[sprite] = sprite.hitboxRect
    
    def Update(self):
        """ Update the position """
        self.oldRect = self.hitboxRect.copy()
        self.Move(True)

class Player(MoveObject):
    # Constructor. 
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__((100, 100), 100)
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\TestSquare.png").convert_alpha(), 0, 3)
        self.basePlayerImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

        self.inventory = []

    def UseItem(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.MOUSEBUTTONDOWN]:
            AutoRifle.Use()

    def CheckControls(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_SPACE]:
            AutoRifle.Use()
    
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
        self.lookDirection = pygame.math.Vector2(xDist, yDist)
        self.lookDirection = self.lookDirection.normalize()
        self.angle = math.degrees(math.atan2(yDist, xDist))
        self.image = pygame.transform.rotate(self.basePlayerImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        
    def Update(self):
        """ Update the position of the player """
        self.oldRect = self.hitboxRect.copy()

        self.CheckControls()
        self.UseItem()
        self.Move(True)
        self.RotateToMouse()
    

class Enemy(MoveObject):
    # Constructor. 
    def __init__(self, x, y):
        # Call the parent class (Move Object) constructor
        super().__init__((x,y), 60)

        # Create the image of the enemy
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\goomba.png").convert_alpha(), 0, 0.10)
        self.baseEnemyImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseEnemyImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        self.closeRect = pygame.Rect(0, 0, self.hitboxRect.width*1.5, self.hitboxRect.height*1.5)
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        self.target = player

        self.override = False # Determins wether to override pathfinding

        self.rootNode = None

        self.pathFind = Pathfinding.Pathfinding((horizontalCount, verticalCount), showPathSprites, pathSprites)
        print("horizontalvert:", (horizontalCount, verticalCount))

        self.health = 30
    
    def CheckDeath(self):
        if self.health <= 0:
            self.kill()

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
    
    def CreateLocalRects(self, sprites):
        self.localRects = {}
        for sprite in sprites:
            if sprite != self and sprite not in enemySprites:
                self.localRects[sprite] = sprite.hitboxRect

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
        self.oldRect = self.hitboxRect.copy()
        """ Update the position of the enemy """
        self.CheckDeath()
        if canPathfind:
            self.pathFind.Pathfind(self.hitboxRect, player.hitboxRect)
            self.override = self.pathFind.override

        if len(self.pathFind.path) > 0:
            self.FollowPath()
        self.RotateToTarget()
        self.Separate(2)
        self.Move(True)
        self.closeRect.center = self.hitboxRect.center
        #pygame.draw.rect(screen, white, self.closeRect)
    
    def Separate(self, factor):
        enemyClose = enemyRects[self.closeRect.collidelist(enemyRects)]
        x = self.pos.x - enemyClose.x
        y = self.pos.y - enemyClose.y
        self.direction.x += x*factor
        self.direction.y += y*factor

class RangedWeapon():
    def __init__(self, damage, fireRate, spread, magazineCap, totalAmmo, reloadSpeed):
        self.damage = damage
        self.fireRate = fireRate
        self.spread = spread
        self.magazineCap = magazineCap
        self.totalAmmo = totalAmmo
        self.reloadSpeed = reloadSpeed
        self.currentAmmo = magazineCap
        self.lastFired = 0
    
    def Use(self):
        timeSince = time.time() - self.lastFired
        print("current ammo:", self.currentAmmo)
        if timeSince >= self.fireRate and self.currentAmmo > 0:
            print("FIRED!")
            self.lastFired = time.time()
            self.Shoot()
            self.currentAmmo -= 1

        elif self.currentAmmo == 0 and self.totalAmmo > 0:
            if self.totalAmmo >= self.magazineCap:
                self.currentAmmo = self.magazineCap
                self.totalAmmo -= self.magazineCap

            elif self.totalAmmo < self.magazineCap:
                self.currentAmmo = self.totalAmmo
                self.totalAmmo = 0
    
    def Shoot(self):
        Bullet(player.pos, 100, self.damage, player.lookDirection)

class Bullet(MoveObject):
    def __init__(self, startingPos, speed, damage, direction):
        super().__init__(startingPos, speed)

        # Create the image of the bullet
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages/bullet.png").convert_alpha(), player.angle-90, 1)
        print("self pos:", self.pos, "| starting pos:", startingPos)
        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.image.get_rect()
        self.rect = self.hitboxRect.copy()
        self.hitboxRect.height = self.hitboxRect.height * 0.5
        self.hitboxRect.width = self.hitboxRect.width * 0.5
        self.hitboxRect.center = self.pos
        self.oldRect = self.hitboxRect.copy()
        self.direction = direction
        self.damage = damage
        allSprites.add(self)
        liveSprites.add(self)
        bullets.add(self)
        self.CreateLocalRects(allSprites)

    def DealDamage(self, sprite):
        sprite.health -= self.damage
    
    def CheckCollision(self):
        collidedWith = self.hitboxRect.collidedict(self.localRects)
        if collidedWith:
            spriteCollidedWith = collidedWith[0]
            if spriteCollidedWith != player and spriteCollidedWith not in bullets and spriteCollidedWith in allSprites:
                print("sprite name:", type(spriteCollidedWith).__name__)
                if spriteCollidedWith in liveSprites:
                    self.DealDamage(spriteCollidedWith)
                    self.kill()
                else:
                    self.kill()
    
    def Update(self):
        self.oldRect = self.hitboxRect.copy()
        self.Move(False)
        self.CheckCollision()

allSprites = pygame.sprite.Group() # Group of all Sprites. Must have a hitbox rect called 'hitboxRect'
liveSprites = pygame.sprite.Group() # Group of all 'living' sprites that need updating
obstacles = pygame.sprite.Group() # Group of all immobile sprites. Checked when pathfinding to note down obstacles. 
                                  # This group is needed as only non-moving sprites are recorded.
pathSprites = pygame.sprite.Group() # Group of sprites representing pathfinding script.
showPathSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group() # Group of enemy sprites.
bullets = pygame.sprite.Group() # Group of bullet sprites to check if bullet colliding with other bullet
enemyRects = [] # List of enemy rects

player = Player()

allSprites.add(player)
liveSprites.add(player)


MapMaker.CreateMap(MapMaker.map)
for wall in MapMaker.wallList:
    allSprites.add(wall)
    obstacles.add(wall)

player.CreateLocalRects(allSprites)

background = pygame.Surface(screen.get_size())

run = True

pygame.time.set_timer(allowPathfinding, timeInterval)

lastTime = time.time()

Pathfinding.CreateObstacleMap((horizontalCount, verticalCount), blockWidth, obstacles, pathSprites)

AutoRifle = RangedWeapon(10, 0.1, 5, 30, 1000, 1.5)

for _ in range(0):
    enemy = Enemy(random.randint(32, screenW-32), random.randint(32, screenH-32))
    allSprites.add(enemy)
    liveSprites.add(enemy)
    enemySprites.add(enemy)
    enemyRects.append(enemy.hitboxRect)
    enemy.CreateLocalRects(allSprites)
    enemy.pathFind.CreateLocalPathMap()

while run:
    dt = time.time() - lastTime
    lastTime = time.time()

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
        #pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)

    #for sprite in showPathSprites:
            #screen.blit(sprite.image, sprite.rect)
    #for sprite in pathSprites:
        #screen.blit(sprite.image, sprite.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
