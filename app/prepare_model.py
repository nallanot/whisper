"""Download weights once; use cached weights on later deployments."""
from faster_whisper import WhisperModel

options = dict(device="cpu", compute_type="int8", download_root="/models")
try:
    model = WhisperModel("small", local_files_only=True, **options)
except (FileNotFoundError, OSError, ValueError, RuntimeError):
    model = WhisperModel("small", local_files_only=False, **options)
print("Whisper small prêt.")
