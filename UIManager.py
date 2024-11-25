import pygame
import Button


class UIManager():
    def __init__(self):
        self.buttonList = []
        self.mouseButtonPressed = False

    def playerUI(self, player, screen):
        # Creates the player UI
        # Health text
        font = pygame.font.SysFont("cambria", 30)
        healthTextInput = "Health: "
        healthTextInput += str(player.health)
        healthText = font.render(healthTextInput, True, "white")
        healthTextRect = healthText.get_rect(center=(150, 550))
        screen.blit(healthText, healthTextRect)
        # Points text
        pointsTextInput = "Points: "
        pointsTextInput += str(player.points)
        pointsText = font.render(pointsTextInput, True, "white")
        pointsTextRect = pointsText.get_rect(center=(350, 550))
        screen.blit(pointsText, pointsTextRect)
        # Current item box
        position = (850, 550)
        frameBehindItemSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
        frameBehindItemSurface = pygame.transform.scale(frameBehindItemSurface, (frameBehindItemSurface.get_rect().w*2, frameBehindItemSurface.get_rect().h*2))
        frameRect = frameBehindItemSurface.get_rect()
        frameRect.center = position
        screen.blit(frameBehindItemSurface, frameRect)
        itemSprite = player.currentItem.itemSprite
        itemSprite = pygame.transform.scale(itemSprite, (itemSprite.get_rect().w * 2, itemSprite.get_rect().h * 2))
        itemBoxRect = itemSprite.get_rect()
        itemBoxRect.center = position
        screen.blit(itemSprite, itemBoxRect)

    def DayUI(self):
        # Creates UI for daytime
        nextWaveSurface = pygame.image.load("SpriteImages\WornButton.png")
        nextWaveSurface = pygame.transform.scale(nextWaveSurface, (200, 75))
        nextWaveButton = Button.Button(nextWaveSurface, 150, 450, "Next Wave", 30, "NextWave", True)
        self.buttonList.append(nextWaveButton)

    def ButtonFunctions(self, name, waveManager):
        # Maps the button names to their functions
        if name == "NextWave":
            waveManager.NextWave()
    
    def Update(self, screen, waveManager, player):
        for button in self.buttonList:
            mPos = pygame.mouse.get_pos()
            button.ChangeColour(mPos)
            if button.CheckForInput(mPos) and self.mouseButtonPressed:
                self.ButtonFunctions(button.name, waveManager)
                if button.doKill:
                    self.buttonList.remove(button)
            button.Update(screen)
        self.playerUI(player, screen)