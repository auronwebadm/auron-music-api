from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import yt_dlp
import json
import os
import tempfile

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
            
            # Criar arquivo temporário com cookies
            cookies_content = os.environ.get('YOUTUBE_COOKIES', '')
            cookies_file = None
            
            if cookies_content:
                cookies_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
                cookies_file.write(cookies_content)
                cookies_file.close()
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookies_file.name if cookies_file else None,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
            
            # Limpar arquivo temporário
            if cookies_file:
                os.unlink(cookies_file.name)
                
            response = {
                'success': True,
                'videoId': video_id,
                'title': info.get('title', ''),
                'duration': str(info.get('duration', 0)),
                'audioUrl': info.get('url', '')
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            if cookies_file:
                os.unlink(cookies_file.name)
            response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
