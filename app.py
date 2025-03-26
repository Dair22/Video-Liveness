from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Habilita CORS para todas as origens. Para produção, use configurações específicas.

# Configurações de upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv'}

# Configurações do Flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Função para verificar se o arquivo tem uma extensão permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para gerar o stream HLS
def generate_hls_stream(video_path):
    try:
        stream_dir = os.path.join('streams', str(os.path.basename(video_path)))
        if not os.path.exists(stream_dir):
            os.makedirs(stream_dir)

        # Definindo a URL do stream
        stream_url = f"/streams/{os.path.basename(video_path)}/index.m3u8"

        # Comando FFmpeg para gerar o stream HLS
        subprocess.run([
            'ffmpeg', '-i', video_path, '-preset', 'fast', '-g', '50', '-sc_threshold', '0',
            os.path.join(stream_dir, 'index.m3u8')
        ], check=True)

        print(f"Stream gerado com sucesso: {stream_url}")
        return stream_url
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o FFmpeg: {str(e)}")
        raise Exception(f"Erro ao gerar o stream: {str(e)}")
    except Exception as e:
        print(f"Erro ao gerar o stream: {str(e)}")
        raise Exception(f"Erro desconhecido: {str(e)}")

# Rota para iniciar o streaming do vídeo
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

        try:
            # Salva o arquivo de vídeo no servidor
            file.save(file_path)

            # Gera o link para o streaming HLS
            stream_url = generate_hls_stream(file_path)

            return jsonify({'status': 'streaming', 'streamUrl': stream_url})

        except Exception as e:
            print(f"Erro ao processar o vídeo: {str(e)}")
            return jsonify({'error': f'Failed to generate stream: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file format'}), 400

# Inicia o servidor na porta 80
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

