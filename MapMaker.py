import pygame
import Camera

white = (255, 255, 255)
map = """WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW    
         W                                           W     
         W                                           W
         W                                           W
         WWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWWW                       
         W                                           W        
         W                                           W        
     WWWWW                                           WWWWW       
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W   
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W                                                   W
     W                                                   W
     W                                                   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W 
     W   W                                           W   W
     W   W                                           W   W
     W   W                                           W   W
     WWWWW                                           WWWWW
         W                                           W
         W                                           W
         WWWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWW                                         
         W                                           W
         W                                           W
         W                                           W                                   
         WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"""

map = map.splitlines()
wallList = []
offset = 32 
distToMainWall = 9
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
                    wallList.append(Wall(((x-distToMainWall)*offset, y*offset)))
            elif character == "W":
                #print("X:", x*32, "|Y:", y*32)
                wallList.append(Wall((x*offset, y*offset)))
