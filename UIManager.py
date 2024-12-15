import pygame
import Button
from time import time

class UIManager():
    def __init__(self, screenW, screenH):
        self.buttonList = []
        self.mouseButtonPressed = False
        self.storeSpriteList = [] # Defines array of items in store. Each element tructured like so: [item, item sprite, item price]  
        self.storeButtonsAdded = False
        self.storeButtonsList = []
        self.itemToBuy = 0
        self.notificationList = [] # List of notifications and their IDs, like so: (notification text, id)
        self.notificationTimeDict = {} # notification IDs to time when sent
        self.notificationID = 0 # notification ID is simply a counter
        self.screenW = screenW
        self.screenH = screenH
    
    def BlitText(self, screen, font, textInput, colour, position):
        text = font.render(textInput, True, colour)
        textRect = text.get_rect(center=position)
        screen.blit(text, textRect)

    def playerUI(self, player, screen):
        # Creates the player UI
        # Health text
        font = pygame.font.SysFont("cambria", 30)
        healthTextInput = "Health: "
        healthTextInput += str(player.health)
        self.BlitText(screen, font, healthTextInput, "white", (self.screenW * 0.1, self.screenH * 0.9))
        # Points text
        pointsTextInput = "Points: "
        pointsTextInput += str(player.points)
        self.BlitText(screen, font, pointsTextInput, "white", (self.screenW * 0.2, self.screenH * 0.9))
        # Current item box
        frameBehindItemSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
        frameBehindItemSurface = pygame.transform.scale(frameBehindItemSurface, (frameBehindItemSurface.get_rect().w*2, frameBehindItemSurface.get_rect().h*2))
        frameRect = frameBehindItemSurface.get_rect()
        frameRect.center = (self.screenW * 0.9+1, self.screenH * 0.9+1)
        screen.blit(frameBehindItemSurface, frameRect)
        itemSprite = player.GetCurrentItem().itemSprite
        itemSprite = pygame.transform.scale(itemSprite, (itemSprite.get_rect().w * 2, itemSprite.get_rect().h * 2))
        itemBoxRect = itemSprite.get_rect()
        itemBoxRect.center = (self.screenW * 0.9, self.screenH * 0.9)
        screen.blit(itemSprite, itemBoxRect)
        inventorySlotFont = pygame.font.SysFont("cambria", 15)
        itemNumberText = "Inventory slot: "
        itemNumberText += str(player.currentItem)
        self.BlitText(screen, inventorySlotFont, itemNumberText, "white", (self.screenW * 0.9, self.screenH * 0.85))
    
    def AddNotification(self, text):
        # Adds a notification to the notification list
        self.notificationTimeDict[self.notificationID] = time()
        self.notificationList.insert(0, (text, self.notificationID))
        self.notificationID += 1
    
    def BlitNotifications(self, screen):
        # Draws notifications onto screen
        fontSize = 20
        font = pygame.font.SysFont("cambria", fontSize)
        initialYlevel = self.screenH*0.8
        notificationDuration = 4 # How long a notification should last
        for notification in self.notificationList:
            timeSent = self.notificationTimeDict[notification[1]] 
            if (time() - timeSent) <= notificationDuration:
                coords = (self.screenW*0.9, initialYlevel - fontSize*self.notificationList.index(notification))
                backdropCoordsTracker = pygame.rect.Rect(0, 0, 300, 22)
                backdropCoordsTracker.center = coords
                backdrop = pygame.Surface((300,22))
                backdrop.set_alpha(128)
                backdrop.fill((0, 0, 0))
                screen.blit(backdrop, backdropCoordsTracker.topleft)
                self.BlitText(screen, font, notification[0], "white", coords)
            else:
                self.notificationList.remove(notification)
                self.notificationTimeDict.pop(notification[1])
    
    def SurvivorSelectionUI(self, screen):
        fontSize = 20
        middleY = self.screenH * 0.3
        xValue = self.screenW * 0.1
        font = pygame.font.SysFont("cambria", fontSize)
        instructionF = "Press F to make Survivor follow" 
        instructionG = "Press G to give Survivor weapon"
        instructionQ = "Press Q to send Survivor to location"
        backdropCoordsTracker = pygame.rect.Rect(0, 0, 300, 100)
        backdropCoordsTracker.center = (xValue, middleY)
        backdrop = pygame.Surface((310, 100))
        backdrop.set_alpha(128)
        backdrop.fill((0, 0, 0))
        screen.blit(backdrop, backdropCoordsTracker.topleft)
        self.BlitText(screen, font, instructionF, "white", (xValue, middleY-fontSize))
        self.BlitText(screen, font, instructionG, "white", (xValue, middleY))
        self.BlitText(screen, font, instructionQ, "white", (xValue, middleY+fontSize))
        
    
    def StatsJudgement(self, value, range, isReversed):
        # Returns wether a given stat of a survivor is good given the range
        ratio = (value - range[0]) / (range[1] - range[0])
        if isReversed:
            if ratio <= 0.2:
                return "Excellent"
            elif ratio <= 0.4:
                return "Good"
            elif ratio <= 0.6:
                return "Decent"
            elif ratio <= 0.8:
                return "Bad"
            else:
                return "Terrible"
        else:
            if ratio <= 0.2:
                return "Terrible"
            elif ratio <= 0.4:
                return "Bad"
            elif ratio <= 0.6:
                return "Decent"
            elif ratio <= 0.8:
                return "Good"
            else:
                return "Excellent"
    
    def SurvivorInfo(self, screen, survivor):
        size = 30
        xCoord = self.screenW * 0.9
        colour = "black"
        font = pygame.font.SysFont("cambria", size)
        nameText = "Name: "
        nameText += survivor.name
        strengthText = "Strength: "
        strengthText += self.StatsJudgement(survivor.strength, survivor.strengthRange, False) 
        speedText = "Speed: "
        speedText += self.StatsJudgement(survivor.speed, survivor.speedRange, False)
        attackSpeedText = "Attack speed: "
        attackSpeedText += self.StatsJudgement(survivor.attackSpeed, survivor.attackSpeedRange, True)
        awarenessText = "Awareness: "
        awarenessText += self.StatsJudgement(survivor.awareness, survivor.awarenessRange, False)
        top = self.screenH * 0.3
        textBackSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
        textBackSurface = pygame.transform.scale(textBackSurface, (textBackSurface.get_rect().w*10, size*6))
        rect = textBackSurface.get_rect()
        rect.center = (xCoord, 0)
        rect.top = top - size
        screen.blit(textBackSurface, rect)
        self.BlitText(screen, font, nameText, colour, (xCoord, top))
        self.BlitText(screen, font, strengthText, colour, (xCoord, top+size))
        self.BlitText(screen, font, speedText, colour, (xCoord, top+(size*2)))
        self.BlitText(screen, font, attackSpeedText, colour, (xCoord, top+(size*3)))
        self.BlitText(screen, font, awarenessText, colour, (xCoord, top+(size*4)))

    def DayUI(self, storeItems):
        # Creates UI for daytime
        nextWaveSurface = pygame.image.load("SpriteImages\WornButton.png")
        nextWaveSurface = pygame.transform.scale(nextWaveSurface, (200, 75))
        nextWaveButton = Button.Button(nextWaveSurface, self.screenW*0.1, self.screenH*0.8, "Next Wave", 30, "NextWave", True)
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
        if player.selectedSurvivor != None:
            self.SurvivorInfo(screen, player.selectedSurvivor)
            self.SurvivorSelectionUI(screen)
        self.BlitNotifications(screen)
    
    def CreateStore(self, screen):
        # Draws sprites from sprite list onto screen for store
        screenW = screen.get_width()
        sizeMultiplier = 2 # The multiplier applied to the sprite
        minSeparation = 5 # The minimum separation between sprites when displaying
        spriteWidth = 32 * sizeMultiplier
        maxSpritesOnScreen = (screenW) // (spriteWidth + minSeparation) # Calculates the maximum number of spirtes on the screen
        spriteCount = 0 # Number of sprites to draw on screen
        if maxSpritesOnScreen < len(self.storeSpriteList):
            spriteCount = maxSpritesOnScreen
        else:
            spriteCount = len(self.storeSpriteList)
        separation = (screenW - spriteCount * spriteWidth) / (spriteCount+1) # Calculates the separation to have between each sprite
        spriteOnScreenCount = 0
        currentX = separation
        yLevel = self.screenH * 0.2
        # Iterates through list of items, drawing their sprites and prices onto the screen
        for item, sprite, price in self.storeSpriteList:
            if spriteOnScreenCount < maxSpritesOnScreen:
                # Draws sprites onto screen
                sprite = pygame.transform.scale(sprite, (sprite.get_rect().w * sizeMultiplier, sprite.get_rect().h * sizeMultiplier))
                spriteBoxRect = sprite.get_rect()
                spriteBoxRect.center = (currentX, yLevel)
                screen.blit(sprite, spriteBoxRect)
                spriteOnScreenCount += 1
                # Draws text with cost of item onto screen
                font = pygame.font.SysFont("cambria", 20)
                itemCostText = "Price: "
                itemCostText += str(price)
                self.BlitText(screen, font, itemCostText, "black", (currentX, yLevel+spriteWidth/2))
                nameYlevel = (yLevel-(spriteWidth)/2)-10
                textBackSurface = pygame.image.load("SpriteImages\WornButton.png")
                textBackSurface = pygame.transform.scale(textBackSurface, (textBackSurface.get_rect().w*2, textBackSurface.get_rect().h*1.4))
                rect = textBackSurface.get_rect()
                rect.center = (currentX, nameYlevel)
                screen.blit(textBackSurface, rect)
                nameText = item.name
                self.BlitText(screen, font, nameText, "red", (currentX, nameYlevel))
                # Creates buttons which run code to buy items
                if not self.storeButtonsAdded:
                    print("store buttons?")
                    print("currnet x:", currentX)
                    buyButtonSurface = pygame.image.load("SpriteImages\SquareWornButton.png")
                    buyButtonSurface = pygame.transform.scale(buyButtonSurface, (32*3, 32*3))
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

