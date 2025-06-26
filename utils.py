import subprocess


def encode_intra_frame(input_path, output_path):
    result = subprocess.run([
        'ffmpeg', '-i', input_path,
        '-g', '1', '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        output_path
    ], capture_output=True, text=True)
    print(result.stderr)

def encode_inter_frame(input_path, output_path):
    result = subprocess.run([
        'ffmpeg', '-i', input_path,
        '-g', '30', '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        output_path
    ], capture_output=True, text=True)
    print(result.stderr)

def convert_format(input_path, output_path, format):
    result = subprocess.run([
        'ffmpeg', '-i', input_path,
        output_path
    ], capture_output=True, text=True)
    print(result.stderr)

def compress_video(input_path, output_path):
    result = subprocess.run([
        'ffmpeg', '-i', input_path,
        '-vf', 'scale=640:-1',
        '-b:v', '500k', '-c:v', 'libx264', '-preset', 'fast',
        output_path
    ], capture_output=True, text=True)
    print(result.stderr)
