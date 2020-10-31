import cv2
import dlib
from game import rect_to_bb
from multiprocessing import Manager, Process
import multiprocessing as mp


def get_face_position(go, center):
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('./shape_predictor_5_face_landmarks.dat')
    cap = cv2.VideoCapture(0+cv2.CAP_DSHOW)
    while go:
        ret, img = cap.read()
        # handle err if ret is False
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        for rect in rects:
            x, y, w, h = rect_to_bb(rect)
            center.append([x, y])
            print(x, y)
    cap.release()
if __name__ == '__main__':
    ctx = mp.get_context('spawn')
    manager = Manager()
    center = manager.list()
    center.append([0, 0])
    print(list(center), center)
    proc = ctx.Process(target=get_face_position, args=(True, center))
    proc.start()
    while True:
        print(list(center)[-1])
    #get_face_position(True, center)
    

