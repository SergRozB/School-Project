import pygame
import Camera

white = (255, 255, 255)
map = """WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW
         W                                                             W    
         W                                                             W     
         W                                                             W
         W                                                             W
         WWWW   WWWWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWWWW   WWWWW                     
         W                                                             W        
         W                                                             W        
         W                                                             W
    WWWWWW           WWWWWWWWW   WWWWWWWWWWWWWWWW   WWWWWWWW           WWWWWW
    W    W                                                             W    W
    W    W      WWW                                                    W    W
    W    W      WWW                                                    W    W
    W    W      WWW                      www            WWW            W    W
    W                                    www            WWW            W    W    
    W                                    www            WWW            W    W
    W                   www                                            W    W
    W    W              www                                            W    W
    W    W              www                                            W    W
    W    W                            WWW                              W    W
    W    W                            WWW                              W    W
    W    W       WWW                  WWW            www               W    W
    W    W       WWW                                 www               W    W
    W    W       WWW                                 www               W    W
    W    W                         www                                 W    W
    W    W                         www                                 W    W
    W    W                         www                                 W    W
    W                                             WWW                       W  
    W                WWW                          WWW                       W
    W                WWW          WWW             WWW                       W
    W    W           WWW          WWW                                  W    W
    W    W                        WWW                                  W    W
    W    W                                  WWW                        W    W
    W    W                  WWW             WWW          WWW           W    W
    W    W                  WWW             WWW          WWW           W    W
    W    W                  WWW                          WWW           W    W
    W    W                                                             W    W
    W    W                                                             W    W
    W    W             www                                             W    W
    W    W             www                                             W    W
    W                  www                          WWW                     W
    W                                 WWW           WWW                     W
    W                                 WWW           WWW                     W
    W    W                            WWW                              W    W
    W    W                                                             W    W
    W    W                 WWW                                         W    W
    W    W                 WWW           WWW                           W    W
    WWWWWW     WWW         WWW           WWW         www               WWWWWW
         W     WWW                       WWW         www               W
         W     WWW                                   www               W
         W                                                             W
         WWWWW   WWWWWWWWWWWWWWWWWWWW   WWWWWWWWWWWWWWWWWWWWWWWW   WWWWW                                         
         W                                                             W
         W                                                             W
         W                                                             W
         W                                                             W                                            
         WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"""

map = map.splitlines()
wallList = []
groundList = []
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
class Ground(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load("SpriteImages\Ground.png").convert_alpha(), 0, 1)
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
                #else:
                    #groundList.append(Ground(((x-distToMainWall)*offset, y*offset)))
            elif character == "W":
                #print("X:", x*32, "|Y:", y*32)
                wallList.append(Wall((x*offset, y*offset)))
            #else:
                #groundList.append(Ground((x*offset, y*offset)))
    #groundList.append(Ground((0, 0)))
