# Metruyen - Công cụ Crawl Truyện

Metruyen là một công cụ crawl dữ liệu truyện với giao diện web được xây dựng bằng Streamlit. Công cụ này cho phép người dùng crawl nội dung từ các trang web truyện và xuất ra định dạng markdown.

## Tính năng chính

- Crawl nội dung truyện từ URL được cung cấp
- Tự động phát hiện và crawl các chương liên quan
- Làm sạch và định dạng nội dung sang markdown
- Giao diện web thân thiện với người dùng
- Xuất kết quả dưới dạng file ZIP

## Yêu cầu hệ thống

- Python 3.11 trở lên
- pip (Python package manager)

## Cài đặt

1. Clone repository về máy:

git clone https://github.com/nguyenngothuong/metruyen.git
cd metruyen

2. Tạo môi trường ảo (khuyến nghị):

# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

3. Cài đặt các thư viện cần thiết:

pip install -r requirements.txt

## Cách sử dụng

1. Khởi động ứng dụng:

streamlit run app.py

2. Truy cập ứng dụng qua trình duyệt:
- Mặc định: http://localhost:8501

3. Sử dụng:
- Nhập URL của truyện cần crawl
- Nhấn "Start Crawling" để bắt đầu
- Đợi quá trình crawl hoàn tất
- Tải file ZIP kết quả về

## Cấu trúc thư mục

metruyen/
├── .devcontainer/        # Cấu hình container dev
├── crawler/             # Module crawler
│   ├── parser.py       # Xử lý parse HTML
│   ├── spider.py       # Logic crawl chính
│   └── utils.py        # Các utility functions
├── app.py              # Ứng dụng Streamlit
├── clean_md.py         # Xử lý làm sạch markdown
├── config.py           # Cấu hình
└── requirements.txt    # Các dependency

## File kết quả

Sau khi crawl xong, bạn sẽ nhận được file ZIP chứa:

- found_urls.txt: Danh sách các URL đã tìm thấy
- crawl_log.txt: Log quá trình crawl
- Thư mục raw/: Nội dung gốc đã crawl
- Thư mục cleaned/: Nội dung đã được làm sạch

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới (git checkout -b feature/AmazingFeature)
3. Commit thay đổi (git commit -m 'Add some AmazingFeature')
4. Push lên branch (git push origin feature/AmazingFeature)
5. Tạo Pull Request

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. Xem LICENSE để biết thêm chi tiết.

## Liên hệ

Nguyễn Ngọ Thưởng - [@nguyenngothuong](https://github.com/nguyenngothuong)

Project Link: [https://github.com/nguyenngothuong/metruyen](https://github.com/nguyenngothuong/metruyen)
