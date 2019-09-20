from utils.file.base import gen_filename, get_ext
import os
import ffmpeg
import subprocess
from datetime import datetime

from utils import get_random_string
from utils.log.base import error
from utils.protocol import code_msg

from functools import wraps
def runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        before = datetime.now()
        rst = func(*args, **kwargs)
        print('*'*50)
        print(f'{func.__name__} : {datetime.now() - before}')
        print('*'*50)
        return rst
    return wrapper


TEMPLATE = [
            {
            'bg': 'bg4.mp4',
            'mask': 'mask4.mp4',
            'fg': 'fg4.mp4',
            'd': 4.75
            },
            {
            'bg': 'bg1.mp4',
            'mask': 'mask1.mp4',
            'fg': 'fg1.mp4',
            'd': 4.75
            },
            {
            'bg': 'bg2.mp4',
            'mask': 'mask2.mp4',
            'fg': 'fg2.mp4',
            'd': 4.75
            },
            {
            'bg': 'bg3.mp4',
            'mask': 'mask3.mp4',
            'fg': 'fg3.mp4',
            'd': 4.75
            },
            ]


def template_path(filename):
    return f'/Users/zedd/Desktop/Gizmos/ffmpeg/template/38/{filename}'


MUSIC = os.getcwd() + f'/template/38/audio.m4a'


class Effect:
    zoom_in = 'zoom_in'
    zoom_out = 'zoom_out'
    fade_in = 'fade_in'
    fade_out = 'fade_out'


class Scene(object):
    def __init__(self, img, background, mask, foreground=None, effect='zoom_out', duration=4.75):
        self.img = img
        self.background = background
        self.mask = mask
        self.foreground = foreground
        self.effect = effect
        self.duration = duration
    
    @property
    def scene(self):
        if not (self.img and self.background and self.mask):
            return None
        
        img_video = img_to_video(self.img, self.duration, 'zoom_out')
        if not img_video:
            return None
    
        complete_path = os.path.join(UPLOAD_DIR, gen_filename(".mp4"))
        
        img_video_input = ffmpeg.input(img_video)
        bg_input = ffmpeg.input(self.background)
        mask_input = ffmpeg.input(self.mask)
        if self.foreground:
            fg_input = ffmpeg.input(self.foreground)

mask_inverted = ffmpeg.filter(mask_input, 'negate')
bg_merged = ffmpeg.filter([bg_input, mask_inverted], 'alphamerge')

img_video_overlay = ffmpeg.filter(
                                  [img_video_input, bg_merged], 'overlay', format='auto')
    if self.foreground:
        fg_input_inverted = ffmpeg.filter(
                                          fg_input, 'mergeplanes', '0x00010200', format='yuva420p')
            img_video_overlay = ffmpeg.filter(
                                              [img_video_overlay, fg_input_inverted], 'overlay')
                                          img_video_overlay = ffmpeg.output(img_video_overlay, complete_path)
                                          try:
                                          ffmpeg.run(img_video_overlay)
                                          except Exception as e:
                                          error('errors', f'scene_error: {e}')
                                          return None
                                          return complete_path

@runtime
def img_to_video(img, duration, effect='zoom_out'):
    complete_path = os.path.join(UPLOAD_DIR, gen_filename(".mp4"))
    img_stream = ffmpeg.input(img, r=25, loop=1)
    img_stream = ffmpeg.filter(img_stream, 'scale', w='iw*4', h='-1')
    if effect == Effect.zoom_out:
        img_stream = ffmpeg.filter(img_stream, 'zoompan', z='zoom+0.002',
                                   x='iw/2-(iw/zoom/2)', y='ih/2-(ih/zoom/2)', s='720x960')
    else:
        return None
    img_stream = ffmpeg.output(img_stream, complete_path, pix_fmt='yuv420p',
                               vcodec='libx264', video_bitrate='600k', r=25,
                               preset='ultrafast', crf=28, t=duration)
                               try:
                                   ffmpeg.run(img_stream)
except Exception as e:
    error('errors', f'img_to_video_error: {e}')
    return None
    return complete_path


def concat_videos(videos):
    txt = ''
    for video in videos:
        txt += "file '{}'\n".format(video)
    if not txt:
        return None
    complete_path = os.path.join(UPLOAD_DIR, gen_filename(".txt"))
    if not os.path.exists(os.path.dirname(complete_path)):
        os.makedirs(os.path.dirname(complete_path))
    with open(complete_path, 'w') as f:
        f.write(txt)
    
    video_path = os.path.join(UPLOAD_DIR, gen_filename(".mp4"))
    stream = ffmpeg.input(complete_path, safe=0, f='concat')
    stream = ffmpeg.output(video_path, c='copy')
    try:
        ffmpeg.run(stream)
        return video_path
    except Exception as e:
        error('errors', f'concat_videos_error: {e}')
        return None


class VideoAlbum(object):
    def __init__(self, imgs):
        self.imgs = imgs
    
    @property
    def album(self):
        scenes = []
        j = 0
        for i in range(len(self.imgs)):
            template = TEMPLATE[j]
            j += 1
            if j >= len(TEMPLATE):
                j = 0
            scene = Scene(self.imgs[i], template_path(template['bg']), template_path(
                                                                                     template['mask']), foreground=template_path(template['fg']),
                          duration=template['d']).scene
                          if scene:
                              scenes.append(scene)
                          
                          if len(scenes) > 1:
                              album = concat_videos(scenes)
                                  elif scenes:
                                      album = scenes[0]
                                          else:
                                              album = None
                                                  if not album:
                                                      return None
                                                          return album


def gen_video_album(imgs):
    img_files = upload_img(imgs)
    video_album = VideoAlbum(img_files).album
    result = code_msg(0)
    result["d"] = {"album": video_album}
    return result


UPLOAD_DIR = '/Users/zedd/video_album'


def upload_img(imgs):
    img_path = []
    for img in imgs:
        if isinstance(img, bytes):
            ext = '.jpg'
        else:
            ext = get_ext(img.filename)
        img.seek(0)
        filename = gen_filename(ext)
        complete_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(os.path.dirname(complete_path)):
            os.makedirs(os.path.dirname(complete_path))
        
        if isinstance(img, bytes):
            with open(complete_path, 'wb') as f:
                f.write(img)
        else:
            img.save(complete_path)
        img_path.append(complete_path)
    
    return img_path
