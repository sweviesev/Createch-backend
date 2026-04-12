"""
Quick API test script — runs while dev server is running.
Tests: register, login (JWT), /api/auth/me/, GET /api/services/, GET /api/orders/
"""
import json
import urllib.request
import urllib.error

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
        body = e.read()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {'error': body.decode()[:200]}


def get(path, token=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{path}', headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read()
        try:
            return e.code, json.loads(body)
        except json.JSONDecodeError:
            return e.code, {'error': body.decode()[:200]}


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
    'password': 'Apitest@1234',
    'confirm_password': 'Apitest@1234',
    'role': 'client',
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

# 3. Profile (authenticated)
print('\n[3] GET /api/auth/me/')
code, resp = get('/auth/me/', token)
print(f'  Status: {code}')
print(f'  User: {resp.get("email")} | Role: {resp.get("role")}')

# 4. Services (public)
print('\n[4] GET /api/services/')
code, resp = get('/services/')
print(f'  Status: {code}')
results = resp.get('results', [])
print(f'  Count: {resp.get("count")} | First: {results[0].get("title", "N/A") if results else "N/A"}')

# 5. Orders
print('\n[5] GET /api/orders/')
code, resp = get('/orders/', token)
print(f'  Status: {code}')
results = resp.get('results', [])
print(f'  Count: {resp.get("count")} | First: {results[0].get("service_title", "N/A") if results else "N/A"}')

# 6. Users
print('\n[6] GET /api/users/')
code, resp = get('/users/')
print(f'  Status: {code}')
results = resp.get('results', [])
print(f'  Count: {resp.get("count")} | First: {results[0].get("email", "N/A") if results else "N/A"}')

print('\n' + '=' * 60)
print('All tests complete!')
print('=' * 60)
