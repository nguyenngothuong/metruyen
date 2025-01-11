import os
import re
import unicodedata

def clean_story_content(content):
    # Chuẩn hóa unicode và loại bỏ các ký tự đặc biệt
    content = unicodedata.normalize('NFKC', content)
    
    # Loại bỏ các phần header và navigation
    content = re.sub(r'^.*?\[Chương sau\].*?\n', '', content, flags=re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', content)
    content = re.sub(r'<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>', '', content)
    
    # Loại bỏ URLs và links
    content = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', content)
    content = re.sub(r'\[.*?\]\(.*?\)', '', content)
    content = re.sub(r'!\[.*?\]\(.*?\)', '', content)
    
    # Tách nội dung thành các dòng và làm sạch
    lines = []
    for line in content.split('\n'):
        line = line.strip()
        if line and not line.startswith('__') and not line.startswith('*'):
            # Loại bỏ các dòng chỉ có số hoặc ký tự đặc biệt
            if not re.match(r'^[\d\s\.,!?"-:;\']+$', line):
                # Loại bỏ khoảng trắng thừa
                line = re.sub(r'\s+', ' ', line)
                lines.append(line)
    
    # Xử lý các đoạn văn
    cleaned_lines = []
    current_line = []
    
    for line in lines:
        # Nếu là tiêu đề chapter, source URL hoặc dòng đặc biệt, giữ nguyên
        if (line.startswith('Chương') or 
            line.startswith('Source URL:') or 
            len(line) < 20 or
            re.match(r'^\d+\.$', line)):  # Số đánh dấu phần
            
            # Thêm đoạn đang xử lý (nếu có)
            if current_line:
                cleaned_lines.append(' '.join(current_line))
                current_line = []
            
            # Thêm dòng đặc biệt
            cleaned_lines.append(line)
            
        else:
            # Nếu dòng kết thúc bằng dấu câu, kết thúc đoạn
            if line[-1] in '.!?':
                current_line.append(line)
                cleaned_lines.append(' '.join(current_line))
                current_line = []
            else:
                current_line.append(line)
    
    # Thêm đoạn cuối cùng nếu có
    if current_line:
        cleaned_lines.append(' '.join(current_line))
    
    # Kết hợp các dòng với khoảng cách phù hợp
    content = ''
    for i, line in enumerate(cleaned_lines):
        if i > 0:
            # Thêm 2 dòng trống trước chapter mới hoặc phần mới
            if line.startswith('Chương') or re.match(r'^\d+\.$', line):
                content += '\n\n\n'
            # Thêm 1 dòng trống giữa các đoạn văn
            else:
                content += '\n\n'
        content += line
    
    return content.strip()

def process_files(input_dir, output_dir):
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all .md files in input directory
    processed = 0
    for filename in os.listdir(input_dir):
        if filename.endswith('.md'):
            try:
                # Setup paths
                input_path = os.path.join(input_dir, filename)
                cleaned_filename = f'cleaned_{filename}'
                output_path = os.path.join(output_dir, cleaned_filename)
                
                # Read and clean content
                with open(input_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                cleaned_content = clean_story_content(content)
                
                # Save cleaned text
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                processed += 1
                print(f"Processed: {filename} -> {cleaned_filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                
    return processed

if __name__ == '__main__':
    input_dir = './raw'  # Input directory containing the files to clean
    output_dir = './cleaned'  # Output directory for cleaned files
    process_files(input_dir, output_dir) 