import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import time
import logging

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_all_links(base_url, path=None):
    links = set()
    try:
        response = requests.get(base_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các link chapter trong phần "Chương Truyện"
        chapter_list = soup.select('.wp-manga-chapter a') or \
                      soup.select('.chapter-list a') or \
                      soup.select('.chapters a') or \
                      soup.select('.wp-manga-chapter a') or \
                      soup.select('ul.list-chapter li a')
        
        for a_tag in chapter_list:
            href = a_tag.get('href')
            if href:
                full_url = urljoin(base_url, href)
                # Nếu có path được chỉ định, chỉ lấy URL có chứa path đó
                if path is None or path in full_url:
                    links.add(full_url)
                
    except Exception as e:
        logging.error(f"Error fetching links: {e}")
    
    return sorted(list(links))

def crawl_content(url, output_dir):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'  # Chỉ định encoding là utf-8
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm nội dung chính - thử nhiều selector khác nhau
        content = None
        selectors = [
            'article.reading-content',
            '.chapter-content',
            '#chapter-content',
            '.content-story',
            '.story-content',
            '.content',
            '#content',
            '.reading-content',
            '.text-left'
        ]
        
        for selector in selectors:
            content = soup.select_one(selector)
            if content:
                break
                
        if content:
            # Tạo tên file từ URL
            filename = f"doc_{urlparse(url).path.strip('/').replace('/', '_')}.md"
            filepath = os.path.join(output_dir, filename)
            
            # Xử lý và làm sạch nội dung
            text_content = content.get_text(separator='\n\n', strip=True)
            
            # Loại bỏ các ký tự đặc biệt và chuẩn hóa unicode
            import unicodedata
            text_content = unicodedata.normalize('NFKC', text_content)
            
            # Lưu nội dung với encoding utf-8
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            return filepath
            
    except Exception as e:
        logging.error(f"Error crawling {url}: {str(e)}")
        return None 