import csv
import random
from collections import Counter

CSV_FILE = "radamsa_tiff2pdf_results.csv"

both_yes = []      # crashed=YES, sanitizer_bug=YES
mixed = []         # one YES, one NO
both_no = []       # crashed=NO, sanitizer_bug=NO

total = 0
crashed_yes = 0
crashed_no = 0
san_yes = 0
san_no = 0

crash_and_san = 0
crash_no_san = 0

return_codes = Counter()

with open(CSV_FILE, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total += 1

        rc = int(row["return_code"])
        crashed = row["crashed"].strip().upper()
        san_bug = row["sanitizer_bug"].strip().upper()

        return_codes[rc] += 1

        if crashed == "YES":
            crashed_yes += 1
        else:
            crashed_no += 1

        if san_bug == "YES":
            san_yes += 1
        else:
            san_no += 1

        if crashed == "YES" and san_bug == "YES":
            crash_and_san += 1
        elif crashed == "YES" and san_bug == "NO":
            crash_no_san += 1

print("=== Summary of fuzz results ===")
print(f"Total test cases           : {total}")
print(f"Crashed = YES              : {crashed_yes}")
print(f"Crashed = NO               : {crashed_no}")
print(f"Sanitizer bug = YES        : {san_yes}")
print(f"Sanitizer bug = NO         : {san_no}")
print()
print(f"Crashed & Sanitizer bug YES: {crash_and_san}")
print(f"Crashed & Sanitizer bug NO : {crash_no_san}")
print()
print("Return code distribution:")
for rc, count in sorted(return_codes.items()):
    print(f"  rc={rc:4d}  -> {count} cases")


with open(CSV_FILE, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        c = row["crashed"].strip().upper()
        s = row["sanitizer_bug"].strip().upper()

        if c == "YES" and s == "YES":
            both_yes.append(row)
        elif c == "NO" and s == "NO":
            both_no.append(row)
        else:
            # c != s  => 1 YES, 1 NO
            mixed.append(row)

def pick_some(lst, k=3):
    if not lst:
        return []
    if len(lst) <= k:
        return lst
    return random.sample(lst, k)

print("=== Random examples (crashed=YES, sanitizer_bug=YES) ===")
for r in pick_some(both_yes, 3):
    print(f"{r['file']},{r['return_code']},{r['crashed']},{r['sanitizer_bug']}")

print("\n=== Random examples (one YES, one NO) ===")
for r in pick_some(mixed, 3):
    print(f"{r['file']},{r['return_code']},{r['crashed']},{r['sanitizer_bug']}")

print("\n=== Random examples (crashed=NO, sanitizer_bug=NO) ===")
for r in pick_some(both_no, 3):
    print(f"{r['file']},{r['return_code']},{r['crashed']},{r['sanitizer_bug']}")