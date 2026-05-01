import webbrowser
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

DISCORD_CLIENT_ID = "1454371400876949576"
REDIRECT_URI = "http://localhost:8765/callback"

auth_code = None

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        auth_code = params.get("code", [None])[0]

        self.send_response(200)
        self.send_header("Content-type", "text/html") 
        self.end_headers()

        html = """
        <html>
        <head>
        <style>
        body {
            margin: 0;
            height: 100vh;
            background-image: url('https://i.imgur.com/97g13LX.png');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-color: #0b0f1a;
        }
        </style>
        </head>
        <body></body>
        </html>
        """

        self.wfile.write(html.encode())

    def log_message(self, *args):
        pass

def login() -> str | None:
    global auth_code
    auth_code = None

    auth_url = (
        f"https://discord.com/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&response_type=code"
        f"&scope=identify"
    )
    webbrowser.open(auth_url)

    server = HTTPServer(("localhost", 8765), OAuthHandler)
    server.handle_request()

    return auth_code 