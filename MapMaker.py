import pygame

white = (255, 255, 255)
map = """
         WWWWWWWWWWWWWWW
         W             W
         W             W
         W             W
         W             W
         W     www     W
         W             W
         W             W
         W             W
         W             W
         WWWWWWWWWWWWWWW"""

map = map.splitlines()
wallList = []

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("SpriteImages\Tile1.png")
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.hitboxRect = self.image.get_rect(center = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

tile = pygame.image.load("SpriteImages\Tile1.png")
def CreateMap(map):
    for y, line in enumerate(map):
        for x, character in enumerate(line):
            if character == "W":
                wallList.append(Wall((x*32, y*32)))
