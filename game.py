from multiprocessing import Process, Manager
import numpy as np
import pygame as pg
from pygame.locals import *
import ecs
from ecs import Component, Event 
import cv2
import dlib
import random
import os
from PIL import Image
import time
from util import *


# initialize pygame constant parameters
pg.init()

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
GREEN = (0, 255, 0)
width = 1200
height = 800


# read in all sprites and animations
sprites, images, contours, meshes, centers = read_sprites(os.path.join(os.getcwd(), 'assets'))

screen = ecs.Entity(hid='screen')
screen.bind(Component(name='size', value=Vector2D(x=width, y=height-(height/10))))
screen.bind(Component(name='lower_bound', value=Vector2D(x=0, y=0)))
screen.bind(Component(name='frame', value=0))


player = create_movable_entity('player', Vector2D(0, 0), True, sprites['spaceship'], Vector2D(0, 0))
player.bind(Component(name='health', value=10))

# make rendering system
class RenderingSystem(ecs.System):
    def __init__(self, display):
        super().__init__()
        self.stars = []
        self.frame = 0
        self.display = display

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
                pg.draw.circle(self.display, star.color, (star.x, star.y), star.radius)  
        self.stars = updated_stars


    def render_health_bar(self):
        pass 
    
    def render_hud(self):
        rect_height = height/10
        rect_y = height- rect_height
        pg.draw.rect(self.display, (164, 164, 164), (0, rect_y, width, rect_height))

    def render_asteroids(self):
        pass

    def render_mail(self):
        pass

    def render_sprites(self):
        entities_to_render = ecs.Entity.filter('render', where=True)

        def rot_center(sprite, angle):
            orig_rect = sprite.get_rect()
            rot_image = pg.transform.rotate(sprite, angle)
            rot_rect = orig_rect.copy()
            rot_rect.center = rot_image.get_rect().center
            rot_image = rot_image.subsurface(rot_rect).copy()
            return rot_image

        for entity in entities_to_render:
            position = entity.components['position']
            sprite = entity.components['sprite']
            if 'contour_to_render' in entity.components:
                points = entity.components['contour_to_render']
                for i in range(len(points)-2):
                    pg.draw.line(self.display, 
                        GREEN, 
                        (int(points[i][0]), int(points[i][1])),
                        (int(points[i+1][0]), int(points[i+1][1])),
                        20
                        )

            #if 'rotation_vel' in entity.components:
            #    entity.components['rotation'] += entity.components['rotation_vel']
            #    sprite = rot_center(sprite, entity.components['rotation']*entity.components['rotation_dir'])
            #    #print(np.array(entity.components['contour_to_render']).shape)
            #    points = entity.components['contour_to_render']
            #    #print(points[-2:])
            #    for i in range(len(points)-2):
            #        #print(points[i])
            #        #if points[i][0] == 0: print('hello')
            #        pg.draw.line(self.display, 
            #            GREEN, 
            #            (int(points[i][0]), int(points[i][1])),
            #            (int(points[i+1][0]), int(points[i+1][1])),
            #            20
            #            )

            self.display.blit(sprite, (position.x, position.y))

    def update(self):
        self.render_background()
        self.render_sprites()
        self.render_hud()
        self.render_health_bar()


class AnimationSystem(ecs.System):
    pass


class CollisionSystem(ecs.System):

    def track_collision_contours(self):
        # get all collission enabled objects
        #entities = ecs.Entity.filter('toggle_collisions')
        #for entity in entities:
        #    #print(entity.components['toggle_collisions'])
        #    sprite = entity.components['sprite']
        #    rotation_magnitude = entity.components['rotation']
        #    contour = rotate_lines(entity.components['contour'], 
        #            sprite.get_rect().center, 
        #            np.radians(rotation_magnitude))
        #    mesh = entity.components['mesh']
        #    entity.components['contour_to_rotate'] = contour
        #    #print(rotation_magnitude)
            pass

    def update(self):
        self.track_collision_contours()


class ObjectManagementSystem(ecs.System):
    """
    handle creation and destruction of envelopes, enemies, and asteroid
    """
    def __init__(self, level):
        super().__init__()
        self.level = level

    def create_new_asteroid():
        pass

    def manage_asteroids(self, asteroids_in_window):
        screen_ent = ecs.Entity.filter('frame')[0]
        #print(screen_ent.components['frame'])
        # remove asteroids outside of window
        asteroids = ecs.Entity.filter('id', where='asteroid')
        #print(len(asteroids))
        max_asteroids = self.level+5+random.randint(0,3)
        if asteroids_in_window < max_asteroids and screen_ent.components['frame']%3==0:
            # create a new asteroid
            if random.uniform(0,1) <0.05:
                asteroid_sprites = list(filter(lambda a: 'asteroid' in a, sprites.keys()))
                weights = []
                for sprite in asteroid_sprites:
                    if 'small' in sprite: weights.append(0.6)
                    if 'medium' in sprite: weights.append(0.3)
                    if 'large' in sprite: weights.append(0.01)
                weights = np.array(weights)
                weights = weights/np.sum(weights)
                sprite = sprites[np.random.choice(asteroid_sprites, p=weights)]
                sprite_rect = sprite.get_rect()
                starting_vel = Vector2D(
                    x=random.randint(-2, 3),
                    y=random.randint(1, 3)
                    )
                sprite_key = random.choice(asteroid_sprites)
                asteroid = create_movable_entity(
                    'asteroid', 
                    Vector2D(random.randint(0, width)-sprite_rect[-2]-10, 0-sprite_rect[-1]-30), 
                    True, 
                    sprites[sprite_key], 
                    starting_vel)
                contour = contours[sprite_key]
                center = centers[sprite_key]
                init_position = asteroid.components['position']
                #sprite.get_rect().center, asteroid.components['rect'].center
                rect_center = asteroid.components['rect'].center
                for i, point in enumerate(contour):
                    #translate_to_sprite = 
                    contour[i] = [-(center[0]-rect_center[0])+point[0], -(center[1]-rect_center[1])+point[1]]
                    #print(contour[i][0], rect_center[0])
                    pass

                asteroid.bind(Component(name='contour', value=contour))
                asteroid.bind(Component(name='contour_to_render', value=contour))
                asteroid.bind(Component(name='mesh', value=meshes[sprite_key]))
                asteroid.bind(Component(name='mesh_to_render', value=meshes[sprite_key]))
                asteroid.bind(Component(name='allow_render', value=True))
                asteroid.bind(Component(name='time_created', value=time.time()))
                asteroid.bind(Component(name='rotation', value=0))
                
                asteroid.bind(Component(name='rotation_vel', value=0))
                #asteroid.bind(Component(name='rotation_vel', value=np.random.randint(1, 10)/10))
                asteroid.bind(Component(name='rotation_dir', value=np.random.choice([-1, 0, 1])))
                asteroid.bind(Component(name='toggle_collisions', value=True))


    def garbage_collection(self, tolerance=120):
        "delete objects that are out of screen and were created a sufficiently long time ago"
        asteroids_in_window = 0
        screen_entity = ecs.Entity.filter('id', where='screen')[0]
        screen_upper_bound = screen_entity.components['size']
        screen_lower_bound = screen_entity.components['lower_bound']

        asteroids = set(ecs.Entity.filter('id', where='asteroid'))
        envelopes = set(ecs.Entity.filter('id', where='envelope'))
        enemies = set(ecs.Entity.filter('id', where='enemy'))
        entities_to_check = list(asteroids|envelopes|enemies)
        for entity in entities_to_check:
            position = entity.components['position']
            rect = entity.components['rect']
            inside_window = position <= screen_upper_bound
            inside_window = inside_window and position >= screen_lower_bound
            time_condition = False
            if 'time_created' in entity.components:
                time_created = entity.components['time_created']
                time_elapsed = time.time()-time_created
                if time_elapsed > tolerance:
                    time_condition = True
                time_condition = True if time_elapsed > tolerance else False
            if inside_window: asteroids_in_window += 1
            if inside_window == False and time_condition == True:
                ecs.Entity.detach_entity(entity.uid)
        return asteroids_in_window

    def update(self):
        asteroids_in_window = self.garbage_collection(tolerance=120)
        #print('look here: ', asteroids_in_window)
        self.manage_asteroids(asteroids_in_window)

# movement system
class MovementSystem(ecs.System):
    def __init__(self):
        super().__init__()
    
    def rotate(self, sprite, angle):
        orig_rect = sprite.get_rect()
        rot_image = pg.transform.rotate(sprite, angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image

    def move_entities(self):
        screen_entity = ecs.Entity.filter('id', where='screen')[0]
        screen_upper_bound = screen_entity.components['size']
        screen_lower_bound = screen_entity.components['lower_bound']
        entities_to_move = ecs.Entity.filter('velocity')  
        for entity in entities_to_move:
            position = entity.components['position']
            rect = entity.components['rect']
            render = False
            if 'render' in entity.components.keys():
                render = entity.components['render']
            if render:
                velocity = entity.components['velocity']
                entity.components['position'] += velocity
                rect[0] += velocity.x
                rect[1] += velocity.y
                # assert that number of rendered asteroids equals number of asteroids with contour component
                if 'contour_to_render' in entity.components.keys():
                    points = entity.components['contour_to_render']
                    for i in range(len(points)-1):
                        entity.components['contour_to_render'][i][0] += velocity.x
                        entity.components['contour_to_render'][i][1] += velocity.y


            
            
                
    def update(self):
        self.move_entities()

def shape_to_np(shape, num_points, dtype):
    coords = np.zeros((num_points, 2), dtype=dtype)
    for i in range(0, num_points):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def rect_to_bb(rect):
    x = rect.left()
    y = rect.top()

    return (x, y, rect.right()-x, rect.bottom()-y)

def get_face_position(go, center):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('./shape_predictor_5_face_landmarks.dat')
    cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    while go.value>0:
        ret, img = cap.read()
        # handle err if ret is False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            x, y, w, h = rect_to_bb(rect)
            shape = predictor(gray, rect)
            shape_np = shape_to_np(shape, 5, "int")
            center_x, center_y = shape_np[4]
            relative_x = (img.shape[1]-center_x)/img.shape[1]
            relative_y = center_y/img.shape[0]
            center.append((relative_x, relative_y))
    cap.release()

if __name__ == '__main__':

    gameDisplay = pg.display.set_mode((width, height), RESIZABLE)
    renderer = RenderingSystem(gameDisplay)
    mover = MovementSystem()
    objectmanager = ObjectManagementSystem(level=1)
    collisionmanager = CollisionSystem()
    #print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('./shape_predictor_5_face_landmarks.dat')
    manager = Manager()
    center = manager.list()
    go = manager.Value("int", 1)
    center.append([0, 0])
    proc = Process(target=get_face_position, args=(go,center))
    proc.start()
    #center.extend([0, 0])
    pg.display.update()
    clock = pg.time.Clock()
    game_exit = False
    #cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    while not game_exit:
        gameDisplay.fill(black)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                #cap.release()
                game_exit = True
        player_pos = center[-1]
        player.components['position'].x = player_pos[0]*width
        player.components['position'].y = player_pos[1]*height - 200 # calibrate this value so that the player starts in the center
        ecs.System.update_all()
        pg.display.update()
        clock.tick(60)
        screen.components['frame'] += 1
    go.value = False
    proc.join()
    pg.quit()
    quit()


