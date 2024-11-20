import pygame
zoomLevel = 0.5

class Camera():
    def __init__(self, player, screenValues):
        self.player = player
        self.offset = pygame.math.Vector2(0, 0)
        self.offsetFloat = pygame.math.Vector2(0, 0)
        self.displayW, self.displayH = screenValues[0], screenValues[1]
        self.const = pygame.math.Vector2((-self.displayW /2 + player.hitboxRect.width / 2) / zoomLevel, -self.displayH/2 / zoomLevel) 
        self.zoomLevel = zoomLevel

    def scroll(self):
        self.offsetFloat.x += (self.player.hitboxRect.x - self.offsetFloat.x + self.const.x) 
        self.offsetFloat.y += (self.player.hitboxRect.y - self.offsetFloat.y + self.const.y) 
        self.offset.x, self.offset.y = int(self.offsetFloat.x), int(self.offsetFloat.y)