# Xero Client ID 86F233D613AF4B7EB6C25183035350F3
# URI http://localhost:8000/callback
# Secret vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd

# CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
# CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
#################
# import webbrowser
# from http.server import BaseHTTPRequestHandler, HTTPServer
# from urllib.parse import urlparse, parse_qs
#
# from xero_python.api_client import ApiClient, Configuration
# from xero_python.identity import IdentityApi
# from xero_python.accounting import AccountingApi
# from xero_python.api_client.oauth2 import OAuth2Token
#
# # ----------------------------
# # CONFIG
# # ----------------------------
# CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
# CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
# REDIRECT_URI = "http://localhost:8000/callback"
# PORT = 8000
#
# auth_code = None
#
# # ----------------------------
# # HTTP SERVER FOR OAUTH CALLBACK
# # ----------------------------
# class OAuthCallbackHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         global auth_code
#         parsed_url = urlparse(self.path)
#         if parsed_url.path == "/callback":
#             params = parse_qs(parsed_url.query)
#             auth_code = params.get("code")[0]
#             self.send_response(200)
#             self.send_header("Content-type", "text/html")
#             self.end_headers()
#             self.wfile.write(b"<html><body><h1>Authentication successful! You can close this tab.</h1></body></html>")
#         else:
#             self.send_response(404)
#             self.end_headers()
#
# # ----------------------------
# # Fetch balance sheet
# # ----------------------------
# def fetch_balance_sheet(api_client, access_token, tenant_id):
#     api_client.set_oauth2_token(access_token)
#     accounting_api = AccountingApi(api_client)
#     response = accounting_api.get_report_balance_sheet(
#         xero_tenant_id=tenant_id,
#         period="MONTH",
#         date="2025-12-01"
#     )
#     return response
#
# # ----------------------------
# # MAIN
# # ----------------------------
# def main():
#     global auth_code
#
#     # Step 1: Generate authorization URL manually
#     oauth = OAuth2Token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
#     authorize_url = oauth.get_authorization_url(
#         redirect_uri=REDIRECT_URI,
#         scopes=[
#             "openid",
#             "profile",
#             "email",
#             "accounting.reports.read",
#             "offline_access"
#         ]
#     )
#
#     print("Opening browser for login...")
#     webbrowser.open(authorize_url)
#
#     # Step 2: Wait for callback
#     server = HTTPServer(("localhost", PORT), OAuthCallbackHandler)
#     print(f"Waiting for OAuth callback on port {PORT}...")
#     while auth_code is None:
#         server.handle_request()
#
#     print("OAuth callback received.")
#
#     # Step 3: Exchange code for token
#     token_response = oauth.get_token(auth_code, redirect_uri=REDIRECT_URI)
#     access_token = token_response["access_token"]
#
#     # Step 4: Create API client
#     config = Configuration()
#     api_client = ApiClient(config)
#
#     # Step 5: Get connected tenants
#     identity_api = IdentityApi(api_client)
#     api_client.set_oauth2_token(access_token)
#     connections = identity_api.get_connections()
#     if not connections:
#         print("No Xero tenants found!")
#         return
#     tenant_id = connections[0].tenant_id
#     print(f"Using tenant: {tenant_id}")
#
#     # Step 6: Fetch balance sheet
#     report = fetch_balance_sheet(api_client, access_token, tenant_id)
#     print("Balance Sheet Report:")
#     print(report)
#
# if __name__ == "__main__":
#     main()



###########################################################################
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from xero_python.api_client.configuration import Configuration, OAuth2Token
from xero_python.api_client import ApiClient
from xero_python.accounting import AccountingApi


# ================================
# CONFIGURE THESE VALUES
# ================================
CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
REDIRECT_URI = "http://localhost:8000/callback"

SCOPES = [
    "openid",
    "profile",
    "email",
    "offline_access",
    "accounting.reports.read"
]

AUTH_URL = "https://login.xero.com/identity/connect/authorize"
TOKEN_URL = "https://identity.xero.com/connect/token"


# ==========================================================
# Global token storage
# ==========================================================
token_data = {}


# ==========================================================
# Minimal OAuth2 Callback Server
# ==========================================================
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global token_data

        if "/callback" not in self.path:
            self.send_response(404)
            self.end_headers()
            return

        # Grab ?code=XYZ
        query = self.path.split("?")[1]
        params = dict(kv.split("=") for kv in query.split("&"))
        code = params.get("code")

        # Exchange code for token
        import requests

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }

        response = requests.post(TOKEN_URL, data=data)
        token_data = response.json()

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Xero authentication successful. You can close this window.")

        # Stop server
        threading.Thread(target=self.server.shutdown).start()


# ==========================================================
# START AUTH FLOW
# ==========================================================
def authenticate():
    # Start local server
    server = HTTPServer(("localhost", 8000), OAuthHandler)
    threading.Thread(target=server.serve_forever).start()

    # Build login URL
    scope_str = " ".join(SCOPES)

    auth_url = (
        f"{AUTH_URL}"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={scope_str}"
    )

    print("Opening browser for login...")
    webbrowser.open(auth_url)

    print("Waiting for OAuth callback...")
    server.serve_forever()


# ==========================================================
# BUILD XERO API CLIENT
# ==========================================================
def build_xero_client():
    global token_data

    # Build OAuth2 token object for this SDK
    oauth2_token = OAuth2Token(
        access_token=token_data["access_token"],
        refresh_token=token_data.get("refresh_token"),
        expires_at=int(token_data["expires_in"]),
        token_type=token_data["token_type"]
    )

    config = Configuration(oauth2_token=oauth2_token)

    api_client = ApiClient(configuration=config)

    # Register token getter/saver
    @api_client.oauth2_token_getter
    def get_token():
        return token_data

    @api_client.oauth2_token_saver
    def save_token(new_token):
        global token_data
        token_data = new_token

    return AccountingApi(api_client)


# ==========================================================
# EXAMPLE: DOWNLOAD A REPORT (Profit & Loss)
# ==========================================================
def run_report(accounting_api):
    orgs = accounting_api.get_organisations()
    tenant_id = orgs.organisations[0].organisation_id

    print("Using tenant:", tenant_id)

    # Get 2024 Profit & Loss as an example
    report = accounting_api.get_report_profit_and_loss(
        xero_tenant_id=tenant_id,
        from_date="2024-01-01",
        to_date="2024-12-31"
    )

    # Save JSON output
    with open("pl_report.json", "w") as f:
        json.dump(report.to_dict(), f, indent=2)

    print("Saved: pl_report.json")


# ==========================================================
# MAIN
# ==========================================================
if __name__ == "__main__":
    authenticate()
    acc_api = build_xero_client()
    run_report(acc_api)
