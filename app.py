from flask import Flask, request, render_template, Response, stream_with_context
import yt_dlp
import io

app = Flask(__name__)

def stream_mp3(url):
    """Scarica e streamma il file MP3 direttamente al client"""
    try:
        # Buffer in memoria invece che su file
        buffer = io.BytesIO()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            # Output direttamente nel buffer
            'outtmpl': '-',
            'prefer_ffmpeg': True,
            'keepvideo': False
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Estrai le informazioni
            info_dict = ydl.extract_info(url, download=False)
            video_title = info_dict.get('title', 'video')
            
            def generate():
                # Scarica e streamma i dati
                proc = ydl.download([url])
                
                # Leggi il buffer a blocchi
                buffer.seek(0)
                while True:
                    chunk = buffer.read(8192)
                    if not chunk:
                        break
                    yield chunk
            
            return {
                'success': True,
                'generator': generate,
                'title': video_title
            }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        result = stream_mp3(url)
        
        if result['success']:
            return Response(
                stream_with_context(result['generator']),
                mimetype='audio/mpeg',
                headers={
                    'Content-Disposition': f'attachment; filename="{result["title"]}.mp3"'
                }
            )
        else:
            return render_template('index.html', error=result['error'])
    
    return render_template('index.html')