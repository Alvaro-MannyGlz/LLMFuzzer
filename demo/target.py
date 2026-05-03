from pathlib import Path
import sys

# Tiny crashable target for demo purposes.
# Crashes when the input contains the token b"CRASH".
input_path = Path(sys.argv[-1])
data = input_path.read_bytes()
print(f"Read {len(data)} bytes from {input_path}")
if b"CRASH" in data:
    raise RuntimeError("Demo crash triggered")
print("OK")
