import streamlit as st
import os
import asyncio
import logging
from urllib.parse import urlparse, urljoin
import tempfile
import zipfile
import io
from crawler import get_all_links, crawl_content
from clean_md import process_files

# Thêm vào đầu file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('crawler.log')
    ]
)

class DocumentationSpider:
    def __init__(self, url, output_dir):
        self.start_url = url
        self.output_dir = output_dir
        self.visited_urls = set()
        # Tự động trích xuất path từ URL
        parsed_url = urlparse(url)
        path_parts = parsed_url.path.split('/')
        if len(path_parts) > 2:  # Có path cụ thể
            # Lấy path đến thư mục cha
            self.base_path = '/'.join(path_parts[:-1])
        else:
            self.base_path = None

    async def crawl(self):
        try:
            # Lấy danh sách links
            links = get_all_links(self.start_url, self.base_path)
            if not links:
                logging.error("No links found")
                return False
            
            # Lưu danh sách URLs vào file
            urls_file = os.path.join(self.output_dir, "found_urls.txt")
            with open(urls_file, "w", encoding="utf-8") as f:
                f.write(f"Base URL: {self.start_url}\n")
                f.write(f"Base Path: {self.base_path}\n")
                f.write(f"Found {len(links)} URLs:\n\n")
                for link in links:
                    f.write(f"{link}\n")
                
            st.write(f"Found {len(links)} links to crawl")
            
            # Crawl từng link với progress bar
            progress_bar = st.progress(0)
            crawl_log = []
            
            for i, link in enumerate(links):
                if link not in self.visited_urls:
                    result = await self.crawl_page(link)
                    status = "Success" if result else "Failed"
                    crawl_log.append(f"{status}: {link}")
                    self.visited_urls.add(link)
                    # Update progress
                    progress_bar.progress((i + 1) / len(links))
            
            # Lưu log crawl
            log_file = os.path.join(self.output_dir, "crawl_log.txt")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write("Crawl Log:\n\n")
                for log in crawl_log:
                    f.write(f"{log}\n")
            
            return True
        except Exception as e:
            logging.error(f"Error during crawling: {str(e)}")
            return False

    async def crawl_page(self, url):
        try:
            filepath = crawl_content(url, self.output_dir)
            if filepath:
                # Thêm URL gốc vào đầu file
                with open(filepath, "r+", encoding="utf-8") as f:
                    content = f.read()
                    f.seek(0)
                    f.write(f"Source URL: {url}\n\n{content}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error crawling {url}: {str(e)}")
            return False

def create_zip_file(directory):
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Đảm bảo tất cả các file được thêm vào
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, directory)
                try:
                    zipf.write(file_path, arcname)
                except Exception as e:
                    st.error(f"Error adding {file} to zip: {str(e)}")
    memory_file.seek(0)
    return memory_file

def main():
    st.title("Documentation Crawler")
    
    # Chỉ cần nhập URL
    url = st.text_input("Enter URL (e.g., https://example.com/stories/story1):", 
                       help="Enter the URL. If it contains a specific path, only links under that path will be crawled.")
    
    if st.button("Start Crawling"):
        if url:
            with st.spinner("Crawling in progress..."):
                try:
                    # Tạo thư mục tạm thời
                    with tempfile.TemporaryDirectory() as temp_dir:
                        # Setup folders
                        domain = urlparse(url).netloc
                        raw_folder = os.path.join(temp_dir, "raw")
                        cleaned_folder = os.path.join(temp_dir, "cleaned")
                        os.makedirs(raw_folder, exist_ok=True)
                        os.makedirs(cleaned_folder, exist_ok=True)
                        
                        # Initialize và run spider
                        spider = DocumentationSpider(url, raw_folder)
                        success = asyncio.run(spider.crawl())
                        
                        if success:
                            # Process và clean files
                            st.write("Crawling completed. Processing files...")
                            processed = process_files(raw_folder, cleaned_folder)
                            st.write(f"Processed {processed} files")
                            
                            # Create ZIP file
                            zip_file = create_zip_file(temp_dir)
                            
                            # Provide download button
                            st.download_button(
                                label="Download Results",
                                data=zip_file,
                                file_name=f"{domain}_crawled_data.zip",
                                mime="application/zip"
                            )
                            
                            st.success("""
                            Crawling and processing completed! The ZIP file contains:
                            - found_urls.txt: List of all URLs found
                            - crawl_log.txt: Crawling status for each URL
                            - raw/: Raw content files with source URLs
                            - cleaned/: Cleaned content files
                            """)
                        else:
                            st.error("Crawling failed. Please check the URL and try again.")
                            
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
        else:
            st.error("Please enter a URL")

if __name__ == "__main__":
    main() 