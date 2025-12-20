# Software_Sec
WSL/Ubuntu Recommended
- crashes/: AFL++ unique crashes from fuzzing tiffcp
- stats/tiffcp/: fuzzer_stats + plot_data
- triage/: minimized testcase + ASan log
- bulk/: Excel triage sheet
- script/: Do the triage job

From libtiff_work/tiff-4.0.4, in order to build-asan:

mkdir build-asan
cd build-asan

CC=clang CXX=clang++ \
CFLAGS="-O1 -g -fno-omit-frame-pointer -fsanitize=address,undefined" \
LDFLAGS="-fsanitize=address,undefined" \
../configure --disable-shared --disable-dependency-tracking

make -j"$(nproc)"

After build, binary tool in: build-asan/tools/tiffcp

Reproduce the test case:

cd tiff-4.0.4/build-asan

ASAN_OPTIONS=abort_on_error=1:symbolize=1:detect_leaks=0 \
./tools/tiffcp ../triage/crash.min.tif /tmp/out.tif

If you want to minimize crash using afl-tmin:

afl-tmin -i <crash_file> -o crash.min.tif -- ./build-asan/tools/tiffcp @@ /tmp/out.tif

Run scripts and export Excel multiple crashes:

cd libtiff_work/tiff-4.0.4
python3 script/triage_bulk_asan.py \
  --mode tiffcp \
  --crash-dir crashes \
  --pattern 'id:*' \
  --target ./build-asan/tools/tiffcp \
  --timeout 5 \
  --out-dir triage_bulk/tiffcp \
  --xlsx triage_bulk/tiffcp/triage_tiffcp.xlsx \
  --keep-logs

After that you can start finding CVE