import asyncio
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from config import Config
from crawler.spider import DocumentationSpider
from crawler.utils import create_directory
import threading

class CrawlerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Documentation Crawler")
        
        # URL Input
        url_frame = ttk.Frame(root, padding="5")
        url_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Label(url_frame, text="Documentation URL:").grid(row=0, column=0, sticky=tk.W)
        self.url_var = tk.StringVar(value="https://docs.prefect.io/v3/")
        ttk.Entry(url_frame, textvariable=self.url_var, width=50).grid(row=0, column=1, padx=5)
        
        # Output Directory
        dir_frame = ttk.Frame(root, padding="5")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        ttk.Label(dir_frame, text="Output Directory:").grid(row=0, column=0, sticky=tk.W)
        self.dir_var = tk.StringVar(value="docs_output")
        ttk.Entry(dir_frame, textvariable=self.dir_var, width=50).grid(row=0, column=1, padx=5)
        
        # Progress
        self.progress_var = tk.StringVar(value="Ready to start...")
        ttk.Label(root, textvariable=self.progress_var).grid(row=2, column=0, pady=10)
        
        # Start Button
        ttk.Button(root, text="Start Crawling", command=self.start_crawling).grid(row=3, column=0, pady=10)
        
    def start_crawling(self):
        url = self.url_var.get().strip()
        output_dir = self.dir_var.get().strip()
        
        if not url or not output_dir:
            messagebox.showerror("Error", "Please enter both URL and output directory")
            return
            
        self.progress_var.set("Crawling started...")
        
        # Chạy crawler trong thread riêng
        thread = threading.Thread(target=self.run_crawler, args=(url, output_dir))
        thread.daemon = True
        thread.start()
        
    def run_crawler(self, url, output_dir):
        try:
            config = Config(start_url=url, output_dir=output_dir)
            create_directory(config.OUTPUT_DIR)
            
            spider = DocumentationSpider(config)
            asyncio.run(spider.crawl())
            
            self.progress_var.set("Crawling completed!")
            messagebox.showinfo("Success", "Documentation crawling completed!")
            
        except Exception as e:
            self.progress_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Crawling failed: {str(e)}")

def main():
    root = tk.Tk()
    app = CrawlerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 