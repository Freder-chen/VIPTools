# VIPTools

VIPTools is a simple video and image processing tool for personal use.

## Description

In target detection, the raw data is often a video, while the data needed for the detection model are images. At the same time, we often want to observe the results by composing a video from the marked images. So we would like to create a small tool called **VideoImageConverter** to simplify this step.

## Requirements

- python3
- python packages
  - opencv-python
  - tqdm
  - fire
  - glob

## Quick Start

### Installation

``` bash
pip3 install -r requirements.txt
```

### Usage

#### 1. shell

```bash
# VIPTools has two class, VideoImageConverter and VideoProcesser.

# In VideoImageConverter, we can
# video to images
python3 -m VIPTools VideoImageConverter video2images --video_filename='video/filename' --imgdir='out'
# images to video
python3 -m VIPTools VideoImageConverter images2video --imgdir='images/dir' --fps=20 --video_filename='out.avi'

# In VideoProcesser, we can
# avi to mp4
python3 -m VIPTools VideoProcesser avi2mp4 --avi_filename='video/filename.avi' --mp4_filename='out.mp4'
# crop video
python3 -m VIPTools VideoProcesser crop_video --video_filename='video/filename' --crop_filename='out[.avi|.mp4]' [--start_time=[0] --end_time=[int]]

# also, we can use `python3 VIPTools -h` to see more.
```

#### 2. python

```python3
import VIPTools

video_filename = 'a.mp4'
imgdir = 'out'

VIPTools.VideoImageConverter().video2image(video_filename, imgdir)
VIPTools.VideoImageConverter().image2video(imgdir, video_filename, fps=20)
```

##  License

Licensed under the MIT Public License.