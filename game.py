import pygame as pg
from pygame.locals import *
import ecs
from ecs import Component, Event 
import cv2
import dlib
import random
import os
from PIL import Image

class Vector2D:
    def __init__(self, x, y, **kwargs):
        self.x = x
        self.y = y
        for key, value in kwargs.items():
            setattr(self, key, value)


    def __add__(self, vec):
        return Vector2D(self.x + vec.x, self.y + vec.y)

    def __radd__(self, vec):
        return Vector2D(self.x + vec.x, self.y + vec.y)

    def __sub__(self, vec):
        return Vector2D(self.x - vec.x, self.y - vec.y)

    def __eq__(self, vec):
        try: return self.x == vec.x and self.y == vec.y
        except: return False

    def __gt__(self, vec):
        try: return self.x > vex.x and self.y > vec.y
        except: return False

    def __ge__(self, vec):
        return self.__eq__(vec) or self.__gt__(vec)

    def __lt__(self, vec):
        try: return self.x < vec.x and self.y < vec.y
        except: return False

    def __le__(self, vec):
        return self.__eq__(vec) or self.__lt__(vec)


# initialize pygame constant parameters
pg.init()

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
width = 650
height = 300
sprites = {}


# read in all sprites and animations
def read_sprites(asset_dir):
    sprite_paths = os.listdir(asset_dir)
    for sprite in sprite_paths:
        path = os.path.join(asset_dir, sprite)
        img = Image.open(path)
        mode = img.mode
        size = img.size
        data = img.tobytes()
        sprites[sprite.split('.')[0]] = pg.image.fromstring(data, size, mode)
        print(sprite)

read_sprites(os.path.join(os.getcwd(), 'assets'))

# initialize game display
gameDisplay = pg.display.set_mode((width, height), RESIZABLE)
pg.display.set_caption('InterGalactic Mailman')


print("[INFO] loading facial landmark predictor...")
detector = dlib.get_frontal_face_detector()


player = ecs.Entity(hid='player')
player.bind(Component(name='position', value=Vector2D(x=0, y=0)))
player.bind(Component(name='render', value=True))
player.bind(Component(name='health', value=10))
player.bind(Component(name='sprite', value=sprites['spaceship']))
player.bind(Component(name='velocity', value=Vector2D(x=0, y=1)))

screen = ecs.Entity(hid='screen')
screen.bind(Component(name='size', value=Vector2D(x=width, y=height)))
screen.bind(Component(name='lower_bound', value=Vector2D(x=0, y=0)))

# make rendering system
class RenderingSystem(ecs.System):
    def __init__(self):
        super().__init__()
        self.stars = []
        self.frame = 0

    def render_background(self):
        speed = ecs.Entity.filter('id', where='player')[0].components['velocity'].y + 4 
        self.frame += 1
        frame_spacing = 40
        # create new stars
        if self.frame % frame_spacing == 0:
            for i in range(random.randint(0, 10)):
                star_vec = Vector2D(x=random.randint(0, width), y=random.randint(-frame_spacing, 0), radius=random.choice([1,2,3]), color=tuple(map(lambda a: a-random.randint(0, 50), white)))
                self.stars.append(star_vec)

        # move stars and delete ones that are no longer in the screen
        updated_stars = []
        for star in self.stars:
            if star.y < height+star.radius:
                star.y += speed - star.radius + random.randint(0,1)
                updated_stars.append(star)
                pg.draw.circle(gameDisplay, star.color, (star.x, star.y), star.radius)  
        self.stars = updated_stars


    def render_health_bar(self):
        pass 
    
    def render_hud(self):
        rect_height = height/10
        rect_y = height- rect_height
        pg.draw.rect(gameDisplay, (164, 164, 164), (0, rect_y, width, rect_height))

    def render_asteroids(self):
        pass

    def render_mail(self):
        pass

    def render_sprites(self):
        entities_to_render = ecs.Entity.filter('render', where=True)
        for entity in entities_to_render:
            position = entity.components['position']
            sprite = entity.components['sprite']
            gameDisplay.blit(sprite, (position.x, position.y))

    def update(self):
        self.render_background()
        self.render_hud()
        self.render_health_bar()
        self.render_sprites()


class AnimationSystem(ecs.System):
    pass

class CollisionSystem(ecs.System):
    pass


class ObjectSystem(ecs.System):
    """
    handle creation and destruction of envelopes, enemies, and meteors
    """
    def __init__(self, level):
        pass

# movement system
class MovementSystem(ecs.System):
    def __init__(self):
        super().__init__()
        self.subscribe('move')

    def move_entities(self):
        screen_entity = ecs.Entity.filter('id', where='screen')[0]
        screen_upper_bound = screen_entity.components['size']
        screen_lower_bound = screen_entity.components['lower_bound']
        entities_to_move = ecs.Entity.filter('velocity')  
        for entity in entities_to_move:
            # player is not allowed to leave screen, other objects are
            inside_window = entity.components['position'] < screen_upper_bound
            inside_window = inside_window and entity.components['position'] >= screen_lower_bound
            print(inside_window)
            if entity.hid != 'player' or not inside_window: 
                entity.components['position'] += entity.components['velocity']
                
    def update(self):
        self.move_entities()

renderer = RenderingSystem()
mover = MovementSystem()

pg.display.update()
clock = pg.time.Clock()
game_exit = False
while not game_exit:
    gameDisplay.fill(black)
    cap = cv2.VideoCapture(0)
    for event in pg.event.get():
        if event.type == pg.QUIT:
            cap.release()
            game_exit = True
    ecs.System.update_all()
    pg.display.update()
    clock.tick(60)
    #ret, img = cap.read() 
pg.quit()
quit()


