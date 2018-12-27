import pygame
import numpy as np
import cv2
import imutils.imutils
from imutils.imutils import face_utils
import dlib
from scipy.spatial import distance as dist
from PIL import Image
import random

# initialize pygame constant parameters
pygame.init()

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
width = 650
height = 300

# initialize game display
gameDisplay = pygame.display.set_mode((width, height))
pygame.display.set_caption('InterGalactic Mailman')

# load images
IMG = Image.open('small_spaceship.png')
METEOR = Image.open('fixed_meteor.png')
ENVELOPE = Image.open('envelope.png')
SPACE = Image.open('space.png')


mode = IMG.mode
size = IMG.size
data = IMG.tobytes()

space_ship = pygame.image.fromstring(data, size, mode)

mode = METEOR.mode
size = METEOR.size
data = METEOR.tobytes()

meteor = pygame.image.fromstring(data, size, mode)

mode = ENVELOPE.mode
size = ENVELOPE.size
data = ENVELOPE.tobytes()

envelope = pygame.image.fromstring(data, size, mode)
envelope = pygame.transform.scale(envelope, (75, 50))

mode = SPACE.mode
size = SPACE.size
data = SPACE.tobytes()

space = pygame.image.fromstring(data, size, mode)
space = pygame.transform.scale(space, (width, height))



# define all objects 
def ship(x, y):
    gameDisplay.blit(space_ship, (x - 90, y - 50))


def obst1(x, y):
    gameDisplay.blit(meteor, (x, y))
    return x, y


def env(x, y):
    gameDisplay.blit(envelope, (x, y))
    return x, y


# update display
pygame.display.update()
game_exit = False


# load facial landmark detector
print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_5_face_landmarks.dat')

# set initial movement for meteors
x1 = 0
y1 = 100
deltax = random.randint(1, 10)
deltay = random.randint(1, 10)

x2 = 600
y2 = 200
deltax2 = random.randint(-10, -1)
deltay2 = random.randint(-10, -1)

x3 = 100
y3 = 100
deltax3 = random.randint(10, 20)
deltay3 = random.randint(-10, 0)

# set intial movement for envelopes
x4 = 0
y4 = random.randint(10, 100)
deltax4 = random.randint(10, 20)
deltay4 = random.randint(10, 15)

x5 = 0
y5 = random.randint(10, 100)
deltax5 = random.randint(10, 20)
deltay5 = random.randint(10, 20)
score = 0

# make random values for meteor movement
random_xvals = []
random_yvals = []
for i in range(10):
    random_xvals.append(random.randint(0, width - 1))

for i in range(10):
    random_yvals.append(random.randint(0, height - 1))

# load music
bbox = pygame.mixer.music.load('ultrafc.wav')

# main game loop
while not game_exit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_exit = True

    # play music
    pygame.mixer.music.play(loops=-1)

    # begin video capture
    cap = cv2.VideoCapture(0)
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                game_exit = True

        #read new image
        ret, img = cap.read()

        # resize image
        img = imutils.imutils.resize(img, width=width)

        #convert to gray scale and detect face in image
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        # loop over the face detections
        for rect in rects:

            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            
            center = shape[4]
            
            # draw background
            gameDisplay.blit(space, [0, 0])

            # make hitboxes around ship
            hitbox_ship1 = pygame.draw.rect(
                gameDisplay, black,
                [width - center[0] - 77+50, center[1] - 0-15, 70, 10])

            hitbox_ship2 = pygame.draw.rect(
                gameDisplay, black,
                [width - center[0] - 71+50, center[1] - 10-15, 60, 10])

            hitbox_ship3 = pygame.draw.rect(
                gameDisplay, black,
                [width - center[0] - 67+50, center[1] - 20-15, 50, 10])

            hitbox_ship4 = pygame.draw.rect(
                gameDisplay, black,
                [width - center[0] - 62+50, center[1] - 30-15, 40, 10])

            hitbox_ship5 = pygame.draw.rect(
                gameDisplay, black,
                [width - center[0] - 57, center[1] - 40, 30, 10])
            ship(width - center[0]+50, center[1]-15)

            # handle interactions for meteor 1
            if x1 < width or y1 < height or x1 > 0 or y1 > 0:
                # make hitboxes around meteor
                hitbox_meteor1 = pygame.draw.rect(gameDisplay, black,
                                                  [x1 + 15, y1, 47, 49])
                # check for collisions
                p1 = hitbox_meteor1.colliderect(hitbox_ship5)
                p2 = hitbox_meteor1.colliderect(hitbox_ship4)
                p3 = hitbox_meteor1.colliderect(hitbox_ship3)
                p4 = hitbox_meteor1.colliderect(hitbox_ship2)
                p5 = hitbox_meteor1.colliderect(hitbox_ship1)

                # if collision is true remove meteor from screen and create it in new location
                if p1 == 1 or p2 == 1 or p3 == 1 or p4 == 1 or p5 == 1:
                    x1 = random.choice(random_xvals)
                    y1 = 0
                    if x1 > width / 2:
                        deltax = random.randint(-10, 0)
                        deltay = random.randint(1, 10)
                    if x1 < width / 2:
                        deltax = random.randint(1, 10)
                        deltay = random.randint(1, 10)
                    
                    # update score
                    score -= 1
                    scr = str(score)
                    pygame.display.set_caption("Score: " + scr)

                # update position of meteor
                x1, y1 = obst1(x1 + deltax, y1 + deltay)

                # if meteor moves off screen create it in new location
                if x1 > width or y1 > height or x1 < 0 or y1 < 0:
                    x1 = random.choice(random_xvals)
                    y1 = 0
                    if x1 > width / 2:
                        deltax = random.randint(-10, 0)
                        deltay = random.randint(1, 10)
                    if x1 < width / 2:
                        deltax = random.randint(1, 10)
                        deltay = random.randint(1, 10)

            # handle interactions for meteor 2
            if x2 < width or y2 < height or x2 > 0 or y2 > 0:
                # make hitboxes around meteor
                hitbox_meteor2 = pygame.draw.rect(gameDisplay, black,
                                                  [x2 + 15, y2, 47, 49])
                # check for collisions
                p1 = hitbox_meteor2.colliderect(hitbox_ship5)
                p2 = hitbox_meteor2.colliderect(hitbox_ship4)
                p3 = hitbox_meteor2.colliderect(hitbox_ship3)
                p4 = hitbox_meteor2.colliderect(hitbox_ship2)
                p5 = hitbox_meteor2.colliderect(hitbox_ship1)

                # if collision is true remove meteor from screen and create it in new location
                if p1 == 1 or p2 == 1 or p3 == 1 or p4 == 1 or p5 == 1:
                    x2 = random.choice(random_xvals)
                    y2 = 0                                            
                    if x2 > width / 2:
                        deltax2 = random.randint(-10, 0)
                        deltay2 = random.randint(1, 10)
                    if x2 < width / 2:
                        deltax2 = random.randint(1, 10)
                        deltay2 = random.randint(1, 10)
                    # update score
                    score -= 1
                    scr = str(score)
                    pygame.display.set_caption("Score: " + scr)
                # update position of meteor
                x2, y2 = obst1(x2 + deltax2, y2 + deltay2)
                # if meteor moves off screen create it in new location
                if x2 > width or y2 > height or x2 < 0 or y2 < 0:
                    x2 = random.choice(random_xvals)
                    y2 = 0
                    if x2 > width / 2:
                        deltax2 = random.randint(-10, 0)
                        deltay2 = random.randint(-10, 10)
                    if x2 < width / 2:
                        deltax = random.randint(1, 10)
                        deltay = random.randint(-10, 1)
                

            # handle interactions for meteor 3
            if x3 < width or y3 < height or x3 > 0 or y3 > 0:
                # make hitboxes around meteor
                hitbox_meteor3 = pygame.draw.rect(gameDisplay, black,
                                                  [x3 + 15, y3, 47, 49])
                # check for collisions
                p1 = hitbox_meteor3.colliderect(hitbox_ship5)
                p2 = hitbox_meteor3.colliderect(hitbox_ship4)
                p3 = hitbox_meteor3.colliderect(hitbox_ship3)
                p4 = hitbox_meteor3.colliderect(hitbox_ship2)
                p5 = hitbox_meteor3.colliderect(hitbox_ship1)
                
                # if collision is true remove meteor from screen and create it in new location
                if p1 == 1 or p2 == 1 or p3 == 1 or p4 == 1 or p5 == 1:
                    x3 = random.choice(random_xvals)
                    y3 = 0
                    if x3 > width / 2:
                        deltax3 = random.randint(-10, 0)
                        deltay3 = random.randint(1, 10)
                    if x3 < width / 2:
                        deltax3 = random.randint(1, 10)
                        deltay3 = random.randint(1, 10)
                    
                    # update score
                    score -= 1
                    scr = str(score)
                    pygame.display.set_caption("Score: " + scr)
                
                # update position of meteor
                x3, y3 = obst1(x3 + deltax3, y3 + deltay3)
                # if meteor moves off screen create it in new location
                if x3 > width or y3 > height or x3 < 0 or y3 < 0:
                    x3 = random.choice(random_xvals)
                    y3 = 0
                    if x3 > width / 2:
                        deltax3 = random.randint(-10, 0)
                        deltay3 = random.randint(1, 10)
                    if x3 < width / 2:
                        deltax3 = random.randint(1, 10)
                        deltay3 = random.randint(1, 10)

            # handle interactions for envelope 1
            if x4 < width or y4 < height or x4 > 0 or y4 > 0:
                # make hitbox around envelope
                hitbox_env1 = pygame.draw.rect(gameDisplay, black,
                                               [x4 + 15, y4, 47, 49])
                # check for collisions with ship
                p1 = hitbox_env1.colliderect(hitbox_ship5)
                p2 = hitbox_env1.colliderect(hitbox_ship4)
                p3 = hitbox_env1.colliderect(hitbox_ship3)
                p4 = hitbox_env1.colliderect(hitbox_ship2)
                p5 = hitbox_env1.colliderect(hitbox_ship1)

                # if collision is true remove envelope from screen and create it in new location
                if p1 == 1 or p2 == 1 or p3 == 1 or p4 == 1 or p5 == 1:
                    x4 = random.choice(random_xvals)
                    y4 = 0
                    if x4 > width / 2:
                        deltax4 = random.randint(-10, 0)
                        deltay4 = random.randint(1, 10)
                    if x4 < width / 2:
                        deltax4 = random.randint(1, 10)
                        deltay4 = random.randint(1, 10)
                    score += 1
                    scr = str(score)
                    pygame.display.set_caption("Score: " + scr)
                # update position of envelope
                x4, y4 = env(x4 + deltax4, y4 + deltay4)
                # if envelope moves off screen create it in new location
                if x4 > width or y4 > height or x4 < 0 or y4 < 0:
                    x4 = random.choice(random_xvals)
                    y4 = 0
                    if x4 > width / 2:
                        deltax4 = random.randint(-10, 0)
                        deltay4= random.randint(1, 10)
                    if x3 < width / 2:
                        deltax4 = random.randint(1, 10)
                        deltay4 = random.randint(1, 10)
            
            # handle interactions for envelope 2
            if x5 < width or y5 < height or x5 > 0 or y5 > 0:
                # make hitbox around envelope 
                hitbox_env1 = pygame.draw.rect(gameDisplay, black,
                                               [x5 + 15, y5, 47, 49])
                # check for collisions
                p1 = hitbox_env1.colliderect(hitbox_ship5)
                p2 = hitbox_env1.colliderect(hitbox_ship4)
                p3 = hitbox_env1.colliderect(hitbox_ship3)
                p4 = hitbox_env1.colliderect(hitbox_ship2)
                p5 = hitbox_env1.colliderect(hitbox_ship1)
                # if collision is true remove envelope from screen and create it in new location
                if p1 == 1 or p2 == 1 or p3 == 1 or p4 == 1 or p5 == 1:
                    x5 = random.choice(random_xvals)
                    y5 = 0
                    if x5 > width / 2:
                        deltax5 = random.randint(-10, 0)
                        deltay5 = random.randint(1, 10)
                    if x4 < width / 2:
                        deltax5 = random.randint(1, 10)
                        deltay5 = random.randint(1, 10)
                    score += 1
                    scr = str(score)
                    pygame.display.set_caption("Score: " + scr)
                # update position of collisions
                x5, y5 = env(x5 + deltax5, y5 + deltay5)
                # if envelope moves off screen create it in new location 
                if x5 > width or y5 > height or x5 < 0 or y5 < 0:
                    x5 = random.choice(random_xvals)
                    y5 = 0
                    if x5 > width / 2:
                        deltax4 = random.randint(-10, 0)
                        deltay4= random.randint(1, 10)
                    if x5 < width / 2:
                        deltax4 = random.randint(1, 10)
                        deltay4 = random.randint(1, 10)


            # update display
            pygame.display.update()

pygame.quit()
quit()
