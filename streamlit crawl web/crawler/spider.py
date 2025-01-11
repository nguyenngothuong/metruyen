import asyncio
import aiohttp
import os
import ssl
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from .parser import HTMLToMarkdownParser
from .utils import get_relative_path, setup_logging
import sqlite3
from aiohttp import ClientTimeout
from asyncio import Semaphore
import random

logger = setup_logging()

class DocumentationSpider:
    def __init__(self, config):
        self.config = config
        self.parser = HTMLToMarkdownParser()
        self.session = None
        self.db_conn = self._init_db()
        
        # Rate limiting
        self.semaphore = Semaphore(self.config.MAX_WORKERS)
        self.last_request_time = 0
        self.min_delay = self.config.REQUEST_DELAY
        self.max_delay = self.config.REQUEST_DELAY * 2
        
        # Lấy base path từ start_url để kiểm tra subdomain
        parsed = urlparse(self.config.START_URL)
        self.base_domain = parsed.netloc
        self.base_path = parsed.path.rstrip('/')
        
    def is_valid_url(self, url):
        """Kiểm tra URL có thuộc subdomain được chỉ định không"""
        try:
            parsed = urlparse(url)
            # Kiểm tra domain
            if parsed.netloc != self.base_domain:
                return False
                
            # Kiểm tra path có bắt đầu bằng base_path
            if not parsed.path.startswith(self.base_path):
                return False
                
            return True
        except:
            return False

    def _init_db(self):
        db_path = os.path.join(self.config.OUTPUT_DIR, 'crawled_urls.db')
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS crawled_urls
                     (url TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        return conn

    async def fetch_with_retry(self, url, max_retries=3):
        timeout = ClientTimeout(total=30)
        
        for attempt in range(max_retries):
            try:
                # Rate limiting
                now = asyncio.get_event_loop().time()
                time_since_last = now - self.last_request_time
                if time_since_last < self.min_delay:
                    delay = random.uniform(self.min_delay, self.max_delay)
                    await asyncio.sleep(delay)
                
                async with self.semaphore:
                    async with self.session.get(url, 
                                              headers=self.config.HEADERS,
                                              timeout=timeout) as response:
                        self.last_request_time = asyncio.get_event_loop().time()
                        
                        if response.status == 429:
                            retry_after = int(response.headers.get('Retry-After', 5))
                            await asyncio.sleep(retry_after)
                            continue
                            
                        response.raise_for_status()
                        return await response.text()
                        
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                logger.warning(f"Attempt {attempt + 1} failed for {url}. Retrying in {wait_time:.2f}s... Error: {str(e)}")
                await asyncio.sleep(wait_time)

    async def is_url_crawled(self, url):
        c = self.db_conn.cursor()
        c.execute('SELECT url FROM crawled_urls WHERE url = ?', (url,))
        return c.fetchone() is not None

    async def mark_url_crawled(self, url):
        c = self.db_conn.cursor()
        c.execute('INSERT OR REPLACE INTO crawled_urls (url) VALUES (?)', (url,))
        self.db_conn.commit()

    async def save_markdown(self, url, markdown):
        filename = get_relative_path(url, self.config.START_URL)
        filepath = os.path.join(self.config.OUTPUT_DIR, f"{filename}.md")
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)
        logger.info(f"Saved: {filepath}")

    def extract_links(self, soup, base_url):
        links = set()
        for a in soup.find_all('a', href=True):
            url = a['href']
            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            if self.is_valid_url(url):  # Chỉ lấy URL thuộc subdomain
                links.add(url)
        return links

    async def process_url(self, url):
        if not self.is_valid_url(url):
            logger.info(f"Skipping invalid URL: {url}")
            return
            
        if await self.is_url_crawled(url):
            logger.info(f"Skipping already crawled URL: {url}")
            return
            
        try:
            html = await self.fetch_with_retry(url)
            soup = BeautifulSoup(html, 'html.parser')
            markdown = self.parser.convert(html)
            
            await self.save_markdown(url, markdown)
            await self.mark_url_crawled(url)
            
            links = self.extract_links(soup, url)
            tasks = []
            for link in links:
                if not await self.is_url_crawled(link):
                    tasks.append(self.process_url(link))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
        except Exception as e:
            logger.error(f"Error processing {url}: {str(e)}")

    async def crawl(self):
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        conn = aiohttp.TCPConnector(
            ssl=ssl_context,
            limit=self.config.MAX_WORKERS,
            force_close=True
        )
        
        async with aiohttp.ClientSession(connector=conn) as session:
            self.session = session
            try:
                await self.process_url(self.config.START_URL)
            except Exception as e:
                logger.error(f"Crawl failed: {str(e)}")
            finally:
                self.session = None 