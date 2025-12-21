import subprocess
import glob
import csv
import os

# --- CẤU HÌNH ---
# THAY ĐỔI 1: Đường dẫn đến file tiffcp đã build với sanitizer
TIFFCP_BIN = "/home/miud0211/Software_Sec/libtiff_work/tiff-4.0.4-sanitized/install-sanitized/bin/tiffcp"

# THAY ĐỔI 2: Thư mục chứa các file fuzz dành cho tiffcp
INPUT_DIR = "./rad_out_tiffcp"

# THAY ĐỔI 3: Tên file CSV kết quả mới
RESULT_CSV = "radamsa_tiffcp_results.csv"

# Nơi để ghi file output (không tạo file rác)
OUTPUT_NULL = "/dev/null"
# --- HẾT CẤU HÌNH ---


# Tìm tất cả các file .tiff trong thư mục input
files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.tiff")))

print(f"Tìm thấy {len(files)} file trong '{INPUT_DIR}'")

# Mở file CSV để ghi kết quả
with open(RESULT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    # Ghi dòng tiêu đề
    writer.writerow(["file", "return_code", "crashed", "sanitizer_bug"])

    # Lặp qua từng file
    for i, path in enumerate(files, 1):
        # Thiết lập môi trường để ASan/UBSan báo lỗi chi tiết
        env = os.environ.copy()
        env["ASAN_OPTIONS"] = "abort_on_error=1"
        env["UBSAN_OPTIONS"] = "print_stacktrace=1"

        # THAY ĐỔI 4: Cú pháp lệnh cho tiffcp là `tiffcp <input> <output>`
        command = [TIFFCP_BIN, path, OUTPUT_NULL]

        proc = subprocess.run(
            command,
            stdout=subprocess.DEVNULL, # Bỏ qua output chuẩn
            stderr=subprocess.PIPE,     # Bắt lỗi chuẩn để phân tích
            env=env
        )

        # Phân tích kết quả trả về
        rc = proc.returncode
        stderr = proc.stderr.decode(errors="ignore")

        crashed = "YES" if rc != 0 else "NO"
        sanitizer_bug = "NO"
        if "AddressSanitizer" in stderr or "runtime error:" in stderr:
            sanitizer_bug = "YES"

        # Ghi kết quả vào file CSV
        writer.writerow([os.path.basename(path), rc, crashed, sanitizer_bug])

        # In tiến trình mỗi 500 file
        if i % 500 == 0 or i == len(files):
            print(f"Đã xử lý {i}/{len(files)} file")

print(f"Hoàn thành! Kết quả đã được lưu vào '{RESULT_CSV}'")
