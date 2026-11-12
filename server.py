"""
Moneyball VB - Mobile Web Application Server.
Standard-library based HTTP server with JSON API.
"""
import os
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from engine.optimizer import load_players
from engine.mobile_optimizer import DynamicOptimizer
from engine.models import Player

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8080
STATIC_DIR = os.path.join(BASE_DIR, "static")
PLAYERS_FILE = os.path.join(BASE_DIR, "players.json")
GAMES_FILE = os.path.join(BASE_DIR, "games.json")

class MoneyballHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        url_path = self.path.split("?")[0]

        if url_path == "/api/players":
            try:
                with open(PLAYERS_FILE, "r") as f:
                    data = json.load(f)
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if url_path == "/api/games":
            try:
                if os.path.exists(GAMES_FILE):
                    with open(GAMES_FILE, "r") as f:
                        data = json.load(f)
                else:
                    data = {"games": []}
                self._send_json(data)
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if url_path == "/api/health":
            self._send_json({"status": "ok"})
            return

        # Serve static files
        clean_path = "index.html" if url_path in ("/", "") else url_path.lstrip("/")
        file_path = os.path.join(STATIC_DIR, clean_path)
        if not os.path.exists(file_path):
            file_path = os.path.join(os.path.dirname(__file__), clean_path)

        if os.path.exists(file_path) and os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            mime_type = mime_type or "text/html"
            try:
                with open(file_path, "rb") as f:
                    content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", mime_type)
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                self.send_error(500, f"Error reading file: {e}")
        else:
            self.send_error(404, "File Not Found")

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)
        url_path = self.path.split("?")[0]

        try:
            body = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception as e:
            self._send_json({"error": f"Invalid JSON: {e}"}, status=400)
            return

        if url_path == "/api/players":
            # Save players
            try:
                with open(PLAYERS_FILE, "w") as f:
                    json.dump(body, f, indent=2)
                self._send_json({"success": True, "message": "Players saved successfully."})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        if url_path == "/api/optimize":
            try:
                # Load current players
                players = load_players(PLAYERS_FILE)
                optimizer = DynamicOptimizer(players)

                active_numbers = body.get("active_players", [p.name for p in players])
                tactical_bias = body.get("tactical_bias", "balanced")
                match_strategy = body.get("match_strategy", "balanced")
                set3_mode = body.get("set3_mode", "win")
                start_mode = body.get("start_mode", "serve")

                plan = optimizer.plan_match(
                    active_numbers=active_numbers,
                    tactical_bias=tactical_bias,
                    match_strategy=match_strategy,
                    set3_mode=set3_mode,
                    start_mode=start_mode
                )
                self._send_json({
                    "success": True,
                    "game_name": body.get("game_name", "Game Day"),
                    "opponent": body.get("opponent", "Opponent"),
                    "date": body.get("date", ""),
                    "plan": plan
                })
            except Exception as e:
                self._send_json({"error": str(e)}, status=400)
            return

        if url_path == "/api/games":
            try:
                # Save or update game in games.json
                games = []
                if os.path.exists(GAMES_FILE):
                    with open(GAMES_FILE, "r") as f:
                        data = json.load(f)
                        games = data.get("games", [])

                game_data = body
                # If game exists by id, update it, else append
                game_id = game_data.get("id")
                updated = False
                for i, g in enumerate(games):
                    if g.get("id") == game_id:
                        games[i] = game_data
                        updated = True
                        break
                if not updated:
                    games.insert(0, game_data)

                with open(GAMES_FILE, "w") as f:
                    json.dump({"games": games}, f, indent=2)

                self._send_json({"success": True, "message": "Game saved to history."})
            except Exception as e:
                self._send_json({"error": str(e)}, status=500)
            return

        self.send_error(404, "Endpoint Not Found")

def run_server(port=PORT):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServer(server_address, MoneyballHandler)
    print(f"🏐 St. Cecilia Volleyball Server running on http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
