'''

'''

import sys
import ffmpeg
import numpy as np


class VideoCapture:
    """
    VideoCapture with cuda by ffmpeg
    """
    def __init__(self, uri, gpu_id=None, quiet=False, out_fps=None):
        self.stopped = False
        self.quiet = quiet
        
        self.video_info = self._get_video_info(uri)
        self.width = int(self.video_info['width']) if 'width' in self.video_info.keys() else None
        self.height = int(self.video_info['height']) if 'height' in self.video_info.keys() else None
        self.fps = eval(self.video_info['avg_frame_rate']) if 'avg_frame_rate' in self.video_info.keys() else None
        self.frame_count = int(self.video_info['nb_frames']) if 'nb_frames' in self.video_info.keys() else None

        input_args = {}
        if gpu_id:
            input_args.update({
                'hwaccel': 'nvdec',
                'hwaccel_device': str(gpu_id),
            })
        self.cap_process = self._ffmpeg_capture(uri, out_fps, input_args)

    def read(self, type=None):
        type = type or 'bytes'
        if type not in ['bytes', 'numpy']:
            raise ValueError('The type option can only be \'bytes\' and \'numpy\'.')

        # Note: RGB24 == 3 bytes per pixel.
        frame_size = self.width * self.height * 3
        frame_bytes = self.cap_process.stdout.read(frame_size)
        if len(frame_bytes) == 0:
            self.release()
            return None

        assert len(frame_bytes) == frame_size        

        if type == 'bytes':
            frame = frame_bytes
        elif type == 'numpy':
            frame = np.frombuffer(frame_bytes, np.uint8).reshape([self.height, self.width, 3])[:, :, ::-1] # RGB format
        else:
            raise ValueError('The type option can only be \'bytes\' and \'numpy\'.')
        return frame

    def is_opened(self):
        return not self.stopped
    
    def release(self):
        if self.is_opened() and hasattr(self, 'cap_process'):
            self.cap_process.terminate()
        self.stopped = True

    def _ffmpeg_capture(self, uri, out_fps=None, input_args={}, output_args={}):
        stream = ffmpeg.input(uri, **input_args)
        if out_fps:
            stream = stream.filter('fps', fps=out_fps, round='up')
        process = (
            stream
            .output('pipe:', format='rawvideo', pix_fmt='rgb24')
            .run_async(pipe_stdout=True, quiet=self.quiet)
        )
        return process

    def _get_video_info(self, uri):
        try:
            probe = ffmpeg.probe(uri) # can raise ffmpeg.Error
        except ffmpeg.Error as e:
            raise ValueError('URI cannot be connected or incorrect: {}'.format(uri))
        video_info = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
        if video_info is None:
            raise ValueError('No video stream found in {}.'.format(uri), file=sys.stderr)
        return video_info


if __name__ == '__main__':
    import os
    import time
    from tqdm import tqdm
    from multiprocessing import Process

    def read_vedio(idx, uri, gpu_id=0):
        print('Run task %s (%s)...' % (idx, os.getpid()))
        start = time.time()

        cap = VideoCapture(uri, gpu_id=gpu_id, quiet=True)
        pbar = tqdm(total=cap.frame_count, desc='Bar {}'.format(idx))
        i = 0
        while cap.is_opened():
            frame = cap.read(type='numpy')
            if frame is None: continue
            
            # do process
            import cv2
            path = f'./examples/{idx}'
            if not os.path.exists(path):
                os.makedirs(path)
            cv2.imwrite(f'{path}/{i}.jpg', frame)

            pbar.update(1)
            i += 1
        cap.release()
        end = time.time()
        print('Task %s runs %0.2f seconds.' % (idx, (end - start)))
    
    uris = [
        # uris
    ]

    P = [Process(target=read_vedio, args=(i, uris[i], None)) for i in range(len(uris))]
    for p in P: p.start()
    for p in P: p.join()

    print('All subprocesses done.')
