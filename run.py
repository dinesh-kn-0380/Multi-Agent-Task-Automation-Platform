import io
import os
import sys

# Force UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"), override=True)

from backend.api.server import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("[*] Multi-Agent Task Automation Platform")
    print(f"    Backend  -> http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=True, use_reloader=False)
