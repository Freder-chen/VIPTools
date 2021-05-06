'''
    Copyed from https://github.com/jrosebr1/imutils/blob/master/imutils/video/filevideostream.py
    Alter:
        cv2.VideoCapture to self's .video_capture.VideoCapture
'''

import sys
import time
import warnings
from threading import Thread

# import the Queue class from Python 3
if sys.version_info >= (3, 0):
    from queue import Queue
# otherwise, import the Queue class for Python 2.7
else:
    from Queue import Queue

try:
    from .video_capture import VideoCapture
except ModuleNotFoundError:
    from video_capture import VideoCapture


class VideoStream:
    def __init__(self, uri, transform=None, queue_size=128, gpu_id=None, quiet=True, read_type='numpy'):
        # initialize the video capture along with the boolean
        # used to indicate if the thread should be stopped or not
        self.cap = VideoCapture(uri, gpu_id=gpu_id, quiet=quiet)
        self.stopped = False
        self.transform = transform
        self.read_type = read_type

        # initialize queue and thread
        self.Q = Queue(maxsize=queue_size)
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped: break

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                frame = self.cap.read(type=self.read_type)

                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if frame is None:
                    self.stopped = True
                    
                # if there are transforms to be done, might as well
                # do them on producer thread before handing back to
                # consumer thread. ie. Usually the producer is so far
                # ahead of consumer that we have time to spare.
                #
                # Python is not parallel but the transform operations
                # are usually OpenCV native so release the GIL.
                #
                # Really just trying to avoid spinning up additional
                # native threads and overheads of additional
                # producer/consumer queues since this one was generally
                # idle grabbing frames.
                if self.transform:
                    frame = self.transform(frame)

                # add the frame to the queue
                self.Q.put(frame)
            else:
                time.sleep(0.1)  # Rest for 10ms, we have a full queue
        self.cap.release()

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of stream.
    def running(self):
        return self.more() or not self.stopped

    def more(self):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        tries = 0
        while self.Q.qsize() == 0 and not self.stopped and tries < 5:
            time.sleep(0.1)
            tries += 1
        return self.Q.qsize() > 0

    def stop(self):
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
        # indicate that the thread should be stopped
        self.stopped = True


class MultiVideoStream(object):
    def __init__(self, source_dicts, transform=None, queue_size=32, quiet=True, read_type='numpy'):
        '''
            source_dicts: [{'uri': 'xxxx', 'gpu_id': 0}, ...]
        '''
        super(MultiVideoStream, self).__init__()
        # initialize the video capture along with the boolean
        # used to indicate if the thread should be stopped or not
        self.streams = []
        for source_dict in source_dicts:
            stream = VideoStream(source_dict['uri'], gpu_id=source_dict['gpu_id'], read_type='numpy').start()
            if not stream.running():
                raise ValueError('Cannot open capture: {}.'.format(source_dict['uri']))
            self.streams.append(stream)
        self.streams_count = len(self.streams)
        
        self.streams_stopped = [False] * len(self.streams)
        self.stopped = False

        self.transform = transform
        self.read_type = read_type

        # initialize queue and thread

        self.Qs = [Queue(maxsize=queue_size) for _ in range(self.streams_count)]
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True

    def start(self):
        # start a thread to read frames from the file video stream
        self.thread.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped: break
            for i, q in enumerate(self.Qs):
                # if the thread indicator variable is set, stop the thread
                if self.stopped: break
                # if the stream stopped, skip the stream
                if self.streams_stopped[i]: continue
                # otherwise, ensure the queue has room in it
                if not q.full():
                    frame = self.streams[i].read()
                    # if we have reached the end of the source, close the source
                    if frame is None:
                        self.streams_stopped[i] = True
                        self.streams[i].stop()
                        # if all stream are stopped, close the thread
                        if all(self.streams_stopped):
                            self.stopped = True
                    # if there are transforms to be done, might as well
                    # do them on producer thread before handing back to
                    # consumer thread. ie. Usually the producer is so far
                    # ahead of consumer that we have time to spare.
                    #
                    # Python is not parallel but the transform operations
                    # are usually OpenCV native so release the GIL.
                    #
                    # Really just trying to avoid spinning up additional
                    # native threads and overheads of additional
                    # producer/consumer queues since this one was generally
                    # idle grabbing frames.
                    if self.transform:
                        frame = self.transform(frame)
                    # add the frame to the queue
                    q.put(frame)
            # all queues are full, sleep some time
            if all(q.full() for q in self.Qs):
                time.sleep(0.1)

    def read(self, idx=None):
        if idx is not None:
            assert isinstance(idx, int) and idx >= 0 and idx < self.streams_count, f'Type of var i does not match or i out of range[0:{self.streams_count - 1}]: {idx}'
            if self.Qs[idx].qsize() == 0 and self.streams_stopped[idx]:
                warnings.warn(f'the stream was stopped: {idx}')
                return None
            # return next frame in the queue
            return self.Qs[idx].get()
        else:
            # all queue return one frame
            return [(self.Qs[i].get() if not self.streams_stopped[i] else None) for i in range(self.streams_count)] if not self.stopped else None

    # Insufficient to have consumer use while(more()) which does
    # not take into account if the producer has reached end of stream.
    def running(self, idx=None):
        if idx is not None:
            assert isinstance(idx, int) and idx >= 0 and idx < self.streams_count, f'Type of var i does not match or i out of range[0:{self.streams_count - 1}]: {idx}'
            return self.more(idx) or not self.streams_stopped[idx]
        else:
            return self.more() or not self.stopped

    def more(self, idx=None):
        # return True if there are still frames in the queue. If stream is not stopped, try to wait a moment
        if idx is not None:
            assert isinstance(idx, int) and idx >= 0 and idx < self.streams_count, f'Type of var i does not match or i out of range[0:{self.streams_count - 1}]: {idx}'
            tries = 0
            while self.Qs[idx].qsize() == 0 and not self.streams_stopped[idx] and tries < 5:
                time.sleep(0.1)
                tries += 1
            return self.Qs[idx].qsize() > 0
        else:        
            tries = 0
            while sum(q.qsize() for q in self.Qs) == 0 and not self.stopped and tries < 5:
                time.sleep(0.1)
                tries += 1
            return sum(q.qsize() for q in self.Qs) > 0

    def stop(self):
        # wait until stream resources are released (producer thread might be still grabbing frame)
        self.thread.join()
        # indicate that the thread should be stopped
        self.stopped = True


if __name__ == '__main__':
    import os
    import time
    from tqdm import tqdm
    from multiprocessing import Process

    def multi_video_stream(idx, source_dicts):
        print('Run task %s (%s)...' % (idx, os.getpid()))
        start = time.time()

        streams = MultiVideoStream(source_dicts).start()
        pbar = tqdm(desc='Bar {}'.format(idx))
        while streams.running():
            for i in range(streams.streams_count):
                frame = streams.read(i)
                if frame is None: break
                # do process
            pbar.update(1)
        streams.stop()
        end = time.time()
        print('Task %s runs %0.2f seconds.' % (idx, (end - start)))

    source_dicts = [
        {
            'uri': 'your uri',
            'gpu_id': 0,
        },
    ]
    

    P = [Process(target=multi_video_stream, args=(i, source_dicts)) for i in range(2)]
    for p in P: p.start()
    for p in P: p.join()

    print('All subprocesses done.')