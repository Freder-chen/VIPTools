# -*- coding: utf-8 -*-
'''
@Time          : 20/10/02
@Author        : Freder Chen
@File          : video_image_converter.py
'''

import os
import cv2
import glob
from tqdm import tqdm
from .utils import mkdir


class VideoImageConverter(object):
    """
    video image converter

    The class have two methods, video2images and images2video.
    """

    def _get_video_writer(self, filename, type, fps, size):
        return cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*type), fps, size)


    def video2images(slef, video_filename, imgdir='out'):
        '''
        video to images

        video_filename: video file
        imgdir: temp path to save images
        '''
        mkdir(imgdir)
        video_capture = cv2.VideoCapture(video_filename)
        length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print('In \'{}\', length: {}, fps: {}, width: {}, height: {}'.format(os.path.basename(video_filename), length, fps, width, height))

        pbar = tqdm(total=length, desc='video2image')
        c = 0
        while video_capture.isOpened():
            rval, frame = video_capture.read()
            if not rval: break
            # index of image
            c += 1
            # and img index start from 1.
            cv2.imwrite(os.path.join(imgdir, '{}.jpg'.format(c)), frame)
            pbar.update(1)
        video_capture.release()


    def images2video(self, imgdir, video_filename='out.avi', fps=20):
        '''
        images to video

        imgdir: imges dir
        video_filename: generate video's filename
        fps: create video's fps, it's better as same as origin video
        '''
        imgs = glob.glob(os.path.join(imgdir, '*.jpg'))
        if len(imgs) <= 0: return
        
        img = cv2.imread(imgs[0])
        height, width = img.shape[0], img.shape[1]
        # judge video format
        if video_filename and isinstance(video_filename, str) and len(video_filename) > 4:
            if video_filename[-3:].lower() == 'mp4':
                type_ = 'mp4v'
            elif video_filename[-3:].lower() == 'avi':
                type_ = 'MJPG'
            else:
                raise ValueError('video_filename only supports .avi and .mp4.')
        else:
            raise ValueError(f'video_filename is not str or too short: {video_filename}')

        videoWriter = self._get_video_writer(video_filename, type_, fps, (width, height))
        for i in tqdm(sorted(imgs, key=lambda f: int(os.path.basename(os.path.normpath(f.split(".jpg", 1)[0])))), desc='image2video'):
            videoWriter.write(cv2.imread(i))
        videoWriter.release()
