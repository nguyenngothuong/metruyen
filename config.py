class Config:
    def __init__(self, start_url=None, output_dir=None):
        # URL gốc của documentation
        self.START_URL = start_url or "https://docs.prefect.io/v3/"
        
        # Thư mục lưu file markdown
        self.OUTPUT_DIR = output_dir or "docs_output"
        
        # Rate limiting config
        self.REQUEST_DELAY = 1.5  # Delay tối thiểu giữa các request
        self.MAX_WORKERS = 3      # Số worker đồng thời tối đa
        
        # Headers để request
        self.HEADERS = {
            "User-Agent": "Mozilla/5.0 (compatible; DocumentationBot/1.0;)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        }
        
        # Pattern URL mặc định - sẽ được cập nhật dựa trên start_url
        self.URL_PATTERNS = []
        self._update_url_patterns()
        
    def _update_url_patterns(self):
        if self.START_URL:
            # Tạo pattern từ start_url
            domain = self.START_URL.split('/')[2]  # Lấy domain từ URL
            self.URL_PATTERNS = [
                f"^https?://{domain}/.*$"
            ] 