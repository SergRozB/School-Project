import pygame
import math
import random

pygame.init()

pygame.display.set_caption("Zombie Test")

screenW = 800
screenH = 600

white = (255, 255, 255)
black = (0, 0, 0)
screen = pygame.display.set_mode([screenW, screenH])
velocity = 2
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    """ This class represents the ball
        It derives from the "Sprite" class in Pygame """
    
    # Vector position
    pos = 0
 
    # Velocity
    velX = 0
    velY = 0
 
    width = 20
    height = 20

 
    # Constructor. 
    def __init__(self):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.pos = pygame.math.Vector2(100, 100)
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("C:\Python School Stuff\School Game\Code\SpriteImages\TestSquare.png").convert_alpha(), 0, 1)
        self.basePlayerImage = self.image
        #self.image = pygame.Surface([self.width, self.height])

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
 
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()     

        self.localHitboxes = []

    def CheckControls(self):
        keys = pygame.key.get_pressed()
        self.velX = 0
        self.velY = 0
    
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velX -= velocity

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velX += velocity

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velY -= velocity
 
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velY += velocity

        if self.velX != 0 and self.velY != 0:
            self.velX /= math.sqrt(2)
            self.velY /= math.sqrt(2)

    def RotateToMouse(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        Mx, My = pygame.mouse.get_pos()
        xDist = Mx - x
        yDist = My - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        #print("angle:", self.angle)
        self.image = pygame.transform.rotate(self.basePlayerImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)

    def Move(self):
        self.pos +=  pygame.math.Vector2(self.velX, self.velY)
        self.hitboxRect.center = self.pos
        self.rect.center = self.hitboxRect.center
        
    def Update(self):
        """ Update the position of the player """

        #print(f"POS: ({self.pos[0]}. {self.pos[1]})")
        self.CheckControls()
        self.Move()
        self.RotateToMouse()
    
    def GetHitbox(self):
        return self.hitboxRect
    
    def GetVelocity(self):
        return [self.velX, self.velY]
    
    def CreateLocalHitboxes(self, rectList):
        print("local hit boxes:", self.localHitboxes)
        for rect in rectList:
            if rect != self.hitboxRect:
                self.localHitboxes.append(rect)
    
    def Test(self):
        print("test") 

class Enemy(Player):
    """ This class represents the ball
        It derives from the "Sprite" class in Pygame """
    
    # Vector position
    pos = 0
 
 
    width = 20
    height = 20

    # Constructor. 
    def __init__(self, x, y):
        # Call the parent class (Sprite) constructor
        super().__init__()

        self.pos = pygame.math.Vector2(x, y)
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("C:\Python School Stuff\School Game\Code\SpriteImages\goomba.png").convert_alpha(), 0, 1)
        self.baseEnemyImage = self.image
        #self.image = pygame.Surface([self.width, self.height])

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.baseEnemyImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
 
        # Get attributes for the height/width of the screen
        self.screenheight = pygame.display.get_surface().get_height()
        self.screenwidth = pygame.display.get_surface().get_width()

        self.localHitboxes = []

        # Velocity
        self.velX = velocity/2
        self.velY = velocity/2

    def RotateToPlayer(self):
        x = self.hitboxRect.centerx
        y = self.hitboxRect.centery
        #print("Playerpos:", player.pos)
        Px, Py = player.pos
        xDist = Px - x
        yDist = Py - y
        self.angle = math.degrees(math.atan2(yDist, xDist))
        #print("ANGLE:", self.angle)
        self.velX = velocity/2 * math.cos(math.radians(self.angle))
        self.velY = velocity/2 * math.sin(math.radians(self.angle))
        #print("distX:", xDist, "| distY:", yDist, "| distY/distY:", xDist/yDist)
        #print("VELX:", self.velX, "| VELY:", self.velY)
        pygame.draw.line(screen, 'red', self.pos, (self.pos.x + self.velX * 100, self.pos.y + self.velY * 100))
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)

        
    def Update(self):
        """ Update the position of the enemy """

        #print(f"POS: ({self.pos[0]}. {self.pos[1]})")
        self.Move()
        self.RotateToPlayer()
        self.CheckCollision()

    def CheckCollision(self):
        arrayPos = self.hitboxRect.collidelist(self.localHitboxes)
        if arrayPos != -1:
            #print(self.hitboxRect.collidelist(self.localHitboxes))
            #print("colliding!")
            spriteColWith = 0 # Will store the sprite collided with
            for item in hitboxRef:
                if item[0] == self.localHitboxes[arrayPos]:
                    spriteColWith = item[1]
            spritePos = spriteColWith.pos
            xDiff = self.pos[0] - spritePos[0]
            yDiff = self.pos[1] - spritePos[1] 
            self.velX = xDiff * spriteColWith.GetVelocity()[0]
            self.velY = yDiff * spriteColWith.GetVelocity()[1]

allSprites = pygame.sprite.Group() # Must have a hitbox rect called 'hitboxRect'
player = Player()
enemy = Enemy(random.randint(1, screenW), random.randint(1, screenH))
enemy1 = Enemy(random.randint(1, screenW), random.randint(1, screenH))
enemy2 = Enemy(random.randint(1, screenW), random.randint(1, screenH))
allSprites.add(player)
allSprites.add(enemy)
allSprites.add(enemy1)
allSprites.add(enemy2)
spriteHitboxes = []
hitboxRef = [] # 2D array which links rects to sprite. [array, sprite]

for sprite in allSprites:
    spriteHitboxes.append(sprite.GetHitbox())
    hitboxRef.append([sprite.GetHitbox(), sprite])

for sprite in allSprites:
    sprite.CreateLocalHitboxes(spriteHitboxes)

for i in spriteHitboxes:
    print("fnenfe:", i)

background = pygame.Surface(screen.get_size())

run = True

while run:
    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    player.Update()
    enemy.Update()
    enemy1.Update()
    enemy2.Update()
    pygame.draw.rect(screen, "red", player.hitboxRect, width=2)
    #pygame.draw.rect(screen, "yellow", player.rect, width=2)
    pygame.draw.rect(screen, "green", enemy.hitboxRect, width = 2)
    pygame.draw.rect(screen, "green", enemy1.hitboxRect, width = 2)
    pygame.draw.rect(screen, "green", enemy2.hitboxRect, width = 2)
    #allSprites.draw(screen)
    screen.blit(player.image, player.rect)
    screen.blit(enemy.image, enemy.rect)
    screen.blit(enemy1.image, enemy1.rect)
    screen.blit(enemy2.image, enemy2.rect)
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
