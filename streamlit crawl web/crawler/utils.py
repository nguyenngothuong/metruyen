import os
import re
import logging
from urllib.parse import urljoin, urlparse

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('crawler.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def is_valid_url(url, patterns):
    for pattern in patterns:
        if re.match(pattern, url):
            return True
    return False

def sanitize_filename(title):
    # Xóa các ký tự không hợp lệ trong tên file
    filename = re.sub(r'[^\w\s-]', '', title.lower())
    filename = re.sub(r'[-\s]+', '-', filename).strip('-_')
    return f"{filename}.md"

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_relative_path(url, base_url):
    parsed_url = urlparse(url)
    path = parsed_url.path.strip('/')
    if path:
        return path.replace('/', '_')
    return 'index' 