# /// script
# requires-python = ">=3.11"
# dependencies = ["curl_cffi"]
# ///

from curl_cffi import requests

CENTER_OID = "6F000000014BHGWDVI"  # zkm
BASE = "https://iframe.cineorder.filmpalast.net"

s = requests.Session(impersonate="chrome120")
s.get("https://iframe.cineorder.filmpalast.net/")  # warm-up, gets cookies
print(s.get("https://iframe.cineorder.filmpalast.net/api/session").json())
s.get(f"{BASE}/zkm")  # warm-up, gets cf cookies

r = s.get(
    f"{BASE}/api/session",
    headers={
        "accept": "application/json",
        "center-oid": CENTER_OID,
        "referer": f"{BASE}/zkm",
    },
)
print(r.status_code, r.json())