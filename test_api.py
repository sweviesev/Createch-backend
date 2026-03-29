"""
Quick API test script — runs while dev server is running.
Tests: register, login (JWT), GET /api/projects/, GET /api/orders/, GET /api/services/
"""
import json
import urllib.request
import urllib.error
import urllib.parse

BASE = 'http://127.0.0.1:8000/api'

def post(path, data, token=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f'{BASE}{path}',
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def get(path, token):
    req = urllib.request.Request(f'{BASE}{path}', headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

print('=' * 60)
print('CREATECH API — ENDPOINT TESTING')
print('=' * 60)

# 1. Register
print('\n[1] POST /api/auth/register/')
code, resp = post('/auth/register/', {
    'email': 'apitest@createch.com',
    'first_name': 'API',
    'last_name': 'Tester',
    'phone': '09555123456',
    'birth_date': '2000-03-15',
    'password': 'Apitest@1234',
    'confirm_password': 'Apitest@1234',
    'role': 'creator',
})
print(f'  Status: {code}')
print(f'  Response: {json.dumps(resp, indent=2)[:300]}')

# 2. Login
print('\n[2] POST /api/auth/login/')
code, resp = post('/auth/login/', {
    'email': 'creator@createch.com',
    'password': 'Creator@1234',
})
print(f'  Status: {code}')
token = resp.get('access', '')
print(f'  Access token (first 40 chars): {token[:40]}...')

# 3. Profile
print('\n[3] GET /api/auth/me/')
code, resp = get('/auth/me/', token)
print(f'  Status: {code}')
print(f'  User: {resp.get("email")} | Role: {resp.get("role")}')

# 4. Projects
print('\n[4] GET /api/projects/')
code, resp = get('/projects/', token)
print(f'  Status: {code}')
print(f'  Count: {resp.get("count")} | Results sample: {resp.get("results", [{}])[0].get("title", "N/A")}')

# 5. Orders
print('\n[5] GET /api/orders/')
code, resp = get('/orders/', token)
print(f'  Status: {code}')
print(f'  Count: {resp.get("count")} | Results sample: {resp.get("results", [{}])[0].get("service_title", "N/A")}')

# 6. Services
print('\n[6] GET /api/services/')
code, resp = get('/services/', token)
print(f'  Status: {code}')
print(f'  Count: {resp.get("count")} | Results sample: {resp.get("results", [{}])[0].get("title", "N/A")}')

# 7. Wallet
print('\n[7] GET /api/wallet/')
code, resp = get('/wallet/', token)
print(f'  Status: {code}')
print(f'  Balance: ₱{resp.get("balance")} | Transactions: {len(resp.get("transactions", []))}')

print('\n' + '=' * 60)
print('All tests complete!')
print('=' * 60)
