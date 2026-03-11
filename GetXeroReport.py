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
# import json
# import threading
# import webbrowser
# from http.server import BaseHTTPRequestHandler, HTTPServer

# from xero_python.api_client.configuration import Configuration, OAuth2Token
# from xero_python.api_client import ApiClient
# from xero_python.accounting import AccountingApi


# # ================================
# # CONFIGURE THESE VALUES
# # ================================
# CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
# CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
# REDIRECT_URI = "http://localhost:8000/callback"

# SCOPES = [
#     "openid",
#     "profile",
#     "email",
#     "offline_access",
#     "accounting.reports.read"
# ]

# AUTH_URL = "https://login.xero.com/identity/connect/authorize"
# TOKEN_URL = "https://identity.xero.com/connect/token"


# # ==========================================================
# # Global token storage
# # ==========================================================
# token_data = {}


# # ==========================================================
# # Minimal OAuth2 Callback Server
# # ==========================================================
# class OAuthHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         global token_data

#         if "/callback" not in self.path:
#             self.send_response(404)
#             self.end_headers()
#             return

#         # Grab ?code=XYZ
#         query = self.path.split("?")[1]
#         params = dict(kv.split("=") for kv in query.split("&"))
#         code = params.get("code")

#         # Exchange code for token
#         import requests

#         data = {
#             "grant_type": "authorization_code",
#             "code": code,
#             "redirect_uri": REDIRECT_URI,
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#         }

#         response = requests.post(TOKEN_URL, data=data)
#         token_data = response.json()

#         self.send_response(200)
#         self.end_headers()
#         self.wfile.write(b"Xero authentication successful. You can close this window.")

#         # Stop server
#         threading.Thread(target=self.server.shutdown).start()


# # ==========================================================
# # START AUTH FLOW
# # ==========================================================
# def authenticate():
#     # Start local server
#     server = HTTPServer(("localhost", 8000), OAuthHandler)
#     threading.Thread(target=server.serve_forever).start()

#     # Build login URL
#     scope_str = " ".join(SCOPES)

#     auth_url = (
#         f"{AUTH_URL}"
#         f"?response_type=code"
#         f"&client_id={CLIENT_ID}"
#         f"&redirect_uri={REDIRECT_URI}"
#         f"&scope={scope_str}"
#     )

#     print("Opening browser for login...")
#     webbrowser.open(auth_url)

#     print("Waiting for OAuth callback...")
#     server.serve_forever()


# # ==========================================================
# # BUILD XERO API CLIENT
# # ==========================================================
# def build_xero_client():
#     global token_data

#     # Build OAuth2 token object for this SDK
#     oauth2_token = OAuth2Token(
#         access_token=token_data["access_token"],
#         refresh_token=token_data.get("refresh_token"),
#         expires_at=int(token_data["expires_in"]),
#         token_type=token_data["token_type"]
#     )

#     config = Configuration(oauth2_token=oauth2_token)

#     api_client = ApiClient(configuration=config)

#     # Register token getter/saver
#     @api_client.oauth2_token_getter
#     def get_token():
#         return token_data

#     @api_client.oauth2_token_saver
#     def save_token(new_token):
#         global token_data
#         token_data = new_token

#     return AccountingApi(api_client)


# # ==========================================================
# # EXAMPLE: DOWNLOAD A REPORT (Profit & Loss)
# # ==========================================================
# def run_report(accounting_api):
#     orgs = accounting_api.get_organisations()
#     tenant_id = orgs.organisations[0].organisation_id

#     print("Using tenant:", tenant_id)

#     # Get 2024 Profit & Loss as an example
#     report = accounting_api.get_report_profit_and_loss(
#         xero_tenant_id=tenant_id,
#         from_date="2024-01-01",
#         to_date="2024-12-31"
#     )

#     # Save JSON output
#     with open("pl_report.json", "w") as f:
#         json.dump(report.to_dict(), f, indent=2)

#     print("Saved: pl_report.json")


# # ==========================================================
# # MAIN
# # ==========================================================
# if __name__ == "__main__":
#     authenticate()
#     acc_api = build_xero_client()
#     run_report(acc_api)
#########################

CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
REDIRECT_URI = "http://localhost:8000/callback"

# import requests
# import webbrowser
# from urllib.parse import urlparse, parse_qs
# import http.server
# import socketserver
# import base64
# import json

# #CLIENT_ID = "YOUR_CLIENT_ID"
# #CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# #REDIRECT_URI = "http://localhost:8080/callback"

# SCOPES = "offline_access accounting.transactions accounting.settings"

# AUTH_URL = "https://login.xero.com/identity/connect/authorize"
# TOKEN_URL = "https://identity.xero.com/connect/token"

# auth_code = None


# class Handler(http.server.SimpleHTTPRequestHandler):
#     def do_GET(self):
#         global auth_code

#         parsed = urlparse(self.path)
#         params = parse_qs(parsed.query)

#         if "code" in params:
#             auth_code = params["code"][0]

#             self.send_response(200)
#             self.send_header("Content-type", "text/html")
#             self.end_headers()

#             self.wfile.write(b"Authorization successful. You can close this window.")


# def get_authorization_code():
#     auth_link = (
#         f"{AUTH_URL}?"
#         f"response_type=code"
#         f"&client_id={CLIENT_ID}"
#         f"&redirect_uri={REDIRECT_URI}"
#         f"&scope={SCOPES}"
#     )

#     print("Opening browser for Xero login...")
#     webbrowser.open(auth_link)

#     with socketserver.TCPServer(("localhost", 8000), Handler) as httpd:
#         while not auth_code:
#             httpd.handle_request()

#     return auth_code


# def exchange_code_for_token(code):

#     credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
#     encoded = base64.b64encode(credentials.encode()).decode()

#     headers = {
#         "Authorization": f"Basic {encoded}",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }

#     data = {
#         "grant_type": "authorization_code",
#         "code": code,
#         "redirect_uri": REDIRECT_URI
#     }

#     response = requests.post(TOKEN_URL, headers=headers, data=data)

#     token_data = response.json()

#     with open("xero_tokens.json", "w") as f:
#         json.dump(token_data, f, indent=4)

#     print("Tokens saved to xero_tokens.json")


# def main():
#     code = get_authorization_code()
#     exchange_code_for_token(code)


# if __name__ == "__main__":
#     main()

####################
import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
import base64
import json
import time

# CLIENT_ID = "YOUR_CLIENT_ID"
# CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# REDIRECT_URI = "http://localhost:8080/callback"

SCOPES = "offline_access accounting.transactions accounting.settings"

AUTH_URL = "https://login.xero.com/identity/connect/authorize"
TOKEN_URL = "https://identity.xero.com/connect/token"

TOKEN_FILE = "xero_tokens.json"

auth_code = None


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code

        parsed = urlparse(self.path)

        if parsed.path == "/callback":
            params = parse_qs(parsed.query)

            if "code" in params:
                auth_code = params["code"][0]

                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                self.wfile.write(
                    b"<h2>Authorization successful. You can close this window.</h2>"
                )


def get_authorization_code():
    auth_link = (
        f"{AUTH_URL}?"
        f"response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES}"
    )

    print("Opening browser for Xero login...")
    webbrowser.open(auth_link)

    with socketserver.TCPServer(("localhost", 8000), Handler) as httpd:
        while not auth_code:
            httpd.handle_request()

    return auth_code


def exchange_code_for_token(code):

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)
    token_data = response.json()

    token_data["expires_at"] = time.time() + token_data["expires_in"]

    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=4)

    print("Tokens saved to xero_tokens.json")


def refresh_token(tokens):

    print("Refreshing access token...")

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"]
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    new_tokens = response.json()
    new_tokens["expires_at"] = time.time() + new_tokens["expires_in"]

    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=4)

    return new_tokens


def get_valid_token():

    with open(TOKEN_FILE) as f:
        tokens = json.load(f)

    if time.time() > tokens["expires_at"]:
        tokens = refresh_token(tokens)

    return tokens["access_token"]


def get_tenant_id(access_token):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }

    response = requests.get(
        "https://api.xero.com/connections",
        headers=headers
    )

    connections = response.json()

    tenant_id = connections[0]["tenantId"]

    print("Connected to tenant:", connections[0]["tenantName"])

    return tenant_id


def get_all_bank_transactions(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    all_transactions = []
    page = 1

    while True:

        url = f"https://api.xero.com/api.xro/2.0/BankTransactions?page={page}"

        response = requests.get(url, headers=headers)

        data = response.json()

        transactions = data.get("BankTransactions", [])

        if not transactions:
            break

        all_transactions.extend(transactions)

        print(f"Fetched page {page} ({len(transactions)} transactions)")

        page += 1

    print(f"\nTotal transactions retrieved: {len(all_transactions)}")

    return all_transactions

def get_all_invoices(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    all_invoices = []
    page = 1

    while True:

        url = f"https://api.xero.com/api.xro/2.0/Invoices?page={page}"

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Error:", response.text)
            break

        data = response.json()

        invoices = data.get("Invoices", [])

        if not invoices:
            break

        print(f"Fetched page {page} ({len(invoices)} invoices)")

        all_invoices.extend(invoices)

        page += 1

    print("Total invoices retrieved:", len(all_invoices))

    return all_invoices

def export_invoices_to_text(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f"https://api.xero.com/api.xro/2.0/Invoices?page={page}"

        response = requests.get(url, headers=headers)
        data = response.json()

        invoices = data.get("Invoices", [])

        if not invoices:
            break

        for inv in invoices:

            contact = ""
            if inv.get("Contact"):
                contact = inv["Contact"].get("Name", "")

            for line in inv.get("LineItems", []):

                row = [
                    inv.get("InvoiceID"),
                    inv.get("Type"),
                    inv.get("Date"),
                    inv.get("DueDate"),
                    inv.get("Status"),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    inv.get("Total")
                ]

                rows.append(row)

        print(f"Fetched page {page}")
        page += 1

    with open("xero_invoices.txt", "w", encoding="utf-8") as f:

        header = [
            "InvoiceID",
            "Type",
            "Date",
            "DueDate",
            "Status",
            "Contact",
            "Description",
            "AccountCode",
            "Quantity",
            "UnitAmount",
            "LineAmount",
            "Total"
        ]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x is not None else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Invoices exported to xero_invoices.txt")


def export_sales(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f'https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type=="ACCREC"'

        response = requests.get(url, headers=headers)
        data = response.json()

        invoices = data.get("Invoices", [])

        if not invoices:
            break

        for inv in invoices:

            contact = inv.get("Contact", {}).get("Name", "")

            for line in inv.get("LineItems", []):

                rows.append([
                    inv.get("InvoiceNumber"),
                    inv.get("Date"),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    inv.get("Total"),
                    inv.get("Status")
                ])

        print(f"Fetched sales page {page}")
        page += 1

    with open("sales.txt", "w", encoding="utf-8") as f:

        header = [
            "InvoiceNumber","Date","Contact","Description",
            "AccountCode","Quantity","UnitAmount",
            "LineAmount","InvoiceTotal","Status"
        ]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Sales exported to sales.txt")

def export_expenses(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f'https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type=="ACCPAY"'

        response = requests.get(url, headers=headers)
        data = response.json()

        invoices = data.get("Invoices", [])

        if not invoices:
            break

        for inv in invoices:

            contact = inv.get("Contact", {}).get("Name", "")

            for line in inv.get("LineItems", []):

                rows.append([
                    inv.get("InvoiceNumber"),
                    inv.get("Date"),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    inv.get("Total"),
                    inv.get("Status")
                ])

        print(f"Fetched expense page {page}")
        page += 1

    with open("expenses.txt", "w", encoding="utf-8") as f:

        header = [
            "BillNumber","Date","Vendor","Description",
            "AccountCode","Quantity","UnitAmount",
            "LineAmount","BillTotal","Status"
        ]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Expenses exported to expenses.txt")

def export_payments(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f"https://api.xero.com/api.xro/2.0/Payments?page={page}"

        response = requests.get(url, headers=headers)
        data = response.json()

        payments = data.get("Payments", [])

        if not payments:
            break

        for p in payments:

            contact = p.get("Invoice", {}).get("Contact", {}).get("Name", "")

            rows.append([
                p.get("Date"),
                contact,
                p.get("Amount"),
                p.get("Reference")
            ])

        print(f"Fetched payments page {page}")
        page += 1

    with open("payments.txt", "w", encoding="utf-8") as f:

        header = ["Date","Contact","Amount","Reference"]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Payments exported to payments.txt")

def export_accounts(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    url = "https://api.xero.com/api.xro/2.0/Accounts"

    response = requests.get(url, headers=headers)
    data = response.json()

    accounts = data.get("Accounts", [])

    with open("accounts.txt", "w", encoding="utf-8") as f:

        header = [
            "Code","Name","Type","Class",
            "Status","Description"
        ]

        f.write("|".join(header) + "\n")

        for a in accounts:

            row = [
                a.get("Code"),
                a.get("Name"),
                a.get("Type"),
                a.get("Class"),
                a.get("Status"),
                a.get("Description")
            ]

            row = [str(x) if x else "" for x in row]

            f.write("|".join(row) + "\n")

    print("Accounts exported to accounts.txt")

def export_contacts(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f"https://api.xero.com/api.xro/2.0/Contacts?page={page}"

        response = requests.get(url, headers=headers)
        data = response.json()

        contacts = data.get("Contacts", [])

        if not contacts:
            break

        for c in contacts:

            rows.append([
                c.get("Name"),
                c.get("EmailAddress"),
                c.get("ContactStatus"),
                c.get("DefaultCurrency")
            ])

        print(f"Fetched contacts page {page}")
        page += 1

    with open("contacts.txt", "w", encoding="utf-8") as f:

        header = ["Name","Email","Status","Currency"]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Contacts exported to contacts.txt")

def export_bank_transactions(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    page = 1
    rows = []

    while True:

        url = f"https://api.xero.com/api.xro/2.0/BankTransactions?page={page}"

        response = requests.get(url, headers=headers)
        data = response.json()

        transactions = data.get("BankTransactions", [])

        if not transactions:
            break

        for t in transactions:

            contact = t.get("Contact", {}).get("Name", "")

            rows.append([
                t.get("Date"),
                contact,
                t.get("Reference"),
                t.get("Total"),
                t.get("Type"),
                t.get("Status")
            ])

        print(f"Fetched bank transactions page {page}")
        page += 1

    with open("bank_transactions.txt", "w", encoding="utf-8") as f:

        header = [
            "Date","Contact","Reference",
            "Total","Type","Status"
        ]

        f.write("|".join(header) + "\n")

        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")

    print("Bank transactions exported to bank_transactions.txt")

def export_tracking_categories(access_token, tenant_id):

    headers = {
        "Authorization": f"Bearer {access_token}",
        "xero-tenant-id": tenant_id,
        "Accept": "application/json"
    }

    url = "https://api.xero.com/api.xro/2.0/TrackingCategories"

    response = requests.get(url, headers=headers)
    data = response.json()

    categories = data.get("TrackingCategories", [])

    with open("tracking_categories.txt", "w", encoding="utf-8") as f:

        header = ["Category","Option"]

        f.write("|".join(header) + "\n")

        for cat in categories:

            for option in cat.get("Options", []):

                row = [
                    cat.get("Name"),
                    option.get("Name")
                ]

                row = [str(x) if x else "" for x in row]

                f.write("|".join(row) + "\n")

    print("Tracking categories exported to tracking_categories.txt")



def main():

    try:
        access_token = get_valid_token()

    except:
        code = get_authorization_code()
        exchange_code_for_token(code)
        access_token = get_valid_token()

    tenant_id = get_tenant_id(access_token)

    transactions = get_all_bank_transactions(access_token, tenant_id)

    with open("transactions.json", "w") as f:
        json.dump(transactions, f, indent=4)

    print("Transactions saved to transactions.json")

    invoices = get_all_invoices(access_token, tenant_id)

    with open("all_invoices.json", "w") as f:
        json.dump(invoices, f, indent=4)

    print("Saved all invoices and bills to all_invoices.json")

    export_invoices_to_text(access_token, tenant_id)

    export_sales(access_token, tenant_id)
    export_expenses(access_token, tenant_id)
    export_payments(access_token, tenant_id)

    export_accounts(access_token, tenant_id)
    export_contacts(access_token, tenant_id)
    export_bank_transactions(access_token, tenant_id)
    export_tracking_categories(access_token, tenant_id)


if __name__ == "__main__":
    main()