import pygame
import Button


class UIManager():
    def __init__(self):
        self.buttonList = []
        self.mouseButtonPressed = False
        self.storeSpriteList = []

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
        frameBehindItemSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
        frameBehindItemSurface = pygame.transform.scale(frameBehindItemSurface, (frameBehindItemSurface.get_rect().w*2, frameBehindItemSurface.get_rect().h*2))
        frameRect = frameBehindItemSurface.get_rect()
        frameRect.center = (851, 552)
        screen.blit(frameBehindItemSurface, frameRect)
        itemSprite = player.currentItem.itemSprite
        itemSprite = pygame.transform.scale(itemSprite, (itemSprite.get_rect().w * 2, itemSprite.get_rect().h * 2))
        itemBoxRect = itemSprite.get_rect()
        itemBoxRect.center = (850, 550)
        screen.blit(itemSprite, itemBoxRect)
        

    def DayUI(self, storeItems):
        # Creates UI for daytime
        nextWaveSurface = pygame.image.load("SpriteImages\WornButton.png")
        nextWaveSurface = pygame.transform.scale(nextWaveSurface, (200, 75))
        nextWaveButton = Button.Button(nextWaveSurface, 150, 450, "Next Wave", 30, "NextWave", True)
        self.buttonList.append(nextWaveButton)
        for item in storeItems:
            self.storeSpriteList.append(item.itemSprite)
            #THIS NOT UPDATING EVERY FRAME, MAKE IT DO SO

    def ButtonFunctions(self, name, waveManager):
        # Maps the button names to their functions
        if name == "NextWave":
            waveManager.NextWave()
    
    def Update(self, screen, waveManager, player):
        # Updates list of buttons, checking for inputs
        for button in self.buttonList:
            mPos = pygame.mouse.get_pos()
            button.ChangeColour(mPos)
            if button.CheckForInput(mPos) and self.mouseButtonPressed:
                self.ButtonFunctions(button.name, waveManager)
                if button.doKill:
                    self.buttonList.remove(button)
            button.Update(screen)
        if waveManager.isDay:
            # Draws sprites from sprite list onto screen for store
            screenW = screen.get_width()
            minSeparation = 5 # The minimum separation between sprites when displaying
            spriteWidth = 32
            maxSpritesOnScreen = screenW-5 // (spriteWidth + minSeparation) # Calculates the maximum number of spirtes on the screen
            print("max:", maxSpritesOnScreen)
            spriteCount = 0 # Number of sprites to draw on screen
            if maxSpritesOnScreen < len(self.storeSpriteList):
                spriteCount = maxSpritesOnScreen
            else:
                spriteCount = len(self.storeSpriteList)
            separation = (screenW - spriteCount * spriteWidth) / (spriteCount+1) # Calculates the separation to have between each sprite
            print("separation:", separation)
            spriteOnScreenCount = 0
            currentX = separation
            for sprite in self.storeSpriteList:
                if spriteOnScreenCount < maxSpritesOnScreen:
                    sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * 2, sprite.get_rect().h * 2))
                    spriteBoxRect = sprite.get_rect()
                    spriteBoxRect.center = (currentX, 110)
                    screen.blit(sprite, spriteBoxRect)
                    spriteOnScreenCount += 1
                    currentX += spriteBoxRect.width + separation
        self.playerUI(player, screen)