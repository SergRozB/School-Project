import pygame

white = (255, 255, 255)
map = """WWWWWWWWWWWWWWWWWWWWWWWWWWW
         W               W         W
         W               W         W 
         W               W         W    
         W               W         W  
         W       W       W         W 
         W               W         W 
         W                         W
         W                         W   
         W                W        W 
         W                W        W
         W                W        W
         W                W        W
         W                W        W
         W                W        W
         WWWWWWWWWWWWWWWWWWWWWWWWWWW"""

map = map.splitlines()
wallList = []

class Wall(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.image.load("SpriteImages\Tile1.png")
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.hitboxRect = self.image.get_rect(topleft = self.pos)
        self.rect = self.hitboxRect.copy()
        self.oldRect = self.hitboxRect.copy()

def CreateMap(map):
    for y, line in enumerate(map):
        for x, character in enumerate(line):
            if y > 0:
                if character == "W":
                    #print("X:", x*32, "|Y:", y*32)
                    wallList.append(Wall(((x-9)*32, (y)*32)))
            elif character == "W":
                #print("X:", x*32, "|Y:", y*32)
                wallList.append(Wall((x*32, y*32)))
