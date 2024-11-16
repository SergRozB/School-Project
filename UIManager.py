import pygame
import Button


class UIManager():
    def __init__(self):
        self.buttonList = []
        self.mouseButtonPressed = False

    def playerUI(self, player, screen):
        font = pygame.font.SysFont("cambria", 30)
        textInput = "Health: "
        textInput += str(player.health)
        text = font.render(textInput, True, "white")
        textRect = text.get_rect(center=(150, 550))
        screen.blit(text, textRect)

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