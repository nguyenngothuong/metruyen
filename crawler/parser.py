import html2text
from bs4 import BeautifulSoup

class HTMLToMarkdownParser:
    def __init__(self):
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        self.h2t.ignore_images = False
        self.h2t.ignore_tables = False
        self.h2t.body_width = 0
        
    def clean_html(self, soup):
        # Xóa các phần tử không cần thiết
        for element in soup.find_all(['script', 'style', 'nav', 'footer']):
            element.decompose()
            
        # Xóa các class không cần thiết
        for element in soup.find_all(class_=['sidebar', 'menu', 'advertisement']):
            element.decompose()
            
        return soup
    
    def convert(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        cleaned_soup = self.clean_html(soup)
        
        # Lấy phần content chính của Prefect docs
        main_content = cleaned_soup.find('main') or cleaned_soup
        
        # Chuyển đổi sang markdown
        markdown = self.h2t.handle(str(main_content))
        
        # Thêm tiêu đề
        title = soup.title.string if soup.title else "Untitled"
        markdown = f"# {title}\n\n{markdown}"
        
        return markdown 