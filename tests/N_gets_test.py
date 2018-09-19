import sys
from threading import Thread
import requests

N = int(sys.argv[1])

results = list(range(N))


def get_req(i):
    r = requests.get('https://api.github.com/user')
    results[i] = r.status_code
    print(i, "I requested")


def N_gets_test():
    threads = []
    for i in range(N):
        thread = Thread(target=get_req, args=(i,))
        thread.start()
        threads.append(thread)
    for t in threads:
        t.join()

    for i in range(len(results)):
        print(i + 1, results[i])


N_gets_test()