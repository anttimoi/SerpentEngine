import pygame, random, math, sys

tileSize = 32
screenResolution = [800,600]
tileSetWidth = 0
tileSetHeight = 0
fps = 60
cameraSpacing = tileSize*10
mapSize = [100, 100]

class IterRegistry(type):
    def __iter__(cls):
        return iter(cls._registry)

class Character:
    global tileSize, mapSize
    __metaclass__ = IterRegistry
    _registry = []

    def __init__(self, name, map):
        self._registry.append(self)
        self.name = name
        self.x = 0
        self.y = 0
        self.speed = 3
        self.sprite = pygame.Surface((tileSize, tileSize))
        self.map = map

    def move(self, x, y):
        if x != 0 and y != 0:
            x = (1/math.sqrt(2))*x
            y = (1/math.sqrt(2))*y

        newX = min((mapSize[0]-1)*tileSize, max(0, self.x + self.speed*x))
        newY = min((mapSize[1]-1)*tileSize, max(0, self.y + self.speed*y))

        hit = self.map.isHit(newX,self.y)
        if hit == False:
            self.x = newX

        hit = self.map.isHit(self.x,newY)
        if hit == False:
            self.y = newY

    def place(self, x, y):
        self.x = min((mapSize[0]-1)*tileSize, max(0, x))
        self.y = min((mapSize[1]-1)*tileSize, max(0, y))

    def setSprite(self, sprite):
        self.sprite.blit(sprite,(0, 0, tileSize, tileSize))
        self.sprite.set_colorkey((255, 0, 255))

    def printSprite(self, screen):
        screen.blit(self.sprite, (self.x, self.y))

class Map:
    global tileSize
    def __init__(self, size, tileSet):
        self.map = []
        self.hit = []
        self.tileSet = tileSet
        self.mapSurface = pygame.Surface((size[0]*tileSize,size[1]*tileSize))
        self.size = size
        self.tileSetWidth = 0
        self.generateMap(tileSet)

    def generateMap(self, tileSet):
        self.map = []
        self.hit = []
        for y in range(0,self.size[1]):
            slice = []
            sliceHit = []
            for x in range(0,self.size[0]):
                block = (random.randint(1,10) == 1)*2+1
                slice.append(block)
                hit = (slice[x] == 3)
                sliceHit.append(hit)
            self.map.append(slice)
            self.hit.append(sliceHit)
        self.mapSurface.set_colorkey((0, 0, 0))
        tileSetFile = pygame.image.load(tileSet)
        self.tileSetWidth = tileSetFile.get_width()
        tile = pygame.Surface((tileSize,tileSize))
        for x in range(0,len(self.map[0])):
            for y in range(0,len(self.map)):
                tile = pygame.Surface((tileSize,tileSize))
                tile.blit(tileSetFile, pygame.Rect(-1*self.getTileCoordinates(self.map[y][x])[0],-1*self.getTileCoordinates(self.map[y][x])[1],tileSize,tileSize))
                self.mapSurface.blit(tile, pygame.Rect(x*tileSize, y*tileSize, tileSize, tileSize))

    def isHit(self, x, y):
        hitBoxSize = 0.9
        hit = False
        points = []
        for xx in range(0,2):
            for yy in range(0,2):
                point = [math.floor((x+tileSize*(hitBoxSize*xx))/tileSize), math.floor((y+tileSize*(hitBoxSize*yy))/tileSize)]
                points.append(point)

        for point in points:
            if self.hit[point[1]][point[0]]:
                hit = True

        return hit

    def getTileCoordinates(self, id):
        global tileSize
        x = id%(self.tileSetWidth/tileSize)
        y = math.floor((id*tileSize)/self.tileSetWidth)
        return [int(x*tileSize),int(y*tileSize)]

class Camera:
    global tileSize, mapSize, screenResolution
    def __init__(self, target, cameraSpacing, dampening):
        self.target = target
        self.spacing = cameraSpacing
        self.offset = [0,0]
        self.dampening = dampening

    def update(self):
        playerScreenPos = [0,0]

        playerScreenPos[0] = self.target.x+self.offset[0]
        playerScreenPos[1] = self.target.y+self.offset[1]

        for i in range(0,2):
            cameraDelta = playerScreenPos[i]-cameraSpacing
            if cameraDelta < 0:
                self.offset[i]+=abs(cameraDelta)/self.dampening

            cameraDelta = screenResolution[i]-playerScreenPos[i]-cameraSpacing-tileSize
            if cameraDelta < 0:
                self.offset[i]-=abs(cameraDelta)/self.dampening

        for i in range(0,2):
            self.offset[i] = min(0, max(-1*(mapSize[i]*tileSize-screenResolution[i]),self.offset[i]))

    def render(self, screen, map, chars):
        self.update()
        screen.fill((128, 128, 128))
        screen.blit(map.mapSurface,(self.offset[0], self.offset[1]))

        renderSprites = []
        for char in chars:
            renderSprites.append([char.sprite, char.x, char.y])

        renderSprites.sort(key=lambda x: x[2])
        for sprite in renderSprites:
            screen.blit(sprite[0],(sprite[1]+self.offset[0],sprite[2]+self.offset[1]))

    def switch(self, old, new):
        self.target = new.target
        self.dampening = new.dampening
        self.spacing = new.spacing
        self.offset = old.offset

def main():
    global tileSize, tileSetWidth, tileSetHeight, screenResolution

    pygame.init()
    displayInfo = pygame.display.Info()
    #screenResolution = [displayInfo.current_w, displayInfo.current_h]
    size = screenResolution[0], screenResolution[1]
    screen = pygame.display.set_mode(size)

    map = Map(mapSize, "tileSet.png")

    charSprites = pygame.image.load("characters.png")
    sprite = pygame.Surface((tileSize, tileSize))
    sprite.blit(charSprites, pygame.Rect(-32, -32, tileSize, tileSize))

    player = Character("player", map)
    player.setSprite(sprite)

    camera = Camera(player, 10, 20)
    currentCamera = camera

    enemy = [None]*200

    for char in enemy:
        sprite = pygame.Surface((tileSize, tileSize))
        sprite.blit(charSprites, pygame.Rect(-1*random.randint(0,5)*32, -1*random.randint(0,5)*32, tileSize, tileSize))
        char = Character("enemy", map)
        char.setSprite(sprite)
        char.place(random.randint(0,mapSize[0]*tileSize), random.randint(0,mapSize[1]*tileSize))
        enemyTrack = char
    mapGenFlag = pygame.time.get_ticks()
    while 1:
        frameStart = pygame.time.get_ticks()

        # Input
        keys = pygame.key.get_pressed()
        player.move(keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_DOWN] - keys[pygame.K_UP])

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()
        if keys[pygame.K_ESCAPE]:
            sys.exit()

        for char in Character._registry:
            if char.name != "player":
                char.move(random.randint(-1,1), random.randint(-1,1))

        # Rendering
        if keys[pygame.K_1] and currentCamera.target != player:
            currentCamera.target = player
            print("Switching to player")
        if keys[pygame.K_2] and currentCamera.target != enemyTrack:
            currentCamera.target = enemyTrack
            print("Switching to enemy")
        if keys[pygame.K_3] and pygame.time.get_ticks()-mapGenFlag>500:
            mapGenFlag = pygame.time.get_ticks()
            map.generateMap(map.tileSet)

        currentCamera.render(screen, map, Character._registry)

        pygame.display.flip()

        # FPS sync
        if ((pygame.time.get_ticks()-frameStart) < (1000/fps)):
            pygame.time.wait(int((1000/fps)-(pygame.time.get_ticks()-frameStart)))

main()