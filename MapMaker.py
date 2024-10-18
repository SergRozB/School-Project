from pygame import image
from pygame import display
from pygame import quit
from pygame import event

screen = display.set_mode((1000, 500))
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
tile = image.load("SpriteImages\Tile1.png")
def CreateMap(map, screen):
    for y, line in enumerate(map):
        for x, character in enumerate(line):
            if character == "W":
                screen.blit(tile, (x*32-100, y*32))

loop = True
while loop:
    screen.fill((0, 0, 0))
    CreateMap(map, screen)
    display.update()
    for event in event.get():
        if event.type == quit:
            loop = False
quit()
