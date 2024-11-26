import pygame
import math
import random
import MapMaker
import VectorFieldPathfinding
import time
import Camera
import UIManager
import cProfile

pygame.init()
zoomLevel = Camera.zoomLevel

blockWidth = 34 
widthOfMap = 0
firstOccurrence = 1000
# Determins the width of the map and the starting x coord 
# from which to instantiate the pathfinding blocks.
for line in MapMaker.map:
    currentWidth = line.rindex("W")
    if MapMaker.map.index(line) > 0:
        currentFirstOccurence = line.index("W") - MapMaker.distToMainWall
    else:
        currentFirstOccurence = line.index("W")
    if currentWidth > widthOfMap:
        widthOfMap = currentWidth
    if currentFirstOccurence < firstOccurrence:
        firstOccurrence = currentFirstOccurence

topSpawnPoint = (100, 50)
top = 0

mapW = 32*widthOfMap
mapH = 32*len(MapMaker.map)
screenW = 1000
screenH = 600

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
green = (0, 255, 0)
darkSoftRed = (194, 36, 25)
screen = pygame.display.set_mode([screenW, screenH])
clock = pygame.time.Clock()

timeInterval = 500 # Time interval for when to pathfind in miliseconds
canPathfind = False
allowPathfinding = pygame.USEREVENT+1 # Custom time event for controlling when pathfinding occurs

print("map W and map h:", mapW, mapH)
horizontalCount = math.ceil(mapW/blockWidth) 
verticalCount = math.ceil((mapH-top)/blockWidth) 
print("horz, vert:", horizontalCount, verticalCount)

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
    def __init__(self, startingPosition):
        # Call the parent class (Sprite) constructor
        super().__init__(startingPosition, 500)
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\PlayerSprite.png").convert_alpha(), 0, 1)
        self.basePlayerImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

        self.lookDirection = 0
        self.inventory = []
        self.currentItem = Fists

        self.canUse = False
        self.health = 10000000000
        self.points = 0

        self.redTintDuration = 0.1
        self.timeSinceTint = 0

    def UseItem(self):
        if self.canUse:
            self.currentItem.Use(self)

    def CheckControls(self):
        keys = pygame.key.get_pressed()
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction.x = -1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction.x = 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.direction.y = -1
 
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.direction.y = 1

    
    def RotateToMouse(self):
        x = self.hitboxRect.centerx 
        y = self.hitboxRect.centery 
        Mx, My = pygame.mouse.get_pos()
        Mx = Mx / zoomLevel
        My = My / zoomLevel
        xDist = (Mx - x) + camera.offset.x 
        yDist = (My - y) + camera.offset.y 
        self.lookDirection = pygame.math.Vector2(xDist, yDist)
        self.lookDirection = self.lookDirection.normalize()
        self.angle = math.degrees(math.atan2(yDist, xDist)) + 90
        self.image = pygame.transform.rotate(self.basePlayerImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
    
    def TakeDamage(self, damage):
        self.health -= damage
        self.timeSinceTint = time.time()
        if self.health <= 0:
            dead()
        
    def Update(self):
        """ Update the position of the player """
        self.oldRect = self.hitboxRect.copy()

        self.CheckControls()
        self.Move(True)
        self.RotateToMouse()
        self.UseItem()
        if (time.time() - self.timeSinceTint) < self.redTintDuration:
            self.image.fill(darkSoftRed, special_flags=pygame.BLEND_RGB_ADD)

class Enemy(MoveObject):
    # Constructor. 
    def __init__(self, startingPos):
        # Call the parent class (Move Object) constructor
        super().__init__(startingPos, 200)

        # Create the image of the enemy
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\zombie.png").convert_alpha(), 0, 1)
        self.baseEnemyImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseEnemyImage.get_rect(center = self.pos)
        self.hitboxRect.inflate(-2, -2)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        self.closeRect = pygame.Rect(self.hitboxRect.left, self.hitboxRect.top, self.hitboxRect.width*1.1, self.hitboxRect.height*1.1)
        #self.outsourcePathRect = pygame.Rect(0, 0, self.hitboxRect.width*1.5, self.hitboxRect.height*1.5)
        self.dealDamageRect = pygame.Rect(self.hitboxRect.left, self.hitboxRect.top, self.hitboxRect.width*1.5, self.hitboxRect.height*1.5)
        #self.isPathfinder = True

        self.target = player
        self.override = False # Determins wether to override pathfinding
        self.rootNode = None
        self.health = 60
        self.damage = 10
        self.initialTime = time.time()
        self.wait = True
        self.lastAttacked = 0
        self.damageRate = 0.5
        self.redTintDuration = 0.1
        self.timeSinceTint = 0      
    
    def DealDamage(self):
        timeSince = time.time() - self.lastAttacked
        if timeSince >= self.damageRate:
            self.lastAttacked = time.time()
            index = self.dealDamageRect.collidelist(zombieAttackSprites.sprites())
            if index != -1:
                spriteInRange = zombieAttackSprites.sprites()[index]
                spriteInRange.TakeDamage(self.damage)
    
    def Wait(self):
        # To prevent enemy going through walls when spawning
        timeToWait = 0.1
        timeSince = (time.time() - self.initialTime)
        print("time since:", timeSince)
        if timeSince >= timeToWait:
            #print("r rh")
            self.wait = False

    def RotateToTarget(self):
        x = (self.hitboxRect.centerx - camera.offset.x) * zoomLevel
        y = (self.hitboxRect.centery - camera.offset.y) * zoomLevel
        Tx, Ty = self.target.rect.center
        Tx = (Tx - camera.offset.x) * zoomLevel
        Ty = (Ty - camera.offset.y) * zoomLevel
        xDist = Tx - x
        yDist = Ty - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        velX = self.speed * math.cos(math.radians(self.angle))
        velY = self.speed * math.sin(math.radians(self.angle))
        self.direction = pygame.math.Vector2(velX, velY)
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle - 90)
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

    def SetDirection(self):
        # Gets the direction the enemy needs to go in according to the pathfinder
        # Must run before move function
        direction = pathFindPlayer.GetDirection(self.hitboxRect)
        #pygame.draw.line(screen, 'red', self.pos, (self.pos.x + self.direction.x , self.pos.y + self.direction.y ))
        self.direction = direction

    def TakeDamage(self, damage):
        self.health -= damage
        self.timeSinceTint = time.time()
        if self.health <= 0:
            player.points += 1
            self.kill()

    def Update(self):
        if self.wait:
            self.Wait()
        else:
            self.oldRect = self.hitboxRect.copy()
            """ Update the position of the enemy """
            self.RotateToTarget()
            self.SetDirection()
            self.Move(True)
            self.closeRect.center = self.hitboxRect.center
            self.dealDamageRect.center = self.hitboxRect.center
            #pygame.draw.rect(screen, white, self.closeRect)
            #pygame.draw.rect(screen, white, self.dealDamageRect)
            self.Separate(0.005)
            self.DealDamage()
            if (time.time() - self.timeSinceTint) < self.redTintDuration:
                self.image.fill(darkSoftRed, special_flags=pygame.BLEND_RGB_ADD)
    
    def Separate(self, factor):
        listOfRects = [item[0] for item in enemyRects]
        enemyCloseList = self.closeRect.collidelistall(listOfRects)
        for index in enemyCloseList:
            enemyClose = listOfRects[index] 
            x = self.pos.x - enemyClose.x
            y = self.pos.y - enemyClose.y
            newVector = pygame.math.Vector2(x*factor, y*factor)
            newVector.normalize()
            self.pos.x += newVector.x
            self.pos.y += newVector.y
            #self.direction.x += x*factor
            #self.direction.y += y*factor

class RangedWeapon():
    def __init__(self, damage, fireRate, spread, magazineCap, totalAmmo, reloadSpeed, imagePath):
        self.damage = damage
        self.fireRate = fireRate
        self.spread = spread
        self.magazineCap = magazineCap
        self.totalAmmo = totalAmmo
        self.reloadSpeed = reloadSpeed
        self.currentAmmo = magazineCap
        self.lastFired = 0
        self.itemSprite = pygame.transform.rotozoom(pygame.image.load(imagePath).convert_alpha(), 0, 1)

    
    def Use(self, user):
        timeSince = time.time() - self.lastFired
        print("current ammo:", self.currentAmmo)
        if timeSince >= self.fireRate and self.currentAmmo > 0:
            print("FIRED!")
            self.lastFired = time.time()
            self.Shoot(user)
            self.currentAmmo -= 1

        elif self.currentAmmo == 0 and self.totalAmmo > 0:
            if self.totalAmmo >= self.magazineCap:
                self.currentAmmo = self.magazineCap
                self.totalAmmo -= self.magazineCap

            elif self.totalAmmo < self.magazineCap:
                self.currentAmmo = self.totalAmmo
                self.totalAmmo = 0
    
    def Shoot(self, user):
        Bullet(user.pos, 1000, self.damage, user.lookDirection)

class Bullet(MoveObject):
    def __init__(self, startingPos, speed, damage, direction):
        super().__init__(startingPos, speed)

        # Create the image of the bullet
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages/bullet.png").convert_alpha(), 0, 1)
        self.baseImage = self.image.copy()
        print("self pos:", self.pos, "| starting pos:", startingPos)
        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.image.get_rect()
        self.image = pygame.transform.rotate(self.baseImage, self.GetAngle())
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
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

    def GetAngle(self):
        # Angle still slightly off....
        x = (self.pos.x - camera.offset.x) * zoomLevel
        y = (self.pos.y - camera.offset.y) * zoomLevel
        Mx, My = pygame.mouse.get_pos()
        Mx = Mx  
        My = My 
        xDist = Mx - x 
        yDist = My - y 
        return -math.degrees(math.atan2(yDist, xDist)) - 90

    def DealDamage(self, sprite):
        sprite.TakeDamage(self.damage)
    
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

class enemySpawnArea(pygame.sprite.Sprite):
    def __init__(self, pos, dimensions):
        super().__init__()
        self.image = pygame.Surface(dimensions)
        self.image.fill(green)
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.rect = self.image.get_rect(topleft = self.pos)

class TestWall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("SpriteImages\Tile1.png")
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.hitboxRect = self.image.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

class WaveManager():
    def __init__(self, enemySpawnTop, enemySpawnBottom, enemySpawnLeft, enemySpawnRight):
        self.zombieCount = 0
        self.spawnNumber = 0
        self.spawnList = [enemySpawnTop, enemySpawnBottom, enemySpawnLeft, enemySpawnRight]
        self.isDay = False   
        self.waveCount = 0 
        self.maxWave = 3

    def NextWave(self):
        print("next wave")
        self.isDay = False
        self.waveCount += 1
        if self.waveCount == 1:
            self.spawnNumber = 1
        elif self.waveCount == 2:
            self.spawnNumber = 10
        elif self.waveCount == 3:
            self.spawnNumber = 15
        for spawnArea in self.spawnList:
            self.SpawnZombies(spawnArea)

    def Daytime(self, uiManager):
        uiManager.DayUI(storeItems, screen)
        player.health = 100

    def Update(self, enemySprites, uiManager):
        self.zombieCount = len(enemySprites)
        if self.zombieCount == 0 and not self.isDay:
            if self.waveCount != self.maxWave:
                print("Turn Day")
                self.Daytime(uiManager)
                self.isDay = True
            else:
                print("You Win!")

    def SpawnZombies(self, enemySpawn):
        # Spawns a number of zombies equivalent to the 'spawn number' in
        # the spawn areas. These spawn areas have to be initiated beforehand.
        print("generate wave")
        borderOffsetX = 16
        borderOffsetY = 16
        leftX = enemySpawn.rect.left+borderOffsetX
        rightX = enemySpawn.rect.right-borderOffsetX
        topY = enemySpawn.rect.top+borderOffsetY
        bottomY = enemySpawn.rect.bottom-borderOffsetY
        for _ in range(self.spawnNumber):
            enemy = Enemy((random.randint(leftX, rightX), random.randint(topY, bottomY)))
            #enemy = Enemy(random.randint(30, 31), random.randint(48, 112))
            #enemy = Enemy((leftX, topY))
            #print("Enemy pos:", enemy.pos, "| Enemy rect pos:", enemy.hitboxRect.center)
            allSprites.add(enemy)
            liveSprites.add(enemy)
            enemySprites.add(enemy)
            enemyRects.append((enemy.hitboxRect, enemy))
            enemy.CreateLocalRects(allSprites)

class MeleeWeapon():
    def __init__(self, attackRange, attackSpeed, damage, imagePath):
        self.attackRange = attackRange
        self.attackSpeed = attackSpeed
        self.damage = damage
        self.lastUsed = 0
        self.baseRangeImage = pygame.transform.rotozoom(pygame.image.load("SpriteImages\Axe Range.png").convert_alpha(), 0, 1)
        self.baseRangeImage = pygame.transform.scale(self.baseRangeImage, (self.baseRangeImage.get_rect().w, self.baseRangeImage.get_rect().h * attackRange))
        self.itemSprite = pygame.transform.rotozoom(pygame.image.load(imagePath).convert_alpha(), 0, 1)
    
    def Use(self, user):
        # Function called when the weapon is used
        timeSince = time.time() - self.lastUsed
        if timeSince >= self.attackSpeed:
            #print("USED!")
            self.lastUsed = time.time()
            self.Attack(user)
    
    def Attack(self, user):
        # Deals damage to the zombie colliding with the rect
        # of the weapon
        rangeImage = pygame.transform.rotate(self.baseRangeImage, -user.angle)
        rangeMask = pygame.mask.from_surface(rangeImage)
        maskImage = rangeMask.to_surface()
        rect = rangeImage.get_rect()
        offsetVector = pygame.math.Vector2(user.hitboxRect.centerx+user.lookDirection.x*16*self.attackRange, user.hitboxRect.centery+user.lookDirection.y*16*self.attackRange)
        rect.center = offsetVector
        print("rect center:", rect.center)
        #pygame.draw.rect(screen, "green", rect)
        screen.blit(maskImage, ((rect.x - camera.offset.x) * zoomLevel, (rect.y - camera.offset.y) * zoomLevel))
        listOfRects = [item[0] for item in enemyRects]
        indices = rect.collidelistall(listOfRects)
        for index in indices:
            zombieRect = listOfRects[index]
            zombieRectMask = pygame.mask.Mask((zombieRect.width, zombieRect.height))
            zombieRectMask.fill()
            offset = (rect.x - zombieRect.x, rect.y - zombieRect.y)
            if rangeMask.overlap(zombieRectMask, offset):
                zombie = enemyRects[index][1]
                zombie.TakeDamage(self.damage)

#################### CREATE GROUPS/LISTS ####################

allSprites = pygame.sprite.Group() # Group of all Sprites. Must have a hitbox rect called 'hitboxRect'
liveSprites = pygame.sprite.Group() # Group of all 'living' sprites that need updating
obstacles = pygame.sprite.Group() # Group of all immobile sprites. Checked when pathfinding to note down obstacles. 
                                  # This group is needed as only non-moving sprites are recorded.
pathSprites = pygame.sprite.Group() # Group of sprites representing pathfinding script.
showPathSprites = pygame.sprite.Group()
enemySprites = pygame.sprite.Group() # Group of enemy sprites.
bullets = pygame.sprite.Group() # Group of bullet sprites to check if bullet colliding with other bullet
noCollisionSprites = pygame.sprite.Group()
enemyRects = [] # 2d array of enemy rects and sprites ---> (enemy rect, enemy sprite)
UISprites = pygame.sprite.Group()
zombieAttackSprites = pygame.sprite.Group() # Group of sprites the zombies will attack
storeItems = []

#################### CREATE OBJECTS ####################

AutoRifle = RangedWeapon(10, 0.1, 5, 30, 1000, 1.5, "SpriteImages\AutoRifleSprite.png")
Axe = MeleeWeapon(1.5, 0.6, 50, "SpriteImages\AxeSprite.png")
Fists = MeleeWeapon(0.8, 0.2, 10, "SpriteImages\FistSprite.png")
player = Player((850, 850))
enemySpawnTop = enemySpawnArea((32, 32), (61*32, 4*32))
enemySpawnLeft = enemySpawnArea((32*-4, 32*10), (4*32, 37*32))
enemySpawnRight = enemySpawnArea((32*63, 32*10), (4*32, 37*32))
enemySpawnBottom = enemySpawnArea((32, 32*52), (61*32, 4*32))

#################### SETUP ####################

allSprites.add(player)
noCollisionSprites.add(enemySpawnTop)
noCollisionSprites.add(enemySpawnLeft)
noCollisionSprites.add(enemySpawnRight)
noCollisionSprites.add(enemySpawnBottom)
liveSprites.add(player)

MapMaker.CreateMap(MapMaker.map)
for wall in MapMaker.wallList:
    allSprites.add(wall)
    obstacles.add(wall)

player.CreateLocalRects(allSprites)
zombieAttackSprites.add(player)

background = pygame.Surface(screen.get_size())

pygame.time.set_timer(allowPathfinding, timeInterval)

lastTime = time.time()
VectorFieldPathfinding.CreateObstacleMap((horizontalCount, verticalCount), blockWidth, obstacles, pathSprites, top, firstOccurrence)
pathFindPlayer = VectorFieldPathfinding.VectorFieldPathfinding((horizontalCount, verticalCount), player.hitboxRect, pathSprites)
pathFindPlayer.CreateLocalPathMap()

camera = Camera.Camera(player, (screenW, screenH))
uiManager = UIManager.UIManager()
waveManager = WaveManager(enemySpawnTop, enemySpawnBottom, enemySpawnLeft, enemySpawnRight)

lastTimeSincePath = 0

storeItems = [Axe, AutoRifle]

#################### SPAWN ZOMBIES ####################

borderOffsetX = 16
borderOffsetY = 16
print("BROL:", enemySpawnTop.rect.left, "| BROR:", enemySpawnTop.rect.right)
print("BROu:", enemySpawnTop.rect.top, "| BROd:", enemySpawnTop.rect.bottom)
print("BROL:", enemySpawnTop.rect.left+borderOffsetX, "| BROR:", enemySpawnTop.rect.right-borderOffsetX)
print("BROu:", enemySpawnTop.rect.top+borderOffsetX, "| BROd:", enemySpawnTop.rect.bottom-borderOffsetX)
#allSprites.add(TestWall((enemySpawnTop.rect.left+borderOffsetX, enemySpawnTop.rect.top+borderOffsetX)))
#allSprites.add(TestWall((enemySpawnTop.rect.left+borderOffsetX, enemySpawnTop.rect.bottom-borderOffsetX)))
#allSprites.add(TestWall((enemySpawnTop.rect.right-borderOffsetX, enemySpawnTop.rect.top+borderOffsetX)))
#allSprites.add(TestWall((enemySpawnTop.rect.right-borderOffsetX, enemySpawnTop.rect.bottom-borderOffsetX)))
leftX = enemySpawnTop.rect.left+borderOffsetX
rightX = enemySpawnTop.rect.right-borderOffsetX
topY = enemySpawnTop.rect.top+borderOffsetY
bottomY = enemySpawnTop.rect.bottom-borderOffsetY
for _ in range(0):
    randomCoords = ((random.randint(leftX, rightX), random.randint(topY, bottomY)))
    print("coords:", randomCoords)
    allSprites.add(TestWall(randomCoords))

#################### MAIN GAME LOOP ####################

def main():
    global run
    global lastTime
    global dt
    global lastTimeSincePath
    while True:
        dt = time.time() - lastTime
        lastTime = time.time()
        timeSincePath = time.time() - lastTimeSincePath
        if timeSincePath >= 0.5:
            #print("time:", timeSincePath)
            pathFindPlayer.CreateMap()
            #cProfile.runctx('pathFindPlayer.CreateMap()', globals(), locals(), sort='cumtime')
            lastTimeSincePath = time.time()
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #print("Mpos:", pygame.mouse.get_pos())
                player.canUse = True
                uiManager.mouseButtonPressed = True
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                player.canUse = False
                uiManager.mouseButtonPressed = False

        for sprite in liveSprites:
            sprite.Update()
            #print("name:", type(sprite).__name__)
            #cProfile.runctx('sprite.Update()', globals(), locals(), sort='cumtime')
            #pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
        camera.scroll()
        for sprite in allSprites:
            drawnRect = sprite.rect.copy()
            drawnRect.width = sprite.rect.width * zoomLevel
            drawnRect.height = sprite.rect.height * zoomLevel
            screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), 
                        ((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))
            #pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
        #pygame.draw.rect(screen, "green", Axe.rangeRect)
        
        #for sprite in pathSprites:
            #drawnRect = sprite.rect.copy()
            #drawnRect.width = sprite.rect.width * zoomLevel
            #drawnRect.height = sprite.rect.height * zoomLevel
            #screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), 
                        #((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))

        #for sprite in noCollisionSprites:
            #drawnRect = sprite.rect.copy()
            #drawnRect.width = sprite.rect.width * zoomLevel
            #drawnRect.height = sprite.rect.height * zoomLevel
            #screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), ((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))
        #pathFindPlayer.DrawVectorMap(screen, camera)    
        #pathFindPlayer.DrawHeatMap(screen, camera)
        waveManager.Update(enemySprites, uiManager)
        uiManager.Update(screen, waveManager, player)
        pygame.display.update()
        clock.tick(60)
#################### DEATH GAME LOOP ####################
def dead():
    pygame.display.set_caption("Ded")
    global dt
    global lastTime
    while True:
        screen.fill("black")
        dt = time.time() - lastTime
        lastTime = time.time()

        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        pygame.display.update()
main()
#cProfile.runctx('Enemy.Update()', globals(), locals())
pygame.quit()