from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import json
import os

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse da URL
        parsed_path = urlparse(self.path)
        params = parse_qs(parsed_path.query)
        
        # Extrai o videoId do parâmetro ?v=
        video_id = params.get('v', [None])[0]
        
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        # Validação
        if not video_id:
            response = {
                'success': False,
                'error': 'Parâmetro "v" (videoId) é obrigatório'
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        try:
            # Comando yt-dlp para extrair informações
            youtube_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Extrai URL do áudio e metadados
            result = subprocess.run(
                [
                    'yt-dlp',
                    '--format', 'bestaudio[ext=m4a]/bestaudio',
                    '--get-url',
                    '--get-title',
                    '--get-duration',
                    '--no-warnings',
                    '--no-playlist',
                    youtube_url
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise Exception(f"yt-dlp falhou: {result.stderr}")
            
            # Parse da saída
            lines = result.stdout.strip().split('\n')
            
            if len(lines) < 3:
                raise Exception("Formato de resposta inválido do yt-dlp")
            
            title = lines[0]
            duration = lines[1]
            audio_url = lines[2]
            
            # Resposta de sucesso
            response = {
                'success': True,
                'videoId': video_id,
                'title': title,
                'duration': duration,
                'audioUrl': audio_url
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except subprocess.TimeoutExpired:
            response = {
                'success': False,
                'error': 'Timeout: Extração demorou muito (>30s)'
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            response = {
                'success': False,
                'error': str(e)
            }
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        # Suporte para CORS preflight
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
