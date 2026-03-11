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

# -----------------------------
# Xero Credentials (do not expose)
# -----------------------------
# CLIENT_ID = "YOUR_CLIENT_ID"
# CLIENT_SECRET = "YOUR_CLIENT_SECRET"
# REDIRECT_URI = "http://localhost:8080/callback"
SCOPES = "offline_access accounting.transactions accounting.settings"

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
    return token_data

def refresh_token(tokens):
    print("Refreshing access token...")
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    headers = {"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "refresh_token", "refresh_token": tokens["refresh_token"]}
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    new_tokens = response.json()

    if "error" in new_tokens:
        print("Failed to refresh token:", new_tokens.get("error_description", new_tokens.get("error")))
        raise Exception("Token refresh failed. Please re-authenticate.")

    if "expires_in" in new_tokens:
        new_tokens["expires_at"] = time.time() + new_tokens["expires_in"]
    else:
        print("Warning: expires_in not returned, using 29 minutes as fallback")
        new_tokens["expires_at"] = time.time() + 29*60

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
# Safe request with retries and token refresh
# -----------------------------
def safe_request(url, tenant_id, page=1, method="GET", data=None):
    for attempt in range(5):
        access_token = get_valid_token()
        headers = {"Authorization": f"Bearer {access_token}", "xero-tenant-id": tenant_id, "Accept": "application/json"}
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                response = requests.post(url, headers=headers, data=data)
        except Exception as e:
            print(f"Request error on page {page}: {e}")
            time.sleep(2)
            continue

        if response.status_code == 200 and response.text.strip():
            try:
                return response.json()
            except Exception as e:
                print(f"JSON decode failed on page {page}: {e}")
                print("Response text:", response.text)
                time.sleep(2)
                continue
        elif response.status_code == 401:
            print("Access token expired, refreshing...")
            refresh_token(json.load(open(TOKEN_FILE)))
            continue
        elif response.status_code == 429:
            wait = (attempt + 1) * 2
            print(f"Rate limit hit (429), sleeping {wait}s before retry...")
            time.sleep(wait)
            continue
        else:
            print(f"Error {response.status_code} on page {page}: {response.text}")
            time.sleep(2)
    print(f"Failed to fetch page {page} after 5 attempts")
    return None

# -----------------------------
# Tenant ID
# -----------------------------
def get_tenant_id(access_token):
    data = safe_request("https://api.xero.com/connections", tenant_id="dummy", method="GET")
    if not data:
        raise Exception("Failed to get tenant ID")
    tenant_id = data[0]["tenantId"]
    print("Connected to tenant:", data[0]["tenantName"])
    return tenant_id

# -----------------------------
# Export invoices (all fields)
# -----------------------------
def export_invoices_to_text(tenant_id, invoice_type, filename, type_label):
    page = 1
    all_rows = []
    headers_set = set()
    
    while True:
        url = f'https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type=="{invoice_type}"'
        data = safe_request(url, tenant_id, page)
        if not data or "Invoices" not in data or not data["Invoices"]:
            break
        
        for inv in data["Invoices"]:
            base_row = {}
            # top-level invoice fields
            for k, v in inv.items():
                if k != "LineItems":
                    base_row[k] = v
                    headers_set.add(k)
            # include all line items as separate rows
            line_items = inv.get("LineItems", [])
            if line_items:
                for li in line_items:
                    row = base_row.copy()
                    for k, v in li.items():
                        row[f"LineItem_{k}"] = v
                        headers_set.add(f"LineItem_{k}")
                    row["TypeLabel"] = type_label
                    headers_set.add("TypeLabel")
                    all_rows.append(row)
            else:
                row = base_row.copy()
                row["TypeLabel"] = type_label
                headers_set.add("TypeLabel")
                all_rows.append(row)
        
        print(f"Fetched {type_label} page {page}")
        page += 1
        time.sleep(0.5)

    headers = list(headers_set)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(headers) + "\n")
        for r in all_rows:
            f.write("|".join(str(r.get(h, "")) for h in headers) + "\n")
    
    print(f"{type_label} exported to {filename}")
    return all_rows  # for combined export

# -----------------------------
# Export paid invoices (all fields)
# -----------------------------
def export_paid_invoices(tenant_id, invoice_type, filename, type_label):
    page = 1
    all_rows = []
    headers_set = set()
    
    while True:
        url = f'https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type=="{invoice_type}" && Status=="PAID"'
        data = safe_request(url, tenant_id, page)
        if not data or "Invoices" not in data or not data["Invoices"]:
            break
        
        for inv in data["Invoices"]:
            base_row = {}
            for k, v in inv.items():
                if k != "LineItems":
                    base_row[k] = v
                    headers_set.add(k)
            line_items = inv.get("LineItems", [])
            if line_items:
                for li in line_items:
                    row = base_row.copy()
                    for k, v in li.items():
                        row[f"LineItem_{k}"] = v
                        headers_set.add(f"LineItem_{k}")
                    row["TypeLabel"] = type_label
                    headers_set.add("TypeLabel")
                    all_rows.append(row)
            else:
                row = base_row.copy()
                row["TypeLabel"] = type_label
                headers_set.add("TypeLabel")
                all_rows.append(row)
        
        print(f"Fetched {type_label} page {page}")
        page += 1
        time.sleep(0.5)

    headers = list(headers_set)
    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(headers) + "\n")
        for r in all_rows:
            f.write("|".join(str(r.get(h, "")) for h in headers) + "\n")
    
    print(f"{type_label} exported to {filename}")
    return all_rows

# -----------------------------
# Export combined paid invoices
# -----------------------------
def export_all_paid_invoices_combined(tenant_id, filename="JOP_all_paid_invoices.txt"):
    sales = export_paid_invoices(tenant_id, "ACCREC", "JOP_paid_sales.txt", "Sale")
    expenses = export_paid_invoices(tenant_id, "ACCPAY", "JOP_paid_expenses.txt", "Expense")
    all_rows = sales + expenses

    # collect headers dynamically
    headers_set = set()
    for r in all_rows:
        headers_set.update(r.keys())
    headers = list(headers_set)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("|".join(headers) + "\n")
        for r in all_rows:
            f.write("|".join(str(r.get(h, "")) for h in headers) + "\n")
    
    print(f"All paid sales and expenses exported to {filename}")

# -----------------------------
# Other exports (payments, accounts, contacts, bank transactions, tracking categories)
# -----------------------------
def export_payments(tenant_id):
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Payments?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data or "Payments" not in data or not data["Payments"]:
            break
        for p in data["Payments"]:
            contact = p.get("Invoice", {}).get("Contact", {}).get("Name", "")
            rows.append([p.get("Date"), contact, p.get("Amount"), p.get("Reference")])
        print(f"Fetched payments page {page}")
        page += 1
        time.sleep(0.5)
    with open("JOP_payments.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Amount","Reference"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join(str(x) if x else "" for x in r) + "\n")
    print("Payments exported to JOP_payments.txt")

def export_accounts(tenant_id):
    url = "https://api.xero.com/api.xro/2.0/Accounts"
    data = safe_request(url, tenant_id)
    if not data or "Accounts" not in data:
        return
    accounts = data["Accounts"]
    with open("JOP_accounts.txt", "w", encoding="utf-8") as f:
        header = ["Code","Name","Type","Class","Status","Description"]
        f.write("|".join(header) + "\n")
        for a in accounts:
            row = [a.get("Code"), a.get("Name"), a.get("Type"), a.get("Class"), a.get("Status"), a.get("Description")]
            f.write("|".join(str(x) if x else "" for x in row) + "\n")
    print("Accounts exported to JOP_accounts.txt")

def export_contacts(tenant_id):
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Contacts?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data or "Contacts" not in data or not data["Contacts"]:
            break
        for c in data["Contacts"]:
            rows.append([c.get("Name"), c.get("EmailAddress"), c.get("ContactStatus"), c.get("DefaultCurrency")])
        print(f"Fetched contacts page {page}")
        page += 1
        time.sleep(0.5)
    with open("JOP_contacts.txt", "w", encoding="utf-8") as f:
        header = ["Name","Email","Status","Currency"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join(str(x) if x else "" for x in r) + "\n")
    print("Contacts exported to JOP_contacts.txt")

def export_bank_transactions(tenant_id):
    page = 1
    rows = []
    while True:
        url = f"https://api.xero.com/api.xro/2.0/BankTransactions?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data or "BankTransactions" not in data or not data["BankTransactions"]:
            break
        for t in data["BankTransactions"]:
            contact = t.get("Contact", {}).get("Name", "")
            rows.append([t.get("Date"), contact, t.get("Reference"), t.get("Total"), t.get("Type"), t.get("Status")])
        print(f"Fetched bank transactions page {page}")
        page += 1
        time.sleep(0.5)
    with open("JOP_bank_transactions.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Reference","Total","Type","Status"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join(str(x) if x else "" for x in r) + "\n")
    print("Bank transactions exported to JOP_bank_transactions.txt")

def export_tracking_categories(tenant_id):
    url = "https://api.xero.com/api.xro/2.0/TrackingCategories"
    data = safe_request(url, tenant_id)
    if not data or "TrackingCategories" not in data:
        return
    categories = data["TrackingCategories"]
    with open("JOP_tracking_categories.txt", "w", encoding="utf-8") as f:
        header = ["Category","Option"]
        f.write("|".join(header) + "\n")
        for cat in categories:
            for option in cat.get("Options", []):
                row = [cat.get("Name"), option.get("Name")]
                f.write("|".join(str(x) if x else "" for x in row) + "\n")
    print("Tracking categories exported to JOP_tracking_categories.txt")

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

    # -----------------------------
    # Original functionality
    # -----------------------------
    export_invoices_to_text(tenant_id, "ACCREC", "JOP_sales.txt", "Sales")
    export_invoices_to_text(tenant_id, "ACCPAY", "JOP_expenses.txt", "Expenses")
    export_payments(tenant_id)
    export_accounts(tenant_id)
    export_contacts(tenant_id)
    export_bank_transactions(tenant_id)
    export_tracking_categories(tenant_id)

    # -----------------------------
    # New: all paid invoices combined
    # -----------------------------
    export_all_paid_invoices_combined(tenant_id)

if __name__ == "__main__":
    main()