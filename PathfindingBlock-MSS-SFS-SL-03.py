from pygame import sprite
from pygame import Surface

class Block(sprite.Sprite):
    
    def __init__(self, x, y, blockWidth, colour):
        super().__init__()

        self.image = Surface([blockWidth, blockWidth])
        self.image.fill(colour)
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