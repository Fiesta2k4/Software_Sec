import subprocess, glob, csv, os

# Binary đã build với -fsanitize=address,undefined
TIFF2PDF_BIN = "/mnt/e/DH/20251/Software_Sec/Capstone_PJ/libtiff_work/tiff-4.0.4-sanitized/install-sanitized/bin/tiff2pdf"
INPUT_DIR = "/mnt/e/DH/20251/Software_Sec/Capstone_PJ/rad_out"
RESULT_CSV = "radamsa_tiff2pdf_results.csv"

files = sorted(glob.glob(os.path.join(INPUT_DIR, "*.tiff")))

print(f"Found {len(files)} files")

with open(RESULT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["file", "return_code", "crashed", "sanitizer_bug"])

    for i, path in enumerate(files, 1):
        env = os.environ.copy()
        # Cho ASan / UBSan in stacktrace rõ
        env["ASAN_OPTIONS"] = "abort_on_error=1"
        env["UBSAN_OPTIONS"] = "print_stacktrace=1"

        proc = subprocess.run(
            [TIFF2PDF_BIN, path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            env=env
        )

        rc = proc.returncode
        stderr = proc.stderr.decode(errors="ignore")

        crashed = "YES" if rc != 0 else "NO"
        sanitizer_bug = "NO"
        if "AddressSanitizer" in stderr or "runtime error:" in stderr:
            sanitizer_bug = "YES"

        writer.writerow([os.path.basename(path), rc, crashed, sanitizer_bug])

        if i % 500 == 0:
            print(f"Processed {i}/{len(files)} files")
