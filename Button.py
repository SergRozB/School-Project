import pygame
pygame.init()

class Button():
    def __init__(self, image, xPos, yPos, textInput, textSize, name, doKill):
        self.image = image
        self.xPos = xPos
        self.yPos = yPos
        self.textSize = textSize
        self.mainFont = pygame.font.SysFont("cambria", self.textSize)
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))
        self.textInput = textInput
        self.text = self.mainFont.render(self.textInput, True, "black")
        self.textRect = self.text.get_rect(center=(self.xPos, self.yPos))
        self.name = name
        self.doKill = doKill
        self.isStoreButton = False

    def Update(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.textRect)
    
    def CheckForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
    
    def ChangeColour(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.mainFont.render(self.textInput, True, "green")
        else:
            self.text = self.mainFont.render(self.textInput, True, "black")

class StoreButton(Button):
    def __init__(self, image, xPos, yPos, textInput, textSize, name, doKill, item):
        self.image = image
        self.xPos = xPos
        self.yPos = yPos
        self.textSize = textSize
        self.mainFont = pygame.font.SysFont("cambria", self.textSize)
        self.rect = self.image.get_rect(center=(self.xPos, self.yPos))
        self.textInput = textInput
        self.text = self.mainFont.render(self.textInput, True, "black")
        self.textRect = self.text.get_rect(center=(self.xPos, self.yPos))
        self.name = name
        self.doKill = doKill
        self.item = item
        self.isStoreButton = True
    
    def CheckForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
    
    def Update(self, screen):
        screen.blit(self.image, self.rect)
        screen.blit(self.text, self.textRect)