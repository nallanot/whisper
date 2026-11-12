import os
import sys
from faster_whisper import WhisperModel

model = WhisperModel(os.getenv("WHISPER_MODEL", "small"), device="cpu",
                     compute_type="int8", cpu_threads=int(os.getenv("CPU_THREADS", "4")),
                     download_root="/models", local_files_only=True)
segments, info = model.transcribe(sys.argv[1], language=None if sys.argv[3] == "auto" else sys.argv[3],
                                  vad_filter=True, beam_size=5)
with open(sys.argv[2], "w", encoding="utf-8") as output:
    for segment in segments:
        start = int(segment.start)
        output.write(f"[{start // 3600:02d}:{start // 60 % 60:02d}:{start % 60:02d}] {segment.text.strip()}\n")
