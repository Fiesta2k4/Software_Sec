Crash: NULL dereference in TIFFFillStrip() when printing error message.
Location: libtiff/tif_read.c:565
Cause: td->td_stripoffset is NULL but code reads td->td_stripoffset[strip]
Triggered via tiffcp -> TIFFReadScanline -> TIFFFillStrip error path.
