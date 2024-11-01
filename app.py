import os
import yt_dlp
from flask import Flask, request, render_template, send_file, make_response
import tempfile
import uuid

app = Flask(__name__)

def generate_safe_filename():
    """Genera un nome file univoco"""
    return str(uuid.uuid4())

def download_mp3(url):
    """Scarica un file MP3 dall'URL del video usando una directory temporanea"""
    try:
        # Usa la directory temporanea di sistema
        temp_dir = tempfile.mkdtemp(dir='/tmp')
        
        # Genera un nome file univoco
        output_file = os.path.join(temp_dir, f"{generate_safe_filename()}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': output_file,
            'prefer_ffmpeg': True,
            'keepvideo': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Estrai le informazioni senza scaricare
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video')
            
            # Scarica il file
            ydl.download([url])
            
            # Trova il file MP3 creato
            mp3_file = None
            for file in os.listdir(temp_dir):
                if file.endswith('.mp3'):
                    mp3_file = os.path.join(temp_dir, file)
                    break
            
            if mp3_file:
                return {
                    'success': True,
                    'file_path': mp3_file,
                    'title': video_title
                }
            else:
                raise Exception("File MP3 non trovato dopo il download")

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        result = download_mp3(url)
        
        if result['success']:
            try:
                # Leggi il file e creane una risposta
                with open(result['file_path'], 'rb') as f:
                    response = make_response(f.read())
                
                # Imposta gli header appropriati
                response.headers['Content-Type'] = 'audio/mpeg'
                response.headers['Content-Disposition'] = f'attachment; filename="{result["title"]}.mp3"'
                
                # Elimina il file temporaneo
                os.remove(result['file_path'])
                
                return response
            except Exception as e:
                return render_template('index.html', error=f"Errore nell'invio del file: {str(e)}")
        else:
            return render_template('index.html', error=result['error'])
    
    return render_template('index.html')