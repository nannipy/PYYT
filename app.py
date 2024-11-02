from flask import Flask, render_template, request, redirect, url_for, session
import pytube
import time
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)
app.secret_key = 'your_secret_key_1284732472'

def get_video_id(url):
    """Estrae l'ID del video dall'URL di YouTube."""
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    return None

def download_video(url, max_retries=3):
    """Tenta di scaricare il video con retry in caso di errore."""
    for attempt in range(max_retries):
        try:
            video = pytube.YouTube(url)
            # Attendi che i dati del video siano disponibili
            time.sleep(1)
            if not video.title:
                raise Exception("Impossibile recuperare il titolo del video")
                
            streams = video.streams.filter(progressive=True, file_extension="mp4").all()
            if not streams:
                raise Exception("Nessuno stream disponibile per questo video")
                
            stream = streams[-1]  # Qualità più alta disponibile
            return video, stream
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2)  # Attendi prima di riprovare

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        try:
            # Verifica che l'URL sia valido
            video_id = get_video_id(youtube_url)
            if not video_id:
                return "URL di YouTube non valido"
                
            video, stream = download_video(youtube_url)
            session['title'] = video.title
            
            # Download del video
            stream.download(output_path='static', filename=f'{video.title}.mp4')
            return redirect(url_for('download'))
        except Exception as e:
            return f"Si è verificato un errore: {str(e)}"
    return render_template('index.html')

@app.route('/download')
def download():
    if 'title' not in session:
        return redirect(url_for('index'))
    return render_template('download.html', video_title=session['title'])

if __name__ == '__main__':
    app.run(debug=True)