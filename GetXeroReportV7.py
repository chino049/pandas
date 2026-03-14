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
from datetime import datetime

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
# Safe request with retries
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
# Helper: format date
# -----------------------------
def format_xero_date(date_str):
    if not date_str:
        return ""
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d").strftime("%Y-%m-%d")
    except:
        return date_str

# -----------------------------
# Export invoices
# -----------------------------
def export_invoices_to_text(tenant_id, invoice_type, filename, type_label):
    page = 1
    rows = []
    total_count = 0
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type==\"{invoice_type}\""
        data = safe_request(url, tenant_id, page)
        if not data:
            break
        invoices = data.get("Invoices", [])
        if not invoices:
            break
        for inv in invoices:
            contact = inv.get("Contact", {}).get("Name", "")
            for line in inv.get("LineItems", []):
                rows.append([
                    inv.get("InvoiceNumber"),
                    format_xero_date(inv.get("Date")),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    inv.get("Total"),
                    inv.get("Status")
                ])
        total_count += len(invoices)
        print(f"Fetched {type_label} page {page} ({len(invoices)} invoices)")
        page += 1
        time.sleep(0.5)

    with open(filename, "w", encoding="utf-8") as f:
        header = ["InvoiceNumber","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","InvoiceTotal","Status"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"{type_label} exported to {filename} ({total_count} total invoices)")

# -----------------------------
# Export payments
# -----------------------------
def export_payments(tenant_id):
    page = 1
    rows = []
    total_count = 0
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Payments?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data:
            break
        payments = data.get("Payments", [])
        if not payments:
            break
        for p in payments:
            contact = p.get("Invoice", {}).get("Contact", {}).get("Name", "")
            rows.append([format_xero_date(p.get("Date")), contact, p.get("Amount"), p.get("Reference")])
        total_count += len(payments)
        print(f"Fetched payments page {page} ({len(payments)} payments)")
        page += 1
        time.sleep(0.5)

    with open("JOP_payments.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Amount","Reference"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"Payments exported to JOP_payments.txt ({total_count} total)")

# -----------------------------
# Export accounts
# -----------------------------
def export_accounts(tenant_id):
    url = "https://api.xero.com/api.xro/2.0/Accounts"
    data = safe_request(url, tenant_id)
    if not data:
        return
    accounts = data.get("Accounts", [])
    with open("JOP_accounts.txt", "w", encoding="utf-8") as f:
        header = ["Code","Name","Type","Class","Status","Description"]
        f.write("|".join(header) + "\n")
        for a in accounts:
            row = [a.get("Code"), a.get("Name"), a.get("Type"), a.get("Class"), a.get("Status"), a.get("Description")]
            f.write("|".join([str(x) if x else "" for x in row]) + "\n")
    print(f"Accounts exported to JOP_accounts.txt ({len(accounts)} total)")

# -----------------------------
# Export contacts
# -----------------------------
def export_contacts(tenant_id):
    page = 1
    rows = []
    total_count = 0
    while True:
        url = f"https://api.xero.com/api.xro/2.0/Contacts?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data:
            break
        contacts = data.get("Contacts", [])
        if not contacts:
            break
        for c in contacts:
            rows.append([c.get("Name"), c.get("EmailAddress"), c.get("ContactStatus"), c.get("DefaultCurrency")])
        total_count += len(contacts)
        print(f"Fetched contacts page {page} ({len(contacts)} contacts)")
        page += 1
        time.sleep(0.5)

    with open("JOP_contacts.txt", "w", encoding="utf-8") as f:
        header = ["Name","Email","Status","Currency"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"Contacts exported to JOP_contacts.txt ({total_count} total)")

# -----------------------------
# Export bank transactions
# -----------------------------
def export_bank_transactions(tenant_id):
    page = 1
    rows = []
    total_count = 0
    while True:
        url = f"https://api.xero.com/api.xro/2.0/BankTransactions?page={page}"
        data = safe_request(url, tenant_id, page)
        if not data:
            break
        transactions = data.get("BankTransactions", [])
        if not transactions:
            break
        for t in transactions:
            contact = t.get("Contact", {}).get("Name", "")
            rows.append([format_xero_date(t.get("Date")), contact, t.get("Reference"), t.get("Total"), t.get("Type"), t.get("Status")])
        total_count += len(transactions)
        print(f"Fetched bank transactions page {page} ({len(transactions)} transactions)")
        page += 1
        time.sleep(0.5)

    with open("JOP_bank_transactions.txt", "w", encoding="utf-8") as f:
        header = ["Date","Contact","Reference","Total","Type","Status"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"Bank transactions exported to JOP_bank_transactions.txt ({total_count} total)")

# -----------------------------
# Export tracking categories
# -----------------------------
def export_tracking_categories(tenant_id):
    url = "https://api.xero.com/api.xro/2.0/TrackingCategories"
    data = safe_request(url, tenant_id)
    if not data:
        return
    categories = data.get("TrackingCategories", [])
    rows = []
    for cat in categories:
        for option in cat.get("Options", []):
            rows.append([cat.get("Name"), option.get("Name")])

    with open("JOP_tracking_categories.txt", "w", encoding="utf-8") as f:
        header = ["Category","Option"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"Tracking categories exported to JOP_tracking_categories.txt ({len(rows)} total)")

# -----------------------------
# Paid invoices
# -----------------------------
def export_paid_invoices(tenant_id, invoice_type, filename, type_label):
    page = 1
    rows = []
    total_count = 0
    while True:
        url = f'https://api.xero.com/api.xro/2.0/Invoices?page={page}&where=Type=="{invoice_type}" && Status=="PAID"'
        data = safe_request(url, tenant_id, page)
        if not data:
            break
        invoices = data.get("Invoices", [])
        if not invoices:
            break
        for inv in invoices:
            contact = inv.get("Contact", {}).get("Name", "")
            for line in inv.get("LineItems", []):
                rows.append([
                    inv.get("InvoiceNumber"),
                    format_xero_date(inv.get("Date")),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    inv.get("Total"),
                    inv.get("Status"),
                    type_label
                ])
        total_count += len(invoices)
        print(f"Fetched {type_label} page {page} ({len(invoices)} invoices)")
        page += 1
        time.sleep(0.5)

    with open(filename, "w", encoding="utf-8") as f:
        header = ["InvoiceNumber","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    print(f"{type_label} exported to {filename} ({total_count} total invoices)")
    return rows

# -----------------------------
# Paid expense claims (with pagination)
# -----------------------------
# def export_paid_expense_claims(tenant_id, filename="JOP_paid_expense_claims.txt"):
#     page = 1
#     rows = []
#     total_count = 0

#     while True:
#         url = f'https://api.xero.com/api.xro/2.0/ExpenseClaims?page={page}&where=Status=="PAID"'
#         data = safe_request(url, tenant_id, page)
#         if not data:
#             break
#         claims = data.get("ExpenseClaims", [])
#         if not claims:
#             break
#         for claim in claims:
#             contact = claim.get("Contact", {}).get("Name", "")
#             for line in claim.get("LineItems", []):
#                 rows.append([
#                     claim.get("ExpenseClaimID"),
#                     format_xero_date(claim.get("Date")),
#                     contact,
#                     line.get("Description"),
#                     line.get("AccountCode"),
#                     line.get("Quantity"),
#                     line.get("UnitAmount"),
#                     line.get("LineAmount"),
#                     claim.get("Total"),
#                     claim.get("Status"),
#                     "ExpenseClaim"
#                 ])
#         total_count += len(claims)
#         print(f"Fetched ExpenseClaims page {page} ({len(claims)} claims)")
#         page += 1
#         time.sleep(0.5)

#     with open(filename, "w", encoding="utf-8") as f:
#         header = ["ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
#         f.write("|".join(header) + "\n")
#         for r in rows:
#             f.write("|".join([str(x) if x else "" for x in r]) + "\n")
    
#     print(f"All paid expense claims exported to {filename} ({total_count} total claims)")
#     return rows

# def export_paid_expense_claims(tenant_id, filename="JOP_paid_expense_claims.txt"):
#     rows = []
#     total_count = 0
#     page = 1
#     page_size = 100  # Xero default max per page is 100

#     while True:
#         url = f"https://api.xero.com/api.xro/2.0/ExpenseClaims?page={page}&pageSize={page_size}&where=Status==\"PAID\""
#         data = safe_request(url, tenant_id, page)
#         if not data:
#             break

#         claims = data.get("ExpenseClaims", [])
#         if not claims:
#             break  # No more claims, stop pagination

#         for claim in claims:
#             contact = claim.get("Contact", {}).get("Name", "")
#             for line in claim.get("LineItems", []):
#                 rows.append([
#                     claim.get("ExpenseClaimID"),
#                     format_xero_date(claim.get("Date")),
#                     contact,
#                     line.get("Description"),
#                     line.get("AccountCode"),
#                     line.get("Quantity"),
#                     line.get("UnitAmount"),
#                     line.get("LineAmount"),
#                     claim.get("Total"),
#                     claim.get("Status"),
#                     "ExpenseClaim"
#                 ])

#         total_count += len(claims)
#         print(f"Fetched ExpenseClaims page {page} ({len(claims)} claims, cumulative {total_count})")
#         page += 1
#         time.sleep(0.5)  # be polite with API rate limits

#     with open(filename, "w", encoding="utf-8") as f:
#         header = ["ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
#         f.write("|".join(header) + "\n")
#         for r in rows:
#             f.write("|".join([str(x) if x else "" for x in r]) + "\n")

#     print(f"All paid expense claims exported to {filename} ({total_count} total claims)")
#     return rows

# def export_paid_expense_claims(tenant_id, filename="JOP_paid_expense_claims.txt"):
#     rows = []
#     total_count = 0
#     page = 1
#     page_size = 100  # max allowed by Xero API

#     while True:
#         url = f"https://api.xero.com/api.xro/2.0/ExpenseClaims?page={page}&pageSize={page_size}&where=Status==\"PAID\""
#         data = safe_request(url, tenant_id, page)
#         if not data:
#             break

#         claims = data.get("ExpenseClaims", [])
#         if not claims:
#             break

#         # Add each claim's line items
#         for claim in claims:
#             contact = claim.get("Contact", {}).get("Name", "")
#             for line in claim.get("LineItems", []):
#                 rows.append([
#                     claim.get("ExpenseClaimID"),
#                     format_xero_date(claim.get("Date")),
#                     contact,
#                     line.get("Description"),
#                     line.get("AccountCode"),
#                     line.get("Quantity"),
#                     line.get("UnitAmount"),
#                     line.get("LineAmount"),
#                     claim.get("Total"),
#                     claim.get("Status"),
#                     "ExpenseClaim"
#                 ])

#         total_count += len(claims)
#         print(f"Fetched ExpenseClaims page {page} ({len(claims)} claims, cumulative {total_count})")

#         # Stop if last page returned less than page_size
#         if len(claims) < page_size:
#             break

#         page += 1
#         time.sleep(0.5)

#     with open(filename, "w", encoding="utf-8") as f:
#         header = ["ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
#         f.write("|".join(header) + "\n")
#         for r in rows:
#             f.write("|".join([str(x) if x else "" for x in r]) + "\n")

#     print(f"All paid expense claims exported to {filename} ({total_count} total claims)")
#     return rows

def export_paid_expense_claims_by_date(tenant_id, start_date, end_date, filename="JOP_paid_expense_claims.txt"):
    rows = []
    total_count = 0
    current_start = start_date

    while True:
        url = (
            f"https://api.xero.com/api.xro/2.0/ExpenseClaims"
            f"?where=Status==\"PAID\" && Date>=DateTime({current_start}) && Date<=DateTime({end_date})"
            f"&pageSize=100"
        )
        data = safe_request(url, tenant_id, page=1)
        if not data:
            break

        claims = data.get("ExpenseClaims", [])
        if not claims:
            break

        for claim in claims:
            contact = claim.get("Contact", {}).get("Name", "")
            for line in claim.get("LineItems", []):
                rows.append([
                    claim.get("ExpenseClaimID"),
                    format_xero_date(claim.get("Date")),
                    contact,
                    line.get("Description"),
                    line.get("AccountCode"),
                    line.get("Quantity"),
                    line.get("UnitAmount"),
                    line.get("LineAmount"),
                    claim.get("Total"),
                    claim.get("Status"),
                    "ExpenseClaim"
                ])
        total_count += len(claims)
        print(f"Fetched {len(claims)} claims from {current_start} to {end_date} (cumulative {total_count})")

        last_date = claims[-1].get("Date")
        if not last_date or last_date >= end_date:
            break
        current_start = last_date[:10]  # next day after last fetched
        time.sleep(0.5)

    # Write to file
    with open(filename, "w", encoding="utf-8") as f:
        header = ["ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
        f.write("|".join(header) + "\n")
        for r in rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")

    print(f"All paid expense claims exported to {filename} ({total_count} total claims)")

    # ✅ Return the rows so caller knows how many were exported
    return rows

# def export_paid_expense_claims_by_date(tenant_id, start_date, end_date, filename="JOP_paid_expense_claims.txt"):
#     rows = []
#     total_count = 0
#     current_start = start_date

#     while True:
#         url = (
#             f"https://api.xero.com/api.xro/2.0/ExpenseClaims"
#             f"?where=Status==\"PAID\" && Date>=DateTime({current_start}) && Date<=DateTime({end_date})"
#             f"&pageSize=100"
#         )
#         data = safe_request(url, tenant_id, page=1)
#         if not data:
#             break

#         claims = data.get("ExpenseClaims", [])
#         if not claims:
#             break

#         for claim in claims:
#             contact = claim.get("Contact", {}).get("Name", "")
#             for line in claim.get("LineItems", []):
#                 rows.append([
#                     claim.get("ExpenseClaimID"),
#                     format_xero_date(claim.get("Date")),
#                     contact,
#                     line.get("Description"),
#                     line.get("AccountCode"),
#                     line.get("Quantity"),
#                     line.get("UnitAmount"),
#                     line.get("LineAmount"),
#                     claim.get("Total"),
#                     claim.get("Status"),
#                     "ExpenseClaim"
#                 ])
#         total_count += len(claims)
#         print(f"Fetched {len(claims)} claims from {current_start} to {end_date} (cumulative {total_count})")

#         # Move start date forward to last claim fetched + 1 day
#         last_date = claims[-1].get("Date")
#         if not last_date or last_date >= end_date:
#             break
#         current_start = last_date[:10]  # next day after last fetched
#         time.sleep(0.5)

#     with open(filename, "w", encoding="utf-8") as f:
#         header = ["ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
#         f.write("|".join(header) + "\n")
#         for r in rows:
#             f.write("|".join([str(x) if x else "" for x in r]) + "\n")

#     print(f"All paid expense claims exported to {filename} ({total_count} total claims)")
#     return rows

# -----------------------------
# Combine all paid invoices + expense claims
# -----------------------------
# def export_all_paid_invoices_combined(tenant_id, filename="JOP_all_paid_invoices.txt"):
#     sales = export_paid_invoices(tenant_id, "ACCREC", "JOP_paid_sales.txt", "Sale")
#     expenses = export_paid_invoices(tenant_id, "ACCPAY", "JOP_paid_expenses.txt", "Expense")
#     expense_claims = export_paid_expense_claims(tenant_id, "JOP_paid_expense_claims.txt")
#     all_rows = sales + expenses + expense_claims

#     with open(filename, "w", encoding="utf-8") as f:
#         header = ["InvoiceNumber/ID","Date","Contact","Description","AccountCode","Quantity","UnitAmount","LineAmount","Total","Status","Type"]
#         f.write("|".join(header) + "\n")
#         for r in all_rows:
#             f.write("|".join([str(x) if x else "" for x in r]) + "\n")
#     print(f"All paid sales, invoices, and expense claims exported to {filename} ({len(all_rows)} total records)")

def export_all_paid_invoices_combined(
    tenant_id,
    start_date="2010-01-01",
    end_date="2030-12-31",
    filename="JOP_all_paid_invoices.txt"
    ):
    # -----------------------------
    # 1️⃣ Paid sales invoices (ACCREC)
    # -----------------------------
    print("Exporting all paid sales invoices...")
    sales = export_paid_invoices(tenant_id, "ACCREC", "JOP_paid_sales.txt", "Sale")
    print(f"Total sales invoices exported: {len(sales)}\n")

    # -----------------------------
    # 2️⃣ Paid supplier invoices (ACCPAY)
    # -----------------------------
    print("Exporting all paid supplier invoices (expenses)...")
    expenses = export_paid_invoices(tenant_id, "ACCPAY", "JOP_paid_expenses.txt", "Expense")
    print(f"Total expense invoices exported: {len(expenses)}\n")

    # -----------------------------
    # 3️⃣ Paid expense claims
    # -----------------------------
    print("Exporting all paid expense claims...")
    expense_claims = export_paid_expense_claims_by_date(
        tenant_id,
        start_date=start_date,
        end_date=end_date,
        filename="JOP_paid_expense_claims.txt"
    )
    print(f"Total expense claims exported: {len(expense_claims)}\n")

    # -----------------------------
    # 4️⃣ Combine all records
    # -----------------------------
    all_rows = sales + expenses + expense_claims
    print(f"Writing combined file with {len(all_rows)} total records...")

    with open(filename, "w", encoding="utf-8") as f:
        header = [
            "InvoiceNumber/ID",
            "Date",
            "Contact",
            "Description",
            "AccountCode",
            "Quantity",
            "UnitAmount",
            "LineAmount",
            "Total",
            "Status",
            "Type"
        ]
        f.write("|".join(header) + "\n")
        for r in all_rows:
            f.write("|".join([str(x) if x else "" for x in r]) + "\n")

    print(f"All paid sales, invoices, and expense claims exported to {filename} ({len(all_rows)} total records)")

    return all_rows

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

    # Original exports
    export_invoices_to_text(tenant_id, "ACCREC", "JOP_sales.txt", "Sales")
    export_invoices_to_text(tenant_id, "ACCPAY", "JOP_expenses.txt", "Expenses")
    export_payments(tenant_id)
    export_accounts(tenant_id)
    export_contacts(tenant_id)
    export_bank_transactions(tenant_id)
    export_tracking_categories(tenant_id)

    # Paid invoices + expense claims
    export_all_paid_invoices_combined(tenant_id)

if __name__ == "__main__":
    main()