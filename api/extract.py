from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yt_dlp
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        video_id = params.get('v', [None])[0]
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        if not video_id:
            response = {'success': False, 'error': 'Parâmetro "v" obrigatório'}
            self.wfile.write(json.dumps(response).encode())
            return
        
        try:
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # 🔥 MÁXIMAS OTIMIZAÇÕES SEM BROWSER
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extractor_args': {
                    'youtube': {
                        # Força client mobile (menos restrições)
                        'player_client': ['android_music', 'android', 'ios'],
                        'skip': ['hls', 'dash'],
                    }
                },
                # Headers de dispositivo Android real
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/19.09.37 (Linux; U; Android 13) gzip',
                    'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
                    'Accept': '*/*',
                }
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                
            response = {
                'success': True,
                'videoId': video_id,
                'title': info.get('title', ''),
                'duration': str(info.get('duration', 0)),
                'audioUrl': info.get('url', '')
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
