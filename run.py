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
    print("\n" + "="*50)
    print(f"🚀 MULTI-AGENT BACKEND IS LIVE ON http://127.0.0.1:{port}")
    print("="*50 + "\n")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
