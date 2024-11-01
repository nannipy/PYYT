from flask import Flask, request, render_template, jsonify, redirect
import yt_dlp

app = Flask(__name__)

def get_audio_url(video_url):
    """Ottiene l'URL diretto dello stream audio"""
    try:
        ydl_opts = {
            'format': 'bestaudio[ext=m4a]/bestaudio',  # Preferisci formato m4a
            'extract_audio': True,
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Estrai le informazioni del video
            info = ydl.extract_info(video_url, download=False)
            
            # Prendi il formato audio migliore disponibile
            for format in info['formats']:
                if format.get('acodec') != 'none' and format.get('vcodec') == 'none':
                    return {
                        'success': True,
                        'url': format['url'],
                        'title': info.get('title', 'audio')
                    }
            
            raise Exception("Nessun formato audio trovato")

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        result = get_audio_url(url)
        
        if result['success']:
            # Reindirizza direttamente all'URL dello stream audio
            return redirect(result['url'])
        else:
            return render_template('index.html', error=result['error'])
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)