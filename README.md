# Twitter Video Downloader

A Python script to download videos from Twitter/X with parallel downloads, cookie support, and progress tracking.

## Features

- � Parallel video downloads using multiple threads
- 🍪 Cookie authentication support for protected tweets
- 📊 Real-time progress indicators (speed, ETA, percentage)
- 🔄 Automatic retry mechanism for failed downloads
- ⚡ aria2c integration for faster downloads (optional)
- 📁 Customizable output filename templates

## Prerequisites

- Python 3.7+
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- (Optional) [aria2c](https://aria2.github.io/) for accelerated downloads

## Installation

1. Clone the repository
   ```
   https://github.com/Lilith-VnK/Twitter_Downloader
   ```
3. Install required packages:
   ```bash
   pip install yt-dlp
   pip install aria2c
   ```

## Usage

Basic syntax:
```bash
python aria2.py [URLS] [OPTIONS]

Arguments:
  urls                    One or more Twitter post URLs
  
Options:
  -c, --cookies PATH      Path to cookies file (default: cookies.txt)
  -o, --output TEMPLATE   Output filename template (default: %(title)s.%(ext)s)
  -t, --threads NUM       Number of parallel downloads (default: 4)
```

### Examples

1. Single download:
   ```bash
   python twitter_downloader.py "https://twitter.com/user/status/1234567890"
   ```

2. With custom cookies and output filename:
   ```bash
   python twitter_downloader.py -c my_cookies.txt -o "videos/%(title)s.%(ext)s" <URL>
   ```

3. Multiple URLs with parallel downloads:
   ```bash
   python twitter_downloader.py -t 8 <URL1> <URL2> <URL3>
   ```

## Cookie Setup

To download protected tweets, create a `cookies.txt` file containing:
- `auth_token`
- `ct0`

### How to get cookies:
1. Login to Twitter/X in your browser
2. Use a cookie exporter extension (e.g. "Get cookies.txt" for Chrome)
3. Export cookies in Netscape format or simple `key=value` format

Example cookies.txt:
```
auth_token=abc123def456
ct0=xyz789
```

## Output Templates

Available template variables:
- `%(title)s`: Post text (sanitized)
- `%(id)s`: Tweet ID
- `%(uploader)s`: Author username
- `%(ext)s`: File extension (mp4)
- `%(upload_date)s`: Post date in YYYYMMDD format

Example:
```bash
-o "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"
```

## Common Issues

1. **Invalid URLs**  
   Ensure URLs match format:  
   `https://(twitter.com|x.com)/username/status/1234567890`

2. **Cookie Errors**  
   Verify cookies.txt contains both `auth_token` and `ct0`

3. **Download Failures**  
   - Try reducing thread count (`-t 2`)
   - Check account permissions for protected tweets
   - Ensure sufficient storage space

## Notes

- Rate limiting may occur with too many parallel requests (4-8 threads recommended)
- Add `--quiet` to suppress progress output if needed
- Files will be overwritten if same filename exists
