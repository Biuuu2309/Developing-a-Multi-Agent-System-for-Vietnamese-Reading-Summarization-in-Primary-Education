# ================================================================
# monitor_server.py — chạy trên vast.ai
# Expose training log qua HTTP để dashboard đọc
# Chạy: python monitor_server.py &
# ================================================================

import json, os, re
from http.server import HTTPServer, BaseHTTPRequestHandler

LOG_FILE    = "/workspace/training.log"
PARAMS_FILE = "/workspace/outputs/best_params.json"

def parse_log():
    if not os.path.exists(LOG_FILE):
        return {"status": "waiting", "trials": [], "current": {}, "vram": [], "best": None}

    with open(LOG_FILE, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    trials   = []
    vram     = []
    best     = None
    current  = {}
    status   = "running"
    final_started = False

    for line in lines:
        # Trial kết thúc
        m = re.search(r"Trial #(\d+)/\d+ \| Score: ([\d.]+) \| Best: ([\d.]+)", line)
        if m:
            trials.append({
                "number": int(m.group(1)),
                "score":  float(m.group(2)),
                "best":   float(m.group(3)),
            })
            best = float(m.group(3))

        # VRAM log
        m = re.search(r"VRAM \[(.+?)\] allocated=([\d.]+)GB \| reserved=([\d.]+)GB", line)
        if m:
            vram.append({
                "tag":      m.group(1),
                "allocated": float(m.group(2)),
                "reserved":  float(m.group(3)),
            })

        # Trial score trong log
        m = re.search(r"Trial (\d+) best avg_rouge = ([\d.]+)", line)
        if m:
            current["last_trial"]       = int(m.group(1))
            current["last_trial_score"] = float(m.group(2))

        # Epoch loss/rouge
        m = re.search(r"'eval_avg_rouge': ([\d.]+)", line)
        if m:
            current["last_eval_rouge"] = float(m.group(1))

        # Final training started
        if "Starting final training" in line:
            final_started = True
            status = "final_training"

        # All done
        if "All done!" in line:
            status = "done"

    if not final_started and status == "running":
        status = "optuna"

    # Đọc best params nếu có
    best_params = None
    if os.path.exists(PARAMS_FILE):
        try:
            with open(PARAMS_FILE) as f:
                best_params = json.load(f)
        except Exception:
            pass

    # Last 20 VRAM entries
    vram_latest = vram[-1] if vram else None

    return {
        "status":      status,
        "trials":      trials,
        "total_trials": 20,
        "current":     current,
        "vram":        vram_latest,
        "best_score":  best,
        "best_params": best_params,
        "log_lines":   lines[-60:],  # 60 dòng log cuối
    }

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        if self.path == "/api":
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(parse_log()).encode())
        else:
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"ViT5 Monitor API - truy cap /api")

    def log_message(self, *args):
        pass  # tắt access log

print("Monitor server chạy tại port 8765")
print("Truy cập: http://<vast-ip>:<port>/api")
HTTPServer(("0.0.0.0", 8765), Handler).serve_forever()
