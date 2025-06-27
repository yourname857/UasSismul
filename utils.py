import os

import cv2
import numpy as np
from moviepy.editor import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def text_to_binary(text):
    return ''.join(format(ord(c), '08b') for c in text) + '00000000'

def binary_to_text(binary_data):
    chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    result = ''
    for b in chars:
        if b == '00000000':
            break
        result += chr(int(b, 2))
    return result

def encode_lsb_on_frame(frame, message):
    binary_message = text_to_binary(message)
    data_index = 0
    h, w, _ = frame.shape
    for y in range(h):
        for x in range(w):
            for c in range(3):  # R, G, B
                if data_index < len(binary_message):
                    original_value = int(frame[y, x, c])
                    modified_value = (original_value & 0b11111110) | int(binary_message[data_index])
                    frame[y, x, c] = np.uint8(modified_value)
                    data_index += 1
    return frame

def decode_lsb_from_frame(frame):
    binary_data = ''
    h, w, _ = frame.shape
    for y in range(h):
        for x in range(w):
            for c in range(3):
                binary_data += str(frame[y, x, c] & 1)
    return binary_to_text(binary_data)

def embed_message_in_video(video_path, message, output_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frames = []
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Gagal membaca video")

    frame = encode_lsb_on_frame(frame, message)
    frames.append(frame)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    cap.release()
    frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
    clip = ImageSequenceClip(frames_rgb, fps=fps)
    clip.write_videofile(output_path, codec='libx264', audio=False)

def extract_message_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        raise ValueError("Gagal membaca video")
    return decode_lsb_from_frame(frame)

def compress_video(input_path, output_path, target_bitrate="500k"):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, bitrate=target_bitrate, codec='libx264')

def convert_format(input_path, output_path):
    clip = VideoFileClip(input_path)
    clip.write_videofile(output_path, codec='libx264')

def encode_intra_frame(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    frames = []
    ret, frame = cap.read()
    if not ret:
        raise ValueError("Gagal membaca video")
    
    for _ in range(30):  # misalnya duplikasi 30 frame pertama
        frames.append(frame.copy())

    cap.release()
    frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
    clip = ImageSequenceClip(frames_rgb, fps=fps)
    clip.write_videofile(output_path, codec='libx264', audio=False)

def encode_inter_frame(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    frames = []
    index = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if index == 10:
            cv2.putText(frame, 'INTER', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 0, 255), 2, cv2.LINE_AA)
        frames.append(frame)
        index += 1

    cap.release()
    frames_rgb = [cv2.cvtColor(f, cv2.COLOR_BGR2RGB) for f in frames]
    clip = ImageSequenceClip(frames_rgb, fps=fps)
    clip.write_videofile(output_path, codec='libx264', audio=False)
