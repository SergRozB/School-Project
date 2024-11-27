import pygame
import Button


class UIManager():
    def __init__(self):
        self.buttonList = []
        self.mouseButtonPressed = False
        self.storeSpriteList = [] # Defines array of items in store. Each element tructured like so: [item, item sprite, item price]  
        self.storeButtonsAdded = False
        self.storeButtonsList = []
        self.itemToBuy = 0

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
        itemSprite = player.GetCurrentItem().itemSprite
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
        self.storeButtonsList = []
        self.storeSpriteList = []
        self.storeButtonsAdded = False
        for item in storeItems:
            # Adds sprites and price to the store sprites list
            self.storeSpriteList.append([item, item.itemSprite, item.price])

    def ButtonFunctions(self, name, waveManager, player):
        # Maps the button names to their functions
        if name == "NextWave":
            waveManager.NextWave(self)
        if name == "Buy":
            player.BuyItem(self.itemToBuy)
    
    def Update(self, screen, waveManager, player):
        # Updates list of buttons, checking for inputs
        for button in self.buttonList:
            mPos = pygame.mouse.get_pos()
            button.ChangeColour(mPos)
            if button.CheckForInput(mPos) and self.mouseButtonPressed:
                if button.isStoreButton:
                    self.itemToBuy = button.item
                self.ButtonFunctions(button.name, waveManager, player)
                if button.doKill:
                    self.buttonList.remove(button)
            button.Update(screen)
        # Runs code which creates store UI if it is daytime
        if waveManager.isDay:
            self.CreateStore(screen)
        self.playerUI(player, screen)
    
    def CreateStore(self, screen):
        # Draws sprites from sprite list onto screen for store
        screenW = screen.get_width()
        minSeparation = 5 # The minimum separation between sprites when displaying
        spriteWidth = 32
        maxSpritesOnScreen = screenW-5 // (spriteWidth + minSeparation) # Calculates the maximum number of spirtes on the screen
        spriteCount = 0 # Number of sprites to draw on screen
        if maxSpritesOnScreen < len(self.storeSpriteList):
            spriteCount = maxSpritesOnScreen
        else:
            spriteCount = len(self.storeSpriteList)
        separation = (screenW - spriteCount * spriteWidth) / (spriteCount+1) # Calculates the separation to have between each sprite
        spriteOnScreenCount = 0
        currentX = separation
        yLevel = 110
        # Iterates through list of items, drawing their sprites and prices onto the screen
        for item, sprite, price in self.storeSpriteList:
            if spriteOnScreenCount < maxSpritesOnScreen:
                # Draws sprites onto screen
                sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * 2, sprite.get_rect().h * 2))
                spriteBoxRect = sprite.get_rect()
                spriteBoxRect.center = (currentX, yLevel)
                screen.blit(sprite, spriteBoxRect)
                spriteOnScreenCount += 1
                # Draws text with cost of item onto screen
                font = pygame.font.SysFont("cambria", 30)
                itemCostText = "Price: "
                itemCostText += str(price)
                itemText = font.render(itemCostText, True, "white")
                itemTextRect = itemText.get_rect(center=(currentX, yLevel+spriteWidth+10))
                screen.blit(itemText, itemTextRect)
                # Creates buttons which run code to buy items
                #print("store buttons added?:", self.storeButtonsAdded)
                if not self.storeButtonsAdded:
                    print("store buttons?")
                    print("currnet x:", currentX)
                    buyButtonSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
                    buyButtonSurface = pygame.transform.scale(buyButtonSurface, (200, 75))
                    buyButton = Button.StoreButton(buyButtonSurface, currentX, yLevel, "   ", 30, "Buy", False, item)
                    self.buttonList.append(buyButton)
                    self.storeButtonsList.append(buyButton)
                currentX += spriteBoxRect.width + separation
        self.storeButtonsAdded = True
    
    def RemoveDayUI(self):
        # Removes the store buttons
        # Called when going from day to night
        print("called?")
        for button in self.storeButtonsList:
            self.buttonList.remove(button)

