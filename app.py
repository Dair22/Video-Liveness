from flask import Flask, Response
import cv2

app = Flask(__name__)

# Carregar um vídeo da galeria (substitua pelo caminho correto do seu vídeo)
video_path = "video.mp4"  # O nome do vídeo que estará na mesma pasta do app.py
cap = cv2.VideoCapture(video_path)

def generate():
    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reinicia o vídeo quando termina
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    return "Servidor está rodando! Acesse /video_feed para ver o streaming."

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
