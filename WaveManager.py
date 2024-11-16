class WaveManager():
    def __init__(self, enemySpawnTop):
        self.zombieCount = 0
        self.spawnNumber = 0
        self.enemySpawnTop = enemySpawnTop
    
    def GenerateWave(self):
        pass

    def NextWave(self):
        print("next wave")
        pass

    def Daytime(self):
        pass

    def Update(self, enemySprites):
        self.zombieCount = len(enemySprites)

    def SpawnZombies(self):
        # Spawns a number of zombies equivalent to the 'spawn number' in
        # the spawn areas. These spawn areas have to be initiated beforehand.
        borderOffsetX = 16
        borderOffsetY = 16
        leftX = self.enemySpawnTop.rect.left+borderOffsetX
        rightX = self.enemySpawnTop.rect.right-borderOffsetX
        topY = self.enemySpawnTop.rect.top+borderOffsetY
        bottomY = self.enemySpawnTop.rect.bottom-borderOffsetY
        for _ in range(self.spawnNumber):
            enemy = Enemy((random.randint(leftX, rightX), random.randint(topY, bottomY)))
            #enemy = Enemy(random.randint(30, 31), random.randint(48, 112))
            #enemy = Enemy((leftX, topY))
            #print("Enemy pos:", enemy.pos, "| Enemy rect pos:", enemy.hitboxRect.center)
            allSprites.add(enemy)
            liveSprites.add(enemy)
            enemySprites.add(enemy)
            enemyRects.append(enemy.hitboxRect)
            enemy.CreateLocalRects(allSprites)
            enemy.pathFind.CreateLocalPathMap()