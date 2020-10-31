import os
import pygame as pg
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import cv2
from scipy.spatial import Delaunay

def drop_alpha(img):
    width, height, channels = img.shape
    new_img = np.zeros((width,height,3))
    for i in range(width):
        for j in range(height):
            r, g, b, a = img[i, j]
            if a == 0: 
                if r>0 or g>0 or b>0:
                    new_img[i, j] = [0, 0, 0]
            else: new_img[i, j] = [r, g, b]

    return new_img.astype(np.uint8)

def get_triangle_area(x, y):
    area=0.5*( (x[0]*(y[1]-y[2])) + (x[1]*(y[2]-y[0])) + (x[2]*(y[0]-y[1])))
    return int(area)


def prune_mesh(mesh, contour, threshold=10):
    """
    remove triangles with small area from mesh
    """
    points = contour[mesh.simplices]
    areas = np.array([get_triangle_area(p[:, 0], p[:, 1])>threshold for p in points])
    ind = np.squeeze(np.argwhere(areas==True))
    return mesh.simplices[ind]

# read in all sprites and animations
def read_sprites(asset_dir):
    sprites = {}
    images = {}
    contours = {}
    meshes = {}
    sprite_paths = os.listdir(asset_dir)
    for sprite in sprite_paths:
        path = os.path.join(asset_dir, sprite)
        img = Image.open(path)
        img_np = drop_alpha(np.array(img))
        mode = img.mode
        size = img.size
        data = img.tobytes()
        key = sprite.split('.')[0]
        sprite = pg.image.fromstring(data, size, mode)
        sprites[key] = sprite 
        images[key] = img_np
        rect = sprite.get_rect() 
        center = [rect[0]+(rect[-2]/2), rect[1]+(rect[-1]/2)]
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        blur = cv2.blur(gray, (3,3))
        ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
        _, cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt_max_ind = np.argmax([cv2.contourArea(cnt) for cnt in cnts])
        cnt = np.squeeze(cnts[cnt_max_ind])
        contours[key] = cnt
        mesh = Delaunay(cnt)
        mesh = prune_mesh(mesh, cnt, threshold=10)
        meshes[key] = mesh
    return sprites, images, contours, meshes


sprites, images, contours, meshes = read_sprites(os.path.join(os.getcwd(), 'assets'))
#print(list(sprites.keys()))
key = 'asteroid_small'
#image = images[key]
#rect = sprites[key].get_rect()
#center = [rect[0]+(rect[-2]/2), rect[1]+(rect[-1]/2)]
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#blur = cv2.blur(gray, (3,3))
#ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
#im2, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#cnt_max_ind = np.argmax([cv2.contourArea(cnt) for cnt in contours])
#print(len(contours))
#cnt = np.squeeze(contours[cnt_max_ind])
#mesh = Delaunay(cnt)
#mesh = prune_mesh(mesh, cnt, threshold=50)
#fig,ax = plt.subplots(1)
#odd_ind = np.arange(1, cnt.shape[1]-1, 2)
#thing = cnt[1::20, :] 
#print(thing.shape)
#
#deg= np.radians(30)
def rotate_lines(points, around, deg):
    rotated_points = []
    translate_to_point = np.array([[1, 0, around[0]], [0, 1, around[1]], [0, 0, 1]])
    translate_to_origin = np.array([[1, 0, -around[0]], [0, 1, -around[1]], [0, 0, 1]])
    rotation_matrix = np.array([[np.cos(deg), -np.sin(deg), 0], [np.sin(deg), np.cos(deg), 0], [0, 0, 1]])
    for point in points: 
        point = [*point, 1]
        to_origin = np.dot(translate_to_origin, point)
        rotate = np.dot(rotation_matrix, to_origin)
        to_point = np.dot(translate_to_point, rotate)
        rotated_points.append(to_point)
    return np.array(rotated_points)
        
def detect_collision(obj1, obj2):
    pass

#print(center)
cnt = contours[key]
#rotated_cnt = rotate_lines(cnt, center, np.radians(90)) 
fig, ax = plt.subplots()
ax.imshow(images[key])
#ax.plot(cnt[1::20, 0], cnt[1::20, 1],color='blue')
ax.plot(cnt[:, 0], cnt[:, 1],color='blue')
#ax.plot(rotated_cnt[1::20, 0], rotated_cnt[1::20, 1], color='purple')
ax.triplot(cnt[:, 0], cnt[:, 1], meshes[key], color='red')
plt.show()

