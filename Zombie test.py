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
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    
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
        self.prevPos = self.pos
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 2
 
        # Create the image of the player
        self.image = pygame.transform.rotozoom(pygame.image.load("C:\Python School Stuff\School Game\Code\SpriteImages\TestSquare.png").convert_alpha(), 0, 1)
        self.basePlayerImage = self.image

        # Get a rectangle object that shows where our image is
        self.hitboxRect = self.basePlayerImage.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
 
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
        pygame.draw.line(screen, 'red', self.pos, (self.pos.x + self.velX * 100, self.pos.y + self.velY * 100))
        self.image = pygame.transform.rotate(self.baseEnemyImage, -self.angle)
        self.rect = self.image.get_rect(center = self.hitboxRect.center)
        
    def Update(self):
        """ Update the position of the enemy """
        self.Move()
        self.RotateToPlayer()
        self.oldRect = self.hitboxRect.copy()

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
        self.oldRect = self.rect


allSprites = pygame.sprite.Group() # Group of all Sprites. Must have a hitbox rect called 'hitboxRect'
liveSprites = pygame.sprite.Group() # Group of all 'living' sprites that need updating
obstacles = pygame.sprite.Group() # Group of all immobile sprites, for use in pathfinding
player = Player()
obstacle = Obstacle(20, 20, 300, 300)
allSprites.add(player)
allSprites.add(obstacle)
liveSprites.add(player)
obstacles.add(obstacle)

for _ in range(5):
    enemy = Enemy(random.randint(1, screenW), random.randint(1, screenH))
    allSprites.add(enemy)
    liveSprites.add(enemy)
    print(enemy.pos)

for sprite in liveSprites:
    sprite.CreateLocalSprites(allSprites)

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
    
    pygame.display.update()
    clock.tick(60)
    
pygame.quit()
