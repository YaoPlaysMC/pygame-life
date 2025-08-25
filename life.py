import pygame, asyncio, os, requests, math, random, time, colorsys
# from multiprocessing import Process


# birth = [3, 4]
# survive = [2, 3, 7]
# numStates = 3
birth = [3, 5, 7]
survive = [2, 3, 5, 6, 8]

rules = [
    # ([3, 5, 7], [2, 3, 5, 6, 8], 4),
    # ([3, 4, 7, 8], [2, 3, 8], 3),
    # ([3, 5, 7], [2, 3, 5, 6], 4),
    # ([3, 4], [2, 3, 7], 3),
    ([3], [2, 3], 2),
    ([3, 6], [2, 3], 2),
    ([3, 5, 7], [2, 3, 8], 2),
    ([3, 5, 7], [2, 3], 2),
    # ([3,4], [1,2], 3)
]

currRule = 0
currHue = 0
numStates = 4
fps = 20
width = 130
height = 64

screenX = 800
screenY = 480

tileSize = 10

width = screenX // tileSize
height = screenY // tileSize

randomRules = True
color = "rainbow"
fullscreen = False
generationsOnly = False

wrapX = True
wrapY = True
offsetX = 0
offsetY = 0
# , flags=pygame.FULLSCREEN
if fullscreen:
    display = pygame.display.set_mode((screenX, screenY), flags=pygame.FULLSCREEN)
else:
    display = pygame.display.set_mode((screenX, screenY))

pygame.init()
clock = pygame.time.Clock()

state = [[0 for i in range(height)] for i in range(width)]
maxCacheSize = 100000
tiles = {}
cache = []
showFps = False

def init():
    tiles[0] = pygame.Surface((tileSize, tileSize))
    tiles[1] = pygame.Surface((tileSize, tileSize))
    tiles[2] = pygame.Surface((tileSize, tileSize))
    tiles[3] = pygame.Surface((tileSize, tileSize))
    tiles[0].fill((0,0,0))
    tiles[1].fill((255,255,255))
    tiles[2].fill((255,0,0))
    tiles[3].fill((127,0,0))

def reset():
    global dead, timer, curr, birth, numStates, survive, state, changed, table
    state = [[0 for i in range(height)] for i in range(width)]
    changed = [[1 for i in range(height)] for i in range(width)]
    # fill(5, 75, 5, 15)
    # fill(5, 75, 38, 43)
    fill(0, 80, 0, 48)
    dead = False
    timer = 0
    curr = 0
    birth = rules[currRule][0]
    survive = rules[currRule][1]
    numStates = rules[currRule][2]
    cache.clear()
    table = [0 for i in range(numStates * 10)]
    for i in range(numStates):
        for j in range(10):
            table[10*i + j] = getNextState(i, j)
    for x in range(min(width, screenX // tileSize)):
        for y in range(min(height, screenY // tileSize)):
            # if changed[x][y] or state[x][y] != 0:
                display.blit(tiles[0], (x * tileSize, y*tileSize))
    updateBoard()


def fill(x0, xf, y0, yf):
    for x in range(x0, xf):
        for y in range(y0, yf):
            state[x][y] = random.randint(0, 1)

def getNextState(currState, numAlive):
    if currState == 1:
        #print(numAlive)
        if numAlive in survive:
            return 1
        elif numStates <= 2:
            return 0
        return 2
    elif currState == 0:
        if numAlive in birth:
            return 1
        return 0
    elif currState >= 2:
        currState += 1
        if currState >= numStates:
            return 0
        return currState

table = []

def updateBoard():
    global state, changed
    newState = [[0 for i in range(height)] for i in range(width)]
    newChanged = [[0 for i in range(height)] for i in range(width)]
    for x in range(width):
        for y in range(height):
            if not changed[x][y]:
                newState[x][y] = state[x][y]
                continue
            curr = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    MikuLewds = (x + i) % width
                    KannaLewds = (y + j) % height

                    if i == 0 and j == 0:
                        continue

                    # if MikuLewds < 0 or MikuLewds >= width:
                    #     if wrapX:
                    #         MikuLewds = MikuLewds % width
                    #     else: continue
                    # if KannaLewds < 0 or KannaLewds >= height:
                    #     if wrapX:
                    #         KannaLewds = KannaLewds % height
                    #     else: continue
                    if state[MikuLewds][KannaLewds] == 1:
                        curr += 1
            
            newState[x][y] = table[10 * state[x][y] + curr]# getNextState(state[x][y], curr) # table[state[x][y]][curr]
            if newState[x][y] != state[x][y]:
                for i in range(-1, 2):
                    for j in range(-1, 2):
                        MikuLewds = x + i
                        KannaLewds = y + j
                        newChanged[MikuLewds%width][KannaLewds%height] = True
    changed = newChanged
    state = newState

def updateScreen():
    global currHue
    if color == "rainbow":
        currHue += 0.001
        currHue %= 1
        rgb = colorsys.hsv_to_rgb(currHue, 1, 1)
        colorMult = [0, 255, 127, 63]
        for i in range(1, numStates):
            tiles[i].fill((int(rgb[0] * colorMult[i]), int(rgb[1] * colorMult[i]), int(rgb[2] * colorMult[i])))
    elif color == "vibe":
        currHue += 0.001
        currHue %= 1
        colorMult = [0, 0, 255, 127]
        for i in range(2, numStates):
            r, g, b = map(lambda a: int(a * colorMult[i]), colorsys.hsv_to_rgb(currHue, 1, 1))
            tiles[i].fill((r, g, b))
            # print(r, g, b)

    # display.fill((0, 0, 0))
    # temp = 0
    for x in range(min(width, screenX // tileSize)):
        for y in range(min(height, screenY // tileSize)):
            if changed[x][y] or state[x][y] != 0:
                display.blit(tiles[state[x][y]], (x * tileSize, y*tileSize))
    pygame.display.update()

def checkRepeat():
    temp = 69420
    mod = int(10 ** 15 + 37)
    for x in range(width):
        for y in range(height):
            temp = (1337 * temp + state[x][y]) % mod
    
    if temp in cache:
        return True
    cache.append(temp)
    return False

def countChaos():
    if numStates <= 2:
        return 0
    curr = 0
    for x in range(width):
        for y in range(height):
            if state[x][y] >= 2:
                curr += 1
    return curr
init()
reset()

seen = [i for i in range(len(rules))]

lastTime = time.time()
totalTime = 0
mousePressed = False

async def loop():
    time.sleep(0.001)

    if mousePressed:
        print(pygame.mouse.get_pos())



while True:
    # asyncio.run(loop)
    if not mousePressed:
        updateBoard()
        updateScreen()
        curr += 1

        currTime = time.time()
        diff = currTime - lastTime
        totalTime += diff
        if showFps:
            print(1 / diff)
        
        pygame.time.wait(max(int((1000 / fps) - 1000 * diff), 0))
        lastTime = time.time()

        # reset = False
        if curr > 100:
            if checkRepeat():
                cache.clear()
                dead = True
        if curr > 10000:
            dead = True
        if dead:
            timer += 1
        if timer > 50:
            # currRule += 1
            # currRule %= len(rules)
            if randomRules:
                currRule = random.choice(seen)
                seen.remove(currRule)
                if len(seen) == 0:
                    seen = [i for i in range(len(rules))]
            # print(totalTime / curr)
            totalTime = 0
            reset()
    
    else:
        pygame.time.wait(1)
        x, y = pygame.mouse.get_pos()
        x = (x // tileSize) % width
        y = (y // tileSize) % height
        print(x, y)
        if state[x][y] != 1:
            state[x][y] = 1
            display.blit(tiles[state[x][y]], (x * tileSize, y*tileSize))
            pygame.display.update()
            for i in range(-1, 2):
                for j in range(-1, 2):
                    MikuLewds = x + i
                    KannaLewds = y + j
                    changed[MikuLewds%width][KannaLewds%height] = True
            
            curr = 0
            dead = False
            timer = 0
            cache.clear()

    # if len(cache) > maxCacheSize:
    #     cache.clear()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mousePressed = True
        elif event.type == pygame.MOUSEBUTTONUP:
            mousePressed = False