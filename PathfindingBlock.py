import pygame

class Block(pygame.sprite.Sprite):
    
    def __init__(self, x, y, blockWidth, colour):
        super().__init__()

        self.image = pygame.Surface([blockWidth, blockWidth])
        self.image.fill(colour)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.pos = (0,0)

        self.nextToWall = False
        self.hasObstacle = False
        self.distToTarget = 0
        self.visited = False
        self.vector = pygame.math.Vector2(0, 0)
    
    def changeColour(self, colour):
        self.image.fill(colour)