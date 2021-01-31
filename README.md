# VIPTool

VIPTool is a simple video and image processing tool for personal use.

## Description

In target detection, the raw data is often a video, while the data needed for the detection model are images. At the same time, we often want to observe the results by composing a video from the marked images. So we would like to create a small tool called **VideoImageConverter** to simplify this step.

## Requirements

- python3
- python packages
  - opencv-python
  - tqdm
  - fire
  - glob

## Usage

```bash
# video to images
python3 VideoImageConverter.py video2Image --videoPath='video/path' --imgDir='out'
# images to video
python3 VideoImageConverter.py image2Video --imgDir='images/dir' --fps=20 --videoPath='out.avi'

# also, you can use `python3 VideoImageConverter.py -h` to see more.
```

##  License

This software is freely available under the MIT Public License.
