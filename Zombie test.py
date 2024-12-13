import pygame
import math
import random
import MapMaker
import VectorFieldPathfinding
import time
import Camera
import UIManager
import cProfile
import Pathfinding
import copy

pygame.init()
zoomLevel = Camera.zoomLevel

blockWidth = 32
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
lightBlue = (140, 255, 255)
darkSoftRed = (194, 36, 25)
screen = pygame.display.set_mode([screenW, screenH])
clock = pygame.time.Clock()

timeInterval = 500 # Time interval for when to pathfind in miliseconds
canPathfind = False
allowPathfinding = pygame.USEREVENT+1 # Custom time event for controlling when pathfinding occurs

#print("map W and map h:", mapW, mapH)
horizontalCount = math.ceil(mapW/blockWidth) 
verticalCount = math.ceil((mapH-top)/blockWidth) 
#print("horz, vert:", horizontalCount, verticalCount)
leftMButtonPressed = False
leftMButtonHeld = False
rightMButtonPressed = False
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
        super().__init__(startingPosition, 300)
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\PlayerSprite.png").convert_alpha(), 0, 1)
        self.basePlayerImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

        self.lookDirection = 0 # Stores the direction the player is looking in
        self.inventory = [Fists] # List containing inventory objects
        self.currentItem = 0 # Stores the position of the current item in the inventory list

        self.canUse = False # Stores if the player can use an item
        self.health = 100 # Stores the health of the player
        self.strength = 1
        self.attackSpeed = 1
        self.points = 0 # Stores the number of points the player has

        self.redTintDuration = 0.1 # The length of time the red tint should last for
        self.timeSinceTint = 0 # The time since the last red tint
        self.selectedSurvivor = None # Stores the selected Survivor
        self.givingCommand = False # Stores if the player is giving a command to check for inputs

    def UseItem(self):
        currentItem = self.GetCurrentItem()
        if leftMButtonHeld and currentItem.isWeapon:
            currentItem.Use(self)
        elif leftMButtonPressed and not currentItem.isWeapon:
            currentItem.Use(self)
    
    def GetCurrentItem(self):
        return self.inventory[self.currentItem]
    
    def ScrollInventory(self, direction):
        if direction == "up":
            if self.currentItem + 1 >= len(self.inventory):
                self.currentItem = 0
            else:
                self.currentItem += 1
        elif direction == "down":
            if self.currentItem - 1 <= 0:
                self.currentItem = len(self.inventory)-1
            else:
                self.currentItem -= 1
    
    def BuyItem(self, item):
        if item in self.inventory:
            print("Already in Inventory!")
        elif self.points >= item.price:
            self.inventory.append(item)
            self.points -= item.price
            print("Bought item!")
            print("Inventory:", self.inventory)
        else:
            print("But I don't have any moneeeey")

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
        #startPosX = (self.hitboxRect.centerx - camera.offset.x) * zoomLevel
        #startPosY = (self.hitboxRect.centery - camera.offset.y) * zoomLevel
        #pygame.draw.line(screen, "green", (startPosX, startPosY), (startPosX + self.lookDirection.x * 20, startPosY + self.lookDirection.y * 20)) 
    
    def TakeDamage(self, damage):
        # When called, takes the input damage from the health
        # If the health reached below or equal to zero, the 'dead' game loop is run
        self.health -= damage
        self.timeSinceTint = time.time()
        if self.health <= 0:
            dead()
    
    def CheckSelection(self):
        # Manages the selection of survivors to give them commands
        wiggleRoom = 50 # Defines the extra room around the survivor hitbox where the player can also select the survivor
        clickedSurvivor = False
        if self.selectedSurvivor != None:
            colour = 0
            if self.givingCommand:
                colour = "purple"
            else:
                colour = "red"
            survivorX = (self.selectedSurvivor.hitboxRect.centerx - camera.offset.x) * zoomLevel
            survivorY = (self.selectedSurvivor.hitboxRect.centery - camera.offset.y) * zoomLevel
            rectToDraw = pygame.rect.Rect(0, 0, self.selectedSurvivor.hitboxRect.w + wiggleRoom, self.selectedSurvivor.hitboxRect.h + wiggleRoom)
            rectToDraw.center = (survivorX, survivorY)
            pygame.draw.rect(screen, colour, rectToDraw, 2)

        for survivor in survivorSprites:
            survivorX = (survivor.hitboxRect.centerx - camera.offset.x) * zoomLevel
            survivorY = (survivor.hitboxRect.centery - camera.offset.y) * zoomLevel
            survivorLeft = int((survivor.hitboxRect.left - camera.offset.x) * zoomLevel) - wiggleRoom
            survivorRight = int((survivor.hitboxRect.right - camera.offset.x) * zoomLevel) + wiggleRoom
            survivorTop = int((survivor.hitboxRect.top - camera.offset.y) * zoomLevel) - wiggleRoom
            survivorBottom = int((survivor.hitboxRect.bottom - camera.offset.y) * zoomLevel) + wiggleRoom
            mPos = pygame.mouse.get_pos()
            if mPos[0] in range(survivorLeft, survivorRight) and mPos[1] in range(survivorTop, survivorBottom) and not self.selectedSurvivor == survivor:
                rectToDraw = pygame.rect.Rect(0, 0, survivor.hitboxRect.w + wiggleRoom, survivor.hitboxRect.h + wiggleRoom)
                rectToDraw.center = (survivorX, survivorY)
                pygame.draw.rect(screen, "green", rectToDraw, 2)
                if rightMButtonPressed:
                    self.selectedSurvivor = survivor
                    clickedSurvivor = True
        if not clickedSurvivor and rightMButtonPressed:
            self.selectedSurvivor = None
    
    def SurvivorCommands(self):
        # Carries out the commands on the selected survivor if the relevant key is pressed
        if not self.givingCommand:
            keys = pygame.key.get_pressed()
            # Checks if the f key is pressed, and if so carries out the follow command
            if keys[pygame.K_f]:
                self.selectedSurvivor.target = self
                self.selectedSurvivor.hasTarget = True
                self.selectedSurvivor = None

            # Checks if the g key is pressed, and if so carries out the give current item command
            if keys[pygame.K_g]:
                currentItem = self.GetCurrentItem()
                if not currentItem.isDefault:
                    print("gave", type(currentItem).__name__,"!")
                    self.selectedSurvivor.currentItem = copy.copy(currentItem)
                    self.inventory.remove(currentItem)
                    self.currentItem -= 1
                else:
                    print("You cant give fists!")
                self.selectedSurvivor = None

            # Checks if the q key is pressed, and if so carries out the go to point command
            if keys[pygame.K_q]:
                print("Giving command")
                self.givingCommand = True
    
    def GiveCommand(self):
        if rightMButtonPressed:
            mPos = pygame.mouse.get_pos()
            mx = (mPos[0] + camera.offset.x) * zoomLevel
            my = (mPos[1] + camera.offset.y) * zoomLevel
            tempObject = TempObject((mx, my))
            canMoveToPos = False
            listOfSprites = pygame.sprite.spritecollide(tempObject, allSprites, False)
            if len(listOfSprites) > 0:
                for sprite in listOfSprites:
                    if sprite not in obstacles:
                        canMoveToPos = True
            else:
                canMoveToPos = True
            
            if canMoveToPos:
                #allSprites.add(tempObject)
                self.selectedSurvivor.target = tempObject
                self.selectedSurvivor.followingCommand = True
                self.selectedSurvivor.hasTarget = True
                self.selectedSurvivor = None
                self.givingCommand = False
            else:
                print("Can't access location!")
                self.selectedSurvivor = None
                self.givingCommand = False

    def Update(self):
        """ Update the position of the player """
        self.oldRect = self.hitboxRect.copy()
        if self.givingCommand:
            self.GiveCommand()
        self.CheckControls()
        self.Move(True)
        self.RotateToMouse()
        self.UseItem()
        self.CheckSelection()
        if self.selectedSurvivor != None:
            self.SurvivorCommands()
        if (time.time() - self.timeSinceTint) < self.redTintDuration:
            self.image.fill(darkSoftRed, special_flags=pygame.BLEND_RGB_ADD)

class Survivor(MoveObject):
    def __init__(self, startingPosition):
        super().__init__(startingPosition, 300)
        
        # Create the image of the survivor
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\PlayerSprite.png").convert_alpha(), 0, 1)
        self.baseImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        self.lookDirection = 0
        self.currentItem = copy.copy(Fists)
        self.target = None # The actual target of the survivor
        self.pathTarget = None # The target the survivor will move towards which may not be the actual target
        self.hasTarget = False
        self.canUse = False # Determines if the survivor can use its item
        self.health = 100
        self.strength = round(random.uniform(0.5, 1.5), 2) # Multiplier affecting damage of melee weapons
        self.speed = random.randint(150, 450) # Randomly selects a speed
        self.attackSpeed = round(random.uniform(0.5, 1.5), 2) # Multiplier affecting rate of damage of melee weapons
        self.awareness = random.randint(500, 1500)
        self.rangeRect = pygame.Rect(self.hitboxRect.left, self.hitboxRect.top, self.awareness, self.awareness)
        survivorNames = ["Bart", "Maria", "Juan", "Takeshi", "Yusef", "Thomas", "Chris", "Sam", "Pedro", "Gabriel", "Ben", "Emily"]
        self.name = random.choice(survivorNames)
        self.redTintDuration = 0.1
        self.timeSinceTint = 0
        self.override = False # Overrides the pathfinding
        self.timeSincePathfind = 0 # Records the time since the last path find operation
        self.pathfindRate = 0.2 # Controls how often the survivor can pathfind in seconds
        self.followingCommand = False # Stores if the survivor is following a command, to stop doing other things
    
    def InitialisePathfinding(self):
        # Creates pathfinding object in survivor when called
        self.pathFind = Pathfinding.Pathfinding((horizontalCount, verticalCount), showPathSprites, pathSprites)
    
    def UseItem(self):
        # Uses current item when called
        if self.canUse:
            self.currentItem.Use(self)  
    
    def IsInRange(self):
        # Determins whether the survivor is close enough to its target
        # If target is zombie, survivor goes to attacking range of zombie 
        # Else if target is player, survivor stays further away from the player
        keepDistance = 0 # Determins the distance the survivor should stay away from the target
        if self.target == player:
            keepDistance = 80
        elif self.followingCommand:
            keepDistance = 32
        else:
            keepDistance = self.currentItem.ReturnRange()*0.6
        x, y = self.hitboxRect.center
        Tx, Ty = self.target.hitboxRect.center
        xDist = Tx - x
        yDist = Ty - y
        dist = math.sqrt(xDist**2 + yDist**2)
        #print("dist:", dist, "| attack range:", self.currentItem.ReturnRange())
        if dist <= keepDistance:
            print("in range!")
            if self.followingCommand:
                self.followingCommand = False
                self.hasTarget = False
            return True
        else:
            return False
            
    def RotateToTarget(self):
        # Rotates the survivor to the target object, but moves it towards the path target
        # The path target is generally the A* path
        x = (self.hitboxRect.centerx - camera.offset.x) * zoomLevel
        y = (self.hitboxRect.centery - camera.offset.y) * zoomLevel
        Tx, Ty = self.target.rect.center
        pTx, pTy = self.pathTarget.rect.center
        Tx = (Tx - camera.offset.x) * zoomLevel
        Ty = (Ty - camera.offset.y) * zoomLevel
        pTx = (pTx - camera.offset.x) * zoomLevel
        pTy = (pTy - camera.offset.y) * zoomLevel
        xDist = Tx - x
        yDist = Ty - y
        xpDist = pTx - x
        ypDist = pTy - y
        self.lookDirection = pygame.math.Vector2(xDist, yDist)
        if xDist != 0 or yDist != 0:
            self.lookDirection = self.lookDirection.normalize()
        #startPosX = (self.hitboxRect.centerx - camera.offset.x) * zoomLevel
        #startPosY = (self.hitboxRect.centery - camera.offset.y) * zoomLevel
        #pygame.draw.line(screen, "red", (startPosX, startPosY), (startPosX + self.lookDirection.x * 20, startPosY + self.lookDirection.y * 20)) 
        self.moveAngle = math.degrees(math.atan2(ypDist, xpDist))  
        self.angle = math.degrees(math.atan2(yDist, xDist))  
        velX = self.speed * math.cos(math.radians(self.moveAngle))
        velY = self.speed * math.sin(math.radians(self.moveAngle))
        self.direction = pygame.math.Vector2(velX, velY)
        self.image = pygame.transform.rotate(self.baseImage, -self.angle - 90)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        self.rect.center = self.hitboxRect.center
    
    def TakeDamage(self, damage):
        self.health -= damage
        self.timeSinceTint = time.time()
        if self.health <= 0:
            dead()
    
    def FollowPath(self):
        # Removes a cell from the path list if collided with
        if len(self.pathFind.path) == 1 or self.override:
            self.pathTarget = self.target
        else:
            self.pathTarget = self.pathFind.path[0]
            if self.hitboxRect.colliderect(self.pathFind.path[0].rect):
                self.pathFind.path.remove(self.pathFind.path[0]) 
                self.pathTarget = self.pathFind.path[0]   
    
    def CheckForZombies(self):
        # Checks if any zombies are within the range of the survivor 
        listOfRects = [item[0] for item in enemyRects]
        index = self.rangeRect.collidelist(listOfRects)
        if index != -1:
            self.target = enemyRects[index][1]
            self.hasTarget = True

        if self.hasTarget:
            if not self.target.alive():
                self.hasTarget = False
                self.direction = pygame.math.Vector2(0, 0)
            
    def Update(self):
        """ Update the position of the survivor """
        #print("survivor pos:", self.hitboxRect.center)
        self.oldRect = self.hitboxRect.copy()
        self.rangeRect.center = self.hitboxRect.center
        if not self.followingCommand:
            self.CheckForZombies()
        #print("target:", self.target, "| has target:", self.hasTarget)

        if (time.time() - self.timeSincePathfind) >= self.pathfindRate and self.hasTarget and not self.override:
            self.pathFind.Pathfind(self.hitboxRect, self.target.hitboxRect)
            #cProfile.runctx('self.pathFind.Pathfind(self.hitboxRect, self.target.hitboxRect)', globals(), locals(), sort='cumtime')
            self.override = self.pathFind.override
            self.timeSincePathfind = time.time()
        else:
            showPathSprites.empty()

        if len(self.pathFind.path) > 0:
            self.FollowPath()
        elif self.hasTarget:
            self.pathTarget = self.target

        if self.hasTarget:
            self.RotateToTarget()
            if self.IsInRange():
                if self.target != player:
                    self.currentItem.Use(self)
            else:
                self.Move(True)

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
        #self.hitboxRect.inflate(-2, -2)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()
        self.closeRect = pygame.Rect(self.hitboxRect.left, self.hitboxRect.top, self.hitboxRect.width*1.1, self.hitboxRect.height*1.1)
        #self.outsourcePathRect = pygame.Rect(0, 0, self.hitboxRect.width*1.5, self.hitboxRect.height*1.5)
        self.dealDamageRect = pygame.Rect(self.hitboxRect.left, self.hitboxRect.top, self.hitboxRect.width*1.1, self.hitboxRect.height*1.1)
        #self.isPathfinder = True

        self.target = player
        self.override = False # Determins wether to override pathfinding
        self.rootNode = None
        self.health = 60
        self.damage = 5
        self.initialTime = time.time()
        self.wait = True
        self.lastAttacked = 0
        self.damageRate = 0.5
        self.redTintDuration = 0.1
        self.timeSinceTint = 0      
        self.died = False
    
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
        if direction.x != 0 or direction.y != 0:
            self.direction = direction

    def TakeDamage(self, damage):
        self.health -= damage
        self.timeSinceTint = time.time()
        if self.health <= 0:
            print("DIE")
            if not self.died:
                player.points += 1
            self.died = True
            self.kill()
            player.localRects.pop(self)
            for surivor in survivorSprites:
                survivor.localRects.pop(self)
            enemyRects.remove((self.hitboxRect, self))

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
    def __init__(self, damage, fireRate, spread, magazineCap, totalAmmo, reloadSpeed, imagePath, price, isDefault):
        self.damage = damage
        self.fireRate = fireRate
        self.spread = spread
        self.magazineCap = magazineCap
        self.totalAmmo = totalAmmo
        self.reloadSpeed = reloadSpeed
        self.currentAmmo = magazineCap
        self.lastFired = 0
        self.itemSprite = pygame.transform.rotozoom(pygame.image.load(imagePath).convert_alpha(), 0, 1)
        self.price = price
        self.isWeapon = True
        self.isDefault = isDefault
    
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
    
    def ReturnRange(self):
        # Returns the range of the weapon from the user
        return 100000

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
            if spriteCollidedWith != player and spriteCollidedWith not in survivorSprites and spriteCollidedWith not in bullets and spriteCollidedWith in allSprites:
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

class TempObject(pygame.sprite.Sprite):
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

    def NextWave(self, uiManager):
        print("next wave")
        self.isDay = False
        uiManager.RemoveDayUI()
        self.waveCount += 1
        if self.waveCount == 1:
            self.spawnNumber = 1
        elif self.waveCount == 2:
            self.spawnNumber = 2
        elif self.waveCount == 3:
            self.spawnNumber = 4
        for spawnArea in self.spawnList:
            self.SpawnZombies(spawnArea)

    def Daytime(self, uiManager):
        uiManager.DayUI(storeItems)
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
        player.CreateLocalRects(allSprites)
        for survivor in survivorSprites:
            print("survivrorovrv")
            survivor.CreateLocalRects(allSprites)

class MeleeWeapon():
    def __init__(self, attackRange, attackSpeed, damage, imagePath, price, isDefault):
        self.attackRange = attackRange
        self.attackSpeed = attackSpeed
        self.damage = damage
        self.lastUsed = 0
        self.baseRangeImage = pygame.transform.rotozoom(pygame.image.load("SpriteImages\Axe Range.png").convert_alpha(), 0, 1)
        self.baseRangeImage = pygame.transform.scale(self.baseRangeImage, (self.baseRangeImage.get_rect().w, self.baseRangeImage.get_rect().h * attackRange))
        self.itemSprite = pygame.transform.rotozoom(pygame.image.load(imagePath).convert_alpha(), 0, 1)
        self.price = price
        self.isWeapon = True
        self.isDefault = isDefault
    
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
        if user == player:
            rangeImage = pygame.transform.rotate(self.baseRangeImage, -user.angle)
        else:
            rangeImage = pygame.transform.rotate(self.baseRangeImage, -user.angle - 90)
        rangeMask = pygame.mask.from_surface(rangeImage)
        maskImage = rangeMask.to_surface()
        rect = rangeImage.get_rect()
        offsetVector = pygame.math.Vector2(user.hitboxRect.centerx+user.lookDirection.x*16*self.attackRange, user.hitboxRect.centery+user.lookDirection.y*16*self.attackRange)
        rect.center = offsetVector
        #print("rect center:", rect.center)
        #pygame.draw.rect(screen, "green", rect)
        #screen.blit(maskImage, ((rect.x - camera.offset.x) * zoomLevel, (rect.y - camera.offset.y) * zoomLevel))
        screen.blit(pygame.transform.scale(maskImage, (rect.w * zoomLevel, rect.h * zoomLevel)), 
                        ((rect.x - camera.offset.x) * zoomLevel, (rect.y - camera.offset.y) * zoomLevel))
        listOfRects = [item[0] for item in enemyRects]
        indices = rect.collidelistall(listOfRects)
        for index in indices:
            zombieRect = listOfRects[index]
            zombieRectMask = pygame.mask.Mask((zombieRect.width, zombieRect.height))
            zombieRectMask.fill()
            offset = (rect.x - zombieRect.x, rect.y - zombieRect.y)
            if rangeMask.overlap(zombieRectMask, offset) and index < len(enemyRects):
                print("INDEX:", index, "| len:", len(listOfRects))
                print("enemy rects:", enemyRects)
                zombie = enemyRects[index][1]
                zombie.TakeDamage(self.damage)
    
    def ReturnRange(self):
        # Returns the range of the weapon from the user
        return self.baseRangeImage.get_rect().h * self.attackRange

def DrawMinimap():
    size = 0.1
    image = pygame.Surface((32, 32))
    backImage = pygame.Surface((mapW, mapH))
    backImage.fill(black)
    backRect = backImage.get_rect()
    backRect.topleft = (0, 0)
    screen.blit(pygame.transform.scale(backImage, (backRect.w * size, backRect.h * size)), 
                    (backRect.x + firstOccurrence*32 * size, backRect.y * size))
    for sprite in allSprites:
        if sprite == player:
            image = pygame.Surface((32, 32))
            image.fill(green)
            drawnRect = image.get_rect(center = sprite.hitboxRect.center)
        elif sprite in survivorSprites:
            image = pygame.Surface((32, 32))
            image.fill(lightBlue)
            drawnRect = image.get_rect(center = sprite.hitboxRect.center)
        elif sprite in enemySprites:
            image = pygame.Surface((32, 32))
            image.fill(red)
            drawnRect = image.get_rect(center = sprite.hitboxRect.center)
        else:
            image = pygame.Surface((32, 32))
            image.fill(white)
            drawnRect = image.get_rect(center = sprite.hitboxRect.center)
        screen.blit(pygame.transform.scale(image, (drawnRect.w * size, drawnRect.h * size)), 
                    (drawnRect.x * size, drawnRect.y * size))
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
survivorSprites = pygame.sprite.Group()

#################### CREATE OBJECTS ####################

AutoRifle = RangedWeapon(10, 0.1, 5, 30, 1000, 1.5, "SpriteImages\AutoRifleSprite.png", 15, False)
Axe = MeleeWeapon(2.5, 0.6, 50, "SpriteImages\AxeSprite.png", 4, False)
Fists = MeleeWeapon(1.5, 0.2, 20, "SpriteImages\FistSprite.png", 0, True)
player = Player((850, 850))
survivor = Survivor((850, 850))
enemySpawnTop = enemySpawnArea((32, 32), (61*32, 4*32))
enemySpawnLeft = enemySpawnArea((32*-4, 32*10), (4*32, 37*32))
enemySpawnRight = enemySpawnArea((32*63, 32*10), (4*32, 37*32))
enemySpawnBottom = enemySpawnArea((32, 32*52), (61*32, 4*32))

#################### SETUP ####################

allSprites.add(player)
allSprites.add(survivor)
noCollisionSprites.add(enemySpawnTop)
noCollisionSprites.add(enemySpawnLeft)
noCollisionSprites.add(enemySpawnRight)
noCollisionSprites.add(enemySpawnBottom)
liveSprites.add(player)
liveSprites.add(survivor)
survivorSprites.add(survivor)

MapMaker.CreateMap(MapMaker.map)
for wall in MapMaker.wallList:
    allSprites.add(wall)
    obstacles.add(wall)

player.CreateLocalRects(allSprites)
survivor.CreateLocalRects(allSprites)
zombieAttackSprites.add(player)

background = pygame.Surface(screen.get_size())

pygame.time.set_timer(allowPathfinding, timeInterval)

lastTime = time.time()
VectorFieldPathfinding.CreateObstacleMap((horizontalCount, verticalCount), blockWidth, obstacles, pathSprites, top, firstOccurrence)
pathFindPlayer = VectorFieldPathfinding.VectorFieldPathfinding((horizontalCount, verticalCount), player.hitboxRect, pathSprites)
pathFindPlayer.CreateLocalPathMap()
#Pathfinding.CreateObstacleMap((horizontalCount, verticalCount), blockWidth, obstacles, pathSprites, top, firstOccurrence)
survivor.InitialisePathfinding()
survivor.pathFind.CreateLocalPathMap()

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
    allSprites.add(TempObject(randomCoords))

#################### MAIN GAME LOOP ####################

def main():
    global run
    global lastTime
    global dt
    global lastTimeSincePath
    global leftMButtonHeld
    global leftMButtonPressed
    global rightMButtonPressed
    while True:
        dt = time.time() - lastTime
        lastTime = time.time()
        timeSincePath = time.time() - lastTimeSincePath
        if timeSincePath >= 0.5:
            #print("time:", timeSincePath)
            pathFindPlayer.CreateMap()
            #cProfile.runctx('pathFindPlayer.CreateMap()', globals(), locals(), sort='tottime')
            lastTimeSincePath = time.time()
        screen.fill(black)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #print("Mpos:", pygame.mouse.get_pos())
                leftMButtonHeld = True
                leftMButtonPressed = True
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                rightMButtonPressed = True

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                leftMButtonHeld = False
            
            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:
                    player.ScrollInventory("up")
                elif event.y == -1:
                    player.ScrollInventory("down")
        

        for sprite in liveSprites:
            sprite.Update()
            #print("name:", type(sprite).__name__)
            #cProfile.runctx('sprite.Update()', globals(), locals(), sort='cumtime')
            #pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
        uiManager.mouseButtonPressed = leftMButtonPressed
        leftMButtonPressed = False
        rightMButtonPressed = False
        camera.scroll()
        for sprite in allSprites:
            drawnRect = sprite.rect.copy()
            drawnRect.width = sprite.rect.width * zoomLevel
            drawnRect.height = sprite.rect.height * zoomLevel
            screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), 
                        ((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))
            #pygame.draw.rect(screen, "green", sprite.hitboxRect, width = 2)
        #pygame.draw.rect(screen, "green", Axe.rangeRect)

        #for sprite in showPathSprites:
            #drawnRect = sprite.rect.copy()
            #drawnRect.width = sprite.rect.width * zoomLevel
            #drawnRect.height = sprite.rect.height * zoomLevel
            #screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), 
                        #((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))
        
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
            #screen.blit(pygame.transform.scale(sprite.image, (sprite.image.get_rect().w * zoomLevel, sprite.image.get_rect().h * zoomLevel)), 
            # ((drawnRect.x - camera.offset.x) * zoomLevel, (drawnRect.y - camera.offset.y) * zoomLevel))

        DrawMinimap()

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