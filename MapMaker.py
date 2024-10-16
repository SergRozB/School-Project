import pygame
screen = pygame.display.set_mode((452, 256))
white = (255, 255, 255)
map = """
         WWWWWWWWWWWWWWWWWWWWWWWWWWW
         W                         W
         W    w                    W
         W                         W
         W                         W
         W            WWW          W
         W                         W
         W                         W
         W                         W
         W                         W
         WWWWWWWWWWWWWWWWWWWWWWWWWWW"""

map = map.splitlines()
for line in map:
    print(line)

#tile = pygame.surface.Surface([10, 10])
#tile.fill(white)
tile = pygame.image.load("SpriteImages\goomba.png")
def CreateMap(map, screen):
    for y, line in enumerate(map):
        for x, c in enumerate(line):
            if c == "W":
                screen.blit(tile, (x*16, y*16))
    
loop = True
while loop:
    screen.fill((0, 0, 0))
    CreateMap(map, screen)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == quit:
            loop = False
pygame.quit()