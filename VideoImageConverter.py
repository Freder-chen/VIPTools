# -*- coding: utf-8 -*-
'''
@Time          : 20/10/02
@Author        : Freder Chen
@File          : VideoImageConverter.py
'''

import os
import cv2
import glob
import fire
from tqdm import tqdm


def mkdir(dir_):
    '''
    make folder if it's not exists

    dir_: folder path
    '''
    if not os.path.exists(dir_):
        os.makedirs(dir_)


class VideoImageConverter(object):
    """
    video image converter

    this class have two methods, video2Image and image2Video.
    `python3 VideoImageConverter.py video2Image -h` to see video2Image help.
    `python3 VideoImageConverter.py image2Video -h` to see image2Video help.
    """

    def video2Image(slef, videoPath, imgDir='out'):
        '''
        video to images

        videoPath: video path
        imgDir: temp path to save images
        '''
        mkdir(imgDir)
        vc = cv2.VideoCapture(videoPath)

        length = int(vc.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = vc.get(cv2.CAP_PROP_FPS)
        width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('In \'{}\', length: {}, fps: {}, width: {}, height: {}'.format(os.path.basename(videoPath), length, fps, width, height))

        pbar = tqdm(total=length, desc='video2Image')
        rval = vc.isOpened()
        c = 0
        while rval:
            rval, frame = vc.read()
            if not rval: break
            c += 1 # index of image
            cv2.imwrite(os.path.join(imgDir, '{}.jpg'.format(c)), frame)
            pbar.update(1)
        vc.release()

    def image2Video(self, imgDir, fps, videoPath='out.avi'):
        '''
        images to video

        imgDir: imges dir
        fps: create video's fps, it's better as same as origin video
        videoPath: generate video's path
        '''
        imgs = glob.glob(os.path.join(imgDir, '*.jpg'))
        if len(imgs) <= 0: return
        
        img = cv2.imread(imgs[0])
        height, width = img.shape[0], img.shape[1]
        videoWriter = cv2.VideoWriter(videoPath, cv2.VideoWriter_fourcc(*'MJPG'), fps, (width, height))
        for i in tqdm(sorted(imgs, key=lambda f: int(os.path.basename(os.path.normpath(f.split(".jpg", 1)[0])))), desc='image2Video'):
            img = cv2.imread(i)
            videoWriter.write(img)


if __name__ == '__main__':
    fire.Fire(VideoImageConverter)
