# -*- coding: utf-8 -*-
'''
@Time          : 21/01/30
@Author        : Freder Chen
@File          : video_processer.py
'''

import os
import cv2
import glob
from tqdm import tqdm
from .utils import mkdir


class VideoProcesser(object):
    """
    video processer

    the class has two methods, avi2mp4 and crop_video.
    """

    def _get_video_writer(self, filename, type, fps, size):
        return cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*type), fps, size)
    

    def avi2mp4(self, avi_filename, mp4_filename):
        '''
        avi to mp4

        avi_filename: source filename
        mp4_filename: dest   filename
        '''
        video_capture = cv2.VideoCapture(avi_filename)
        length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(mp4_filename, length, fps, (width, height))

        mkdir(os.path.dirname(mp4_filename))
        
        video_writer = self._get_video_writer(mp4_filename, 'mp4v', fps if fps not in [float('inf'), float('nan')] else 20, (width, height))
        pbar = tqdm(total=length, desc='avi2mp4')
        while video_capture.isOpened():
            rval, frame = video_capture.read()
            if not rval: break
            video_writer.write(frame)
            pbar.update(1)
        video_capture.release()
        video_writer.release()


    def crop_video(self, video_filename, crop_filename, start_time=None, end_time=None):
        '''
        crop video

        start_time defaults to 0, end_time defaults to length,
        and the unit of time is seconds.
        '''

        # load video info
        video_capture = cv2.VideoCapture(video_filename)
        length = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_capture.get(cv2.CAP_PROP_FPS)
        width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # judge video format
        if crop_filename and isinstance(crop_filename, str) and len(crop_filename) > 4:
            if crop_filename[-3:].lower() == 'mp4':
                type_ = 'mp4v'
            elif crop_filename[-3:].lower() == 'avi':
                type_ = 'MJPG'
            else:
                raise ValueError(f'crop_filename only supports .avi and .mp4.')
        else:
            raise ValueError(f'crop_filename error: {crop_filename}')

        mkdir(os.path.dirname(crop_filename))

        # calculate start frame and end frame
        # start_frame defaults to 0,
        # end_frame defaults to length.
        start_frame = int((start_time or 0) * fps)
        end_frame = int((end_time or (length / fps)) * fps)

        # jump to video start frame
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        # write to croped video
        video_writer = self._get_video_writer(crop_filename, type_, fps, (width, height))
        pbar = tqdm(total=end_frame - start_frame, desc='crop {} to {}'.format(os.path.basename(video_filename), os.path.basename(crop_filename)))
        for _ in range(start_frame, end_frame):
            if video_capture.isOpened():
                rval, frame = video_capture.read()
                if not rval: break
                video_writer.write(frame)
                pbar.update(1)

        video_capture.release()
        video_writer.release()
