import pygame

screen = pygame.display.set_mode((1000, 500))
white = (255, 255, 255)
map = """
         WWWWWWWWWWWWWWW
         W             W
         W             W
         W             W
         W             W
         W             W
         W             W
         W             W
         W             W
         W             W
         WWWWWWWWWWWWWWW"""

map = map.splitlines()
for line in map:
    print(line)

#tile = pygame.surface.Surface([10, 10])
#tile.fill(white)
tile = pygame.image.load("SpriteImages\Tile1.png")
def CreateMap(map, screen):
    for y, line in enumerate(map):
        for x, character in enumerate(line):
            if character == "W":
                screen.blit(tile, (x*32-100, y*32))

loop = True
while loop:
    screen.fill((0, 0, 0))
    CreateMap(map, screen)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            loop = False
pygame.quit()
