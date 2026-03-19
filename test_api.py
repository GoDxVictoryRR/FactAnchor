import urllib.request
import urllib.parse
import json
import time

BASE_URL = 'https://factanchor-api.onrender.com/api/v1'
EMAIL = f'demo_finance_{int(time.time())}@factanchor.com'
PASSWORD = 'StrongPassword123!'

def request(url, method='GET', data=None, headers=None):
    if headers is None: headers = {}
    req = urllib.request.Request(url, method=method, headers=headers)
    if data is not None:
        data = json.dumps(data).encode('utf-8')
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, data=data) as response:
            return response.status, json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')

print('1. Signing up...')
status, user_data = request(f'{BASE_URL}/auth/signup', 'POST', {'email': EMAIL, 'password': PASSWORD})
if status != 200:
    print(f'Signup failed: {user_data}')
    exit(1)
print('Signup success!')

print('2. Logging in...')
status, token_data = request(f'{BASE_URL}/auth/login', 'POST', {'email': EMAIL, 'password': PASSWORD})
if status != 200:
    print(f'Login failed: {token_data}')
    exit(1)
token = token_data.get('access_token')
headers = {'Authorization': f'Bearer {token}'}
print('Login success! Got token.')

print('3. Submitting Demo Medical/Finance Report...')
report_text = 'The patient was prescribed 50mg of Aspirin daily. Our Q3 revenue reached $5.5 million with a 12% YoY growth.'
status, report_data = request(f'{BASE_URL}/reports', 'POST', {'text': report_text}, headers=headers)
if status not in (200, 202):
    print(f'Report submission failed: {report_data}')
    exit(1)
report_id = report_data.get('report_id')
print(f'Report submitted! ID: {report_id}')

print('4. Polling for completion...')
for i in range(15):
    status, data = request(f'{BASE_URL}/reports/{report_id}', 'GET', headers=headers)
    if status == 200:
        report_status = data.get('status')
        print(f'Check {i+1}: Status = {report_status}')
        if report_status == 'COMPLETE':
            print('Verification pipeline SUCCESSFUL!')
            print('Trust Score:', data.get('trust_score'))
            print('Claims detected:', len(data.get('claims', [])))
            for claim in data.get('claims', []):
                print(f"- {claim.get('content')} | Status: {claim.get('verification_status')} | Score: {claim.get('confidence_score')}")
            exit(0)
    else:
        print(f'Failed to fetch status: {data}')
    time.sleep(3)

print('Timeout: Report did not complete within 45 seconds.')
exit(1)
