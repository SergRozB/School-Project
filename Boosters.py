from pygame import transform
from pygame import image
from time import time

class HealthBooster():
    def __init__(self):
        self.itemSprite = transform.rotozoom(image.load("SpriteImages\HealthSerum.png").convert_alpha(), 0, 1)
        self.price = 4
        self.isWeapon = False
        self.isDefault = False
        self.name = "Health Serum"
        self.newHealth = 200
    
    def Use(self, user):
        if user.health <= 100:
            user.health = self.newHealth
            user.inventory.remove(self)
            user.currentItem = 0
        else:
            print("Can't use when other health serum in effect")

class SpeedBooster():
    def __init__(self):
        self.itemSprite = transform.rotozoom(image.load("SpriteImages\SpeedSerum.png").convert_alpha(), 0, 1)
        self.price = 4
        self.isWeapon = False
        self.isDefault = False
        self.name = "Speed Serum"
        self.speedMultiplier = 2
        self.statusDuration = 30
    
    def Use(self, user):
        if not user.hasSpeedBoost:
            user.speed *= self.speedMultiplier
            user.hasSpeedBoost = True
            user.timeSinceSpeedBoost = time()
            user.statusList.append("speed")
            user.inventory.remove(self)
            user.currentItem = 0
        else:
            print("Can't use when other speed serum in effect")

class StrengthBooster():
    def __init__(self):
        self.itemSprite = transform.rotozoom(image.load("SpriteImages\StrengthPills.png").convert_alpha(), 0, 1)
        self.price = 4
        self.isWeapon = False
        self.isDefault = False
        self.name = "Strength Pills"
        self.newStrength = 2
        self.statusDuration = 30
    
    def Use(self, user):
        if not user.hasStrengthBoost:
            user.strength = self.newStrength
            user.hasStrengthBoost = True
            user.timeSinceStrengthBoost = time()
            user.statusList.append("strength")
            user.inventory.remove(self)
            user.currentItem = 0
        else:
            print("Can't use when other strength pill in effect")

class AttackSpeedBooster():
    def __init__(self):
        self.itemSprite = transform.rotozoom(image.load("SpriteImages\AttackSpeedTablet.png").convert_alpha(), 0, 1)
        self.price = 4
        self.isWeapon = False
        self.isDefault = False
        self.name = "Rage Tablet"
        self.newAttackSpeed = 2
        self.statusDuration = 30
    
    def Use(self, user):
        if not user.hasAttackSpeedBoost:
            user.attackSpeed = self.newAttackSpeed
            user.hasAttackSpeedBoost = True
            user.timeSinceAttackSpeedBoost = time()
            user.statusList.append("attackSpeed")
            user.inventory.remove(self)
            user.currentItem = 0
        else:
            print("Can't use when other tablet in effect")
