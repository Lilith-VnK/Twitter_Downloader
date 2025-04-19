import sys
import re
import yt_dlp
import shutil
import concurrent.futures
import time
import threading
from pathlib import Path
from argparse import ArgumentParser

class ConsoleUI:
    COLORS = {
        "error": "\033[31m",
        "success": "\033[32m",
        "warning": "\033[33m",
        "info": "\033[36m",
        "reset": "\033[0m"
    }
    
    def __init__(self):
        self.lock = threading.Lock()
        self.spinner_chars = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
        self.spinner_pos = 0
    
    def print(self, message, status=None, end="\n"):
        with self.lock:
            color = self.COLORS.get(status, "")
            sys.stdout.write(f"{color}{message}{self.COLORS['reset']}{end}")
            sys.stdout.flush()
    
    def show_progress(self, d):
        if d['status'] == 'downloading':
            self._update_progress(
                percent=d.get('_percent_str', 'N/A'),
                speed=d.get('_speed_str', 'N/A'),
                eta=d.get('_eta_str', 'N/A')
            )
    
    def _update_progress(self, percent, speed, eta):
        with self.lock:
            spin = self.spinner_chars[self.spinner_pos]
            self.spinner_pos = (self.spinner_pos + 1) % len(self.spinner_chars)
            progress = f"{spin} {percent} | {speed} | ETA: {eta}"
            sys.stdout.write("\r" + " " * 80 + "\r")
            sys.stdout.write(f"{self.COLORS['info']}{progress}{self.COLORS['reset']}")
            sys.stdout.flush()

console = ConsoleUI()

def validate_urls(urls):
    pattern = re.compile(
        r"^(?:https?://)?(?:www\.)?(?:twitter\.com|x\.com)/[A-Za-z0-9_]+/status/[0-9]+(?:\?.*)?$"
    )
    return [url for url in urls if pattern.match(url)]

def load_cookies(cookie_path):
    required = {'auth_token', 'ct0'}
    cookies = {}
    
    try:
        with open(cookie_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(('#', '//')):
                    continue
                
                if '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 7 and parts[5] in required:
                        cookies[parts[5]] = parts[6]
                elif '=' in line:
                    name, value = line.split('=', 1)
                    if name.strip() in required:
                        cookies[name.strip()] = value.strip()
        
        if not all(key in cookies for key in required):
            raise ValueError("Missing required cookies")
            
        return cookies
    except Exception as e:
        console.print(f"Cookie error: {str(e)}", "error")
        sys.exit(1)

def download_video(url, output_template, cookies):
    ydl_opts = {
        'outtmpl': output_template,
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'cookiefile': 'cookies.txt',
        'noprogress': True,
        'concurrent_fragment_downloads': 4,
        'http_chunk_size': 1048576,
        'retries': 3,
        'fragment_retries': 3,
        'skip_unavailable_fragments': True,
        'progress_hooks': [console.show_progress],
        'sanitize_filename': True,
        'restrictfilenames': True,
        'external_downloader': 'aria2c' if shutil.which('aria2c') else None,
        'external_downloader_args': [
            '-x 8', '-s 8', '-k 2M',
            '--allow-overwrite=true',
            '--auto-file-renaming=false'
        ]
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            console.print(f"Starting download: {info['title']}", "info")
            
            ydl.download([url])
            console.print(f"Successfully downloaded: {info['title']}", "success")
            return True
            
    except yt_dlp.utils.DownloadError as e:
        console.print(f"Download failed: {str(e)}", "error")
        return False
    except Exception as e:
        console.print(f"Critical error: {str(e)}", "error")
        sys.exit(1)

def main():
    parser = ArgumentParser(description='Twitter Video Downloader')
    parser.add_argument('urls', nargs='+', help='Twitter post URLs')
    parser.add_argument('-c', '--cookies', default='cookies.txt', help='Cookie file path')
    parser.add_argument('-o', '--output', default='%(title)s.%(ext)s', help='Output filename template')
    parser.add_argument('-t', '--threads', type=int, default=4, help='Number of parallel downloads')
    
    args = parser.parse_args()
    
    valid_urls = validate_urls(args.urls)
    if not valid_urls:
        console.print("No valid Twitter URLs found", "error")
        sys.exit(1)
        
    try:
        cookies = load_cookies(args.cookies)
    except Exception as e:
        console.print(f"Cookie validation failed: {str(e)}", "error")
        sys.exit(1)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for url in valid_urls:
            future = executor.submit(
                download_video,
                url,
                args.output,
                cookies
            )
            futures.append(future)
            
        success = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    success += 1
            except Exception as e:
                console.print(f"Thread error: {str(e)}", "error")
                
    console.print(f"\nDownload complete: {success}/{len(valid_urls)} successful", "info")

if __name__ == '__main__':
    main()