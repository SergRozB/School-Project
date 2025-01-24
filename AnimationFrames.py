from pygame import image

# Animation Frames

# Player Axe Frames
playerAxeFrames = []
playerAxeFrames.append(image.load("SpriteImages\AxeSwing1.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing2.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing3.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing4.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing5.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing6.png"))
playerAxeFrames.append(image.load("SpriteImages\AxeSwing7.png"))
axeDamageFrame = 4 # Frame where damage should be inflicted

# Player Rifle Frames
playerRifleFrames = []
playerRifleFrames.append(image.load("SpriteImages\PlayerSpriteAutorifle1.png"))
playerRifleFrames.append(image.load("SpriteImages\PlayerSpriteAutorifle2.png"))
rifleFireFrame = 1

# Player Pistol Frames
playerPistolFrames = []
playerPistolFrames.append(image.load("SpriteImages\PlayerSpritePistol1.png"))
playerPistolFrames.append(image.load("SpriteImages\PlayerSpritePistol2.png"))
pistolFireFrame = 1