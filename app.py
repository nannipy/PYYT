import os
import yt_dlp
from flask import Flask, request, render_template, send_file

app = Flask(__name__)

def download_mp3(url):
    """Scarica un file MP3 dall'URL del video"""
    try:
        # Configurazione per yt-dlp
        download_path = os.path.join('downloads', 'mp3')
        os.makedirs(download_path, exist_ok=True)

        # Opzioni per yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        }

        # Scaricamento del file
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Ottieni il nome del file scaricato
            filename = ydl.prepare_filename(info_dict)
            filename = os.path.splitext(filename)[0] + '.mp3'
            
            # Ritorna il percorso completo del file
            return filename

    except Exception as e:
        return f"Errore nel download: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        url = request.form['url']
        result = download_mp3(url)
    
    return render_template('index.html', result=result)

@app.route('/download/<path:filename>')
def download_file(filename):
    filepath = os.path.join('downloads', 'mp3', filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)