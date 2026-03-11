CLIENT_ID = "86F233D613AF4B7EB6C25183035350F3"
CLIENT_SECRET = "vcIMN3DMASE5omjr3H1SG0fqyypDIHeXHSEKxCAK9x5XI7dd"
REDIRECT_URI = "http://localhost:8000/callback"

import requests
import webbrowser
from urllib.parse import urlparse, parse_qs
import http.server
import socketserver
import base64
import json
import time
import pandas as pd

# -----------------------------
# Xero Credentials (do not expose)
# -----------------------------
# CLIENT_ID = "YOUR_CLIENT_ID"
# CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# REDIRECT_URI = "http://localhost:8080/callback"
# SCOPES = "offline_access accounting.transactions accounting.settings"

AUTH_URL = "https://login.xero.com/identity/connect/authorize"
TOKEN_URL = "https://identity.xero.com/connect/token"
TOKEN_FILE = "xero_tokens.json"

auth_code = None

# -----------------------------
# HTTP Handler for OAuth redirect
# -----------------------------
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

# -----------------------------
# OAuth functions
# -----------------------------
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
    headers = {"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI}
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
    headers = {"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    new_tokens = response.json()
    new_tokens["expires_at"] = time.time() + new_tokens["expires_in"]
    with open(TOKEN_FILE, "w") as f:
        json.dump(new_tokens, f, indent=4)
    return new_tokens

def get_valid_token():
    with open(TOKEN_FILE) as f:
        tokens = json.load(f)
    if time.time() > tokens.get("expires_at", 0):
        tokens = refresh_token(tokens)
    return tokens["access_token"]

# -----------------------------
# Helper to safely get JSON
# -----------------------------
def safe_get_json(url, headers, page):
    for attempt in range(3):
        response = requests.get(url, headers=headers)
        if response.status_code == 401:
            print("Access token invalid/expired")
            return None, 401
        if response.status_code != 200:
            print(f"Error fetching page {page}: {response.status_code} {response.text}")
            return None, response.status_code
        if response.text.strip():
            try:
                return response.json(), 200
            except Exception as e:
                print(f"JSON decode failed page {page}: {e}")
                print("Response:", response.text)
        print("Empty or invalid response, retrying...")
        time.sleep(2)
    print(f"Failed to get valid JSON after 3 attempts for page {page}")
    return None, None

# -----------------------------
# Get Tenant ID
# -----------------------------
def get_tenant_id(access_token):
    headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    data, status = safe_get_json("https://api.xero.com/connections", headers, page=1)
    if not data:
        raise Exception("Failed to get tenant ID")
    tenant_id = data[0]["tenantId"]
    print("Connected to tenant:", data[0]["tenantName"])
    return tenant_id

# -----------------------------
# Generic Export function
# -----------------------------
def export_invoices_to_text(access_token, tenant_id, invoice_type, filename, type_label):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type==\"{invoice_type}\""
        data, status = safe_get_json(url, headers, page)
        if not data or status != 200:
            break
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
        print(f"Fetched {type_label} page {page}")
        page += 1
    with open(filename, "w", encoding="utf-8") as f:
        header = ["InvoiceNumber","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","InvoiceTotal","Status"]
        f.write("|".join(header) + "\n")
        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")
    print(f"{type_label} exported to {filename}")

# -----------------------------
# Export Payments
# -----------------------------
def export_payments(access_token, tenant_id):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Payments?page={page}"
        data, status = safe_get_json(url, headers, page)
        if not data or status != 200:
            break
        payments = data.get("Payments", [])
        if not payments:
            break
        for p in payments:
            contact = p.get("Invoice", {}).get("Contact", {}).get("Name", "")
            rows.append([p.get("Date"), contact, p.get("Amount"), p.get("Reference")])
        print(f"Fetched payments page {page}")
        page += 1
    with open("payments.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Amount","Reference"]
        f.write("|".join(header) + "\n")
        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")
    print("Payments exported to payments.txt")

# -----------------------------
# Export Accounts
# -----------------------------
def export_accounts(access_token, tenant_id):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    data, status = safe_get_json("https://api.xero.com/api.xro/2.0/Accounts", headers, 1)
    if not data:
        return
    accounts = data.get("Accounts", [])
    with open("accounts.txt", "w", encoding="utf-8") as f:
        header = ["Code","Name","Type","Class","Status","Description"]
        f.write("|".join(header) + "\n")
        for a in accounts:
            row = [a.get("Code"), a.get("Name"), a.get("Type"), a.get("Class"), a.get("Status"), a.get("Description")]
            row = [str(x) if x else "" for x in row]
            f.write("|".join(row) + "\n")
    print("Accounts exported to accounts.txt")

# -----------------------------
# Export Contacts
# -----------------------------
def export_contacts(access_token, tenant_id):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Contacts?page={page}"
        data, status = safe_get_json(url, headers, page)
        if not data or status != 200:
            break
        contacts = data.get("Contacts", [])
        if not contacts:
            break
        for c in contacts:
            rows.append([c.get("Name"), c.get("EmailAddress"), c.get("ContactStatus"), c.get("DefaultCurrency")])
        print(f"Fetched contacts page {page}")
        page += 1
    with open("contacts.txt", "w", encoding="utf-8") as f:
        header = ["Name","Email","Status","Currency"]
        f.write("|".join(header) + "\n")
        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")
    print("Contacts exported to contacts.txt")

# -----------------------------
# Export Bank Transactions
# -----------------------------
def export_bank_transactions(access_token, tenant_id):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/BankTransactions?page={page}"
        data, status = safe_get_json(url, headers, page)
        if not data or status != 200:
            break
        transactions = data.get("BankTransactions", [])
        if not transactions:
            break
        for t in transactions:
            contact = t.get("Contact", {}).get("Name", "")
            rows.append([t.get("Date"), contact, t.get("Reference"), t.get("Total"), t.get("Type"), t.get("Status")])
        print(f"Fetched bank transactions page {page}")
        page += 1
    with open("bank_transactions.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Reference","Total","Type","Status"]
        f.write("|".join(header) + "\n")
        for r in rows:
            r = [str(x) if x else "" for x in r]
            f.write("|".join(r) + "\n")
    print("Bank transactions exported to bank_transactions.txt")

# -----------------------------
# Export Tracking Categories
# -----------------------------
def export_tracking_categories(access_token, tenant_id):
    headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
    data, status = safe_get_json("https://api.xero.com/api.xro/2.0/TrackingCategories", headers, 1)
    if not data:
        return
    categories = data.get("TrackingCategories", [])
    with open("tracking_categories.txt", "w", encoding="utf-8") as f:
        header = ["Category","Option"]
        f.write("|".join(header) + "\n")
        for cat in categories:
            for option in cat.get("Options", []):
                row = [cat.get("Name"), option.get("Name")]
                row = [str(x) if x else "" for x in row]
                f.write("|".join(row) + "\n")
    print("Tracking categories exported to tracking_categories.txt")

# -----------------------------
# Main
# -----------------------------
def main():
    try:
        access_token = get_valid_token()
    except:
        code = get_authorization_code()
        exchange_code_for_token(code)
        access_token = get_valid_token()

    tenant_id = get_tenant_id(access_token)

    export_invoices_to_text(access_token, tenant_id, "ACCREC", "sales.txt", "Sales")
    export_invoices_to_text(access_token, tenant_id, "ACCPAY", "expenses.txt", "Expenses")
    export_payments(access_token, tenant_id)
    export_accounts(access_token, tenant_id)
    export_contacts(access_token, tenant_id)
    export_bank_transactions(access_token, tenant_id)
    export_tracking_categories(access_token, tenant_id)

# -----------------------------
if __name__ == "__main__":
    main()