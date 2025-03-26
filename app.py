from flask import Flask, request, jsonify
from flask_cors import CORS  # Importando o CORS
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Permitindo CORS para todos os domínios

# Configuração de upload de vídeos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mkv', 'avi'}
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # Limite de 100MB para upload de vídeos

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # Limite de tamanho de upload

# Função para verificar a extensão do arquivo
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/start-stream', methods=['POST'])
def start_stream():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Gerar URL do stream HLS
        try:
            stream_url = generate_hls_stream(file_path)
            return jsonify({'status': 'streaming', 'streamUrl': stream_url})
        except Exception as e:
            return jsonify({'error': f'Failed to generate stream: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file format'}), 400

# Função para gerar o stream HLS
def generate_hls_stream(video_path):
    stream_dir = os.path.join('streams', str(os.path.basename(video_path)))
    if not os.path.exists(stream_dir):
        os.makedirs(stream_dir)

    # Comando FFmpeg para criar o stream HLS
    stream_url = f"/streams/{os.path.basename(video_path)}/index.m3u8"
    subprocess.run([
        'ffmpeg', '-i', video_path, '-preset', 'fast', '-g', '50', '-sc_threshold', '0',
        os.path.join(stream_dir, 'index.m3u8')
    ], check=True)

    return stream_url

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
