# -*- coding: utf-8 -*-
# @Author: Zedd
# @Date: 2019-03-07 11:05:27

from moviepy.editor import (
    VideoClip, VideoFileClip, CompositeVideoClip,
    AudioFileClip, AudioClip, TextClip, concatenate_videoclips
)
from moviepy.video.io.bindings import (mplfig_to_npimage)
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

cwd = os.getcwd()


def make_video(srcs_videos, subtitles=None):

    # head_temp_clip = VideoFileClip(cwd + '/' + 'head.mp4').subclip(0, 4)
    # head_text_clip = TextClip(txt=title, color='red', method='caption', fontsize=30).set_duration(
    #     4).set_position('center')
    # head_clip = CompositeVideoClip([head_temp_clip, head_text_clip])

    # tail_temp_clip = VideoFileClip(cwd + '/' + 'tail.mp4').subclip(0, 4)
    # tail_text_clip = TextClip(txt=author, color='red', method='caption', fontsize=30).set_duration(
    #     4).set_position('center')
    # tail_clip = CompositeVideoClip([tail_temp_clip, tail_text_clip])

    # subtitles = subtitles.split(',')
    # subtitle_clips = []
    # subtitle_clip_temp = VideoFileClip(
    #     cwd + '/' + 'subtitle.mp4').subclip(0, 3)
    # for sub in subtitles:
    #     txt_clip = TextClip(txt=sub, color='red', method='caption', fontsize=30).set_duration(
    #         3).set_position('center')
    #     sub_clip = CompositeVideoClip([subtitle_clip_temp, txt_clip])
    #     subtitle_clips.append(sub_clip)

    scene1 = Scene('bg1.mp4', 'fg1.mp4', 'mask1.mp4')
    scene2 = Scene('bg2.mp4', 'fg2.mp4', 'mask2.mp4')
    scene3 = Scene('bg3.mp4', 'fg3.mp4', 'mask3.mp4')
    scene4 = Scene('bg4.mp4', 'fg4.mp4', 'mask4.mp4')
    scene_temps = [scene1, scene2, scene3, scene4]
    scene_temps_len = len(scene_temps)

    scene_clips = []
    i = 0
    for v in srcs_videos:
        if i >= scene_temps_len:
            i = 0
        scene_temp = scene_temps[i]
        v_clip = VideoFileClip(cwd + '/' + v)
        scene_clips.append(scene_temp.clip(v_clip))
        i += 1

    all_clips = []
    # all_clips.extend(head_clip)
    # all_clips.extend(subtitle_clips)
    all_clips.extend(scene_clips)
    # all_clips.append(tail_clip)

    result = concatenate_videoclips(all_clips).set_audio(
        AudioFileClip(cwd + '/audio.m4a'))
    result.write_videofile(cwd + '/final.mp4')


class Scene(object):
    def __init__(self, bg, fg, mask, length=4):
        self.bg = bg
        self.fg = fg
        self.mask = mask
        self.length = length

    base_path = cwd + '/'

    @property
    def b(self):
        return self.base_path + self.bg

    @property
    def f(self):
        return self.base_path + self.fg

    @property
    def m(self):
        return self.base_path + self.mask

    def clip(self, video):
        clips = []
        if self.bg:
            bg_clip = VideoFileClip(self.b).subclip(0, self.length)
            clips.append(bg_clip)

        video_clip = video.subclip(0, self.length)
        if self.mask:
            mask_clip = VideoFileClip(self.m).subclip(0, self.length).to_mask()
            video_clip = video_clip.set_mask(mask_clip)
        clips.append(video_clip)

        if self.fg:
            fg_clip = VideoFileClip(self.f).subclip(0, self.length)
            fg_mask = fg_clip.to_mask()
            fg_clip = fg_clip.set_mask(fg_mask)
            clips.append(fg_clip)

        fin_clip = CompositeVideoClip(clips)
        return fin_clip


x = np.linspace(-2, 2, 200)
duration = 2
fig, ax = plt.subplots()
def make_frame(t):
    ax.clear()
    ax.plot(x, np.sinc(x**2) + np.sin(x + 2*np.pi/duration * t), lw=3)
    ax.set_ylim(-1.5, 2.5)
    return mplfig_to_npimage(fig)


def draw_animation():
    animation = VideoClip(make_frame=make_frame, duration=duration)
    animation.write_videofile("matplotlib.mp4", fps=20)


if __name__ == "__main__":
    make_video(['cat.mp4', 'deer.mp4', 'dog.mp4', 'horse.mp4', 
                'leopard.mp4', 'monkey.mp4', 'panda.mp4', 'penguin.mp4', 
                'pig.mp4', 'swan.mp4', 'tiger.mp4', 'wolf.mp4'])
    # draw_animation()
