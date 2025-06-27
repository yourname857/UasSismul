import os

from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename

from utils import (compress_video, convert_format, embed_message_in_video,
                   encode_inter_frame, encode_intra_frame,
                   extract_message_from_video)

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

        filename = secure_filename(video.filename)
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)

        original_name, _ = os.path.splitext(filename)
        file_ext = f'.{output_format}' if option == 'convert' and output_format else '.mp4'
        output_filename = f"{original_name}_{option}{file_ext}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        try:
            if option == 'compress':
                compress_video(video_path, output_path)
            elif option == 'convert' and output_format:
                convert_format(video_path, output_path)
            elif option == 'intra':
                encode_intra_frame(video_path, output_path)
            elif option == 'inter':
                encode_inter_frame(video_path, output_path)
            else:
                return "Opsi tidak valid atau belum didukung."

            return render_template('index.html', result=output_filename)
        except Exception as e:
            return f"Terjadi kesalahan saat memproses video: {str(e)}"

    return render_template('index.html', result=None)

@app.route('/steganografi', methods=['GET', 'POST'])
def steganografi():
    encoded_path = None
    decoded_message = None

    if request.method == 'POST':
        if 'encode' in request.form:
            video = request.files['video']
            secret = request.form['secret']
            filename = secure_filename(video.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            video.save(input_path)

            output_filename = f"encoded_{filename}"
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            try:
                embed_message_in_video(input_path, secret, output_path)
                encoded_path = output_filename
            except Exception as e:
                return f"Error encoding: {str(e)}"

        elif 'decode' in request.form:
            video = request.files['video']
            filename = secure_filename(video.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            video.save(input_path)
            try:
                decoded_message = extract_message_from_video(input_path)
            except Exception as e:
                return f"Error decoding: {str(e)}"

    return render_template('steganografi.html', result=encoded_path, message=decoded_message)

@app.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(OUTPUT_FOLDER, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
