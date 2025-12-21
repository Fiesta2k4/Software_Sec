import os
import csv
import subprocess

# --- CẤU HÌNH ---
# File CSV chứa kết quả fuzzing
CSV_FILE = "radamsa_tiffcp_results.csv"

# Đường dẫn đến file tiffcp đã được instrument
TIFFCP_BIN = "/home/miud0211/Software_Sec/libtiff_work/tiff-4.0.4-sanitized/install-sanitized/bin/tiffcp"

# Thư mục chứa các file TIFF đã được fuzz
INPUT_DIR = "./rad_out_tiffcp"

# Thư mục để lưu các file log lỗi chi tiết
LOG_DIR = "./error_logs"
# --- HẾT CẤU HÌNH ---


def main():
    """Hàm chính để tìm file lỗi và thu thập log."""
    print("--- Bắt đầu script thu thập log lỗi chi tiết ---")

    # 1. Kiểm tra các file và thư mục cần thiết
    if not os.path.exists(CSV_FILE):
        print(f"Lỗi: Không tìm thấy file kết quả '{CSV_FILE}'!")
        return
    if not os.path.exists(TIFFCP_BIN):
        print(f"Lỗi: Không tìm thấy file thực thi '{TIFFCP_BIN}'!")
        return

    # 2. Tạo thư mục chứa log nếu chưa có
    os.makedirs(LOG_DIR, exist_ok=True)
    print(f"Các file log sẽ được lưu trong thư mục: '{LOG_DIR}'")

    # 3. Đọc file CSV và tìm ra các file gây lỗi sanitizer
    guilty_files = []
    with open(CSV_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Chúng ta chỉ quan tâm đến các file có lỗi sanitizer
            if row.get('sanitizer_bug') == 'YES':
                guilty_files.append(row['file'])
    
    if not guilty_files:
        print("Không tìm thấy file nào có lỗi sanitizer trong file CSV. Dừng lại.")
        return

    total_files = len(guilty_files)
    print(f"Tìm thấy {total_files} file có lỗi sanitizer. Bắt đầu xử lý...")
    print("-" * 50)

    # 4. Lặp qua từng file lỗi và chạy lại để lấy log
    for i, filename in enumerate(guilty_files, 1):
        input_path = os.path.join(INPUT_DIR, filename.strip())
        log_path = os.path.join(LOG_DIR, filename.strip() + ".log")

        print(f"[{i}/{total_files}] Đang xử lý: {filename.strip()}")
        
        if not os.path.exists(input_path):
            print(f"  -> Cảnh báo: Không tìm thấy file '{input_path}'. Bỏ qua.")
            continue

        # Chạy lệnh và bắt output lỗi (stderr)
        command = [TIFFCP_BIN, input_path, "/dev/null"]
        proc = subprocess.run(command, capture_output=True, text=True)
        
        # Ghi toàn bộ stderr vào file log
        with open(log_path, 'w') as log_file:
            log_file.write(proc.stderr)

    print("-" * 50)
    print("Hoàn thành! Tất cả các log đã được thu thập thành công.")
    print(f"Bây giờ bạn có thể xem các file trong thư mục '{LOG_DIR}' và gửi chúng để phân tích.")

if __name__ == "__main__":
    main()
