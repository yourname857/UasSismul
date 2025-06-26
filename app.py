import os
import uuid

from flask import Flask, render_template, request, send_file

from utils import (compress_video, convert_format, encode_inter_frame,
                   encode_intra_frame)

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'static/output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video = request.files['video']
        option = request.form['option']
        output_format = request.form.get('format')

        original_name = os.path.splitext(video.filename)[0]
        file_ext = '.mp4' if option != 'convert' else f'.{output_format}'
        output_filename = f"{original_name}_{option}{file_ext}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        video_path = os.path.join(UPLOAD_FOLDER, video.filename)
        video.save(video_path)

        try:
            if option == 'intra':
                encode_intra_frame(video_path, output_path)
            elif option == 'inter':
                encode_inter_frame(video_path, output_path)
            elif option == 'convert' and output_format:
                convert_format(video_path, output_path, output_format)
            elif option == 'compress':
                compress_video(video_path, output_path)
        except Exception as e:
            return f"Terjadi kesalahan: {str(e)}"

        return render_template('index.html', result=output_filename)

    return render_template('index.html', result=None)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
