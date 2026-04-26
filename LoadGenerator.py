# import requests
# import random
# import time

# # ================= CONFIG =================

# BASE_URL = "http://52.87.209.224/:5000"   # 👈 update if needed

# URLS = [
#     "/",
#     "/health",
#     "/delay/1",
#     "/delay/2",
#     "/delay/3",
#     "/random-delay",
#     "/random-failure",
#     "/error/400",
#     "/error/404",
#     "/error/500",
#     "/exception"
# ]

# # ================= LOAD =================

# print("🚀 Starting Load...\n")

# while True:
#     url = random.choice(URLS)   # pick random endpoint
#     full_url = BASE_URL + url

#     try:
#         start = time.time()
#         response = requests.get(full_url, timeout=5)
#         latency = round(time.time() - start, 3)

#         print(f"{url} -> {response.status_code} | {latency}s")

#     except Exception as e:
#         print(f"{url} -> ERROR: {e}")

#     time.sleep(0.3)   # small delay (controls load)



import requests
import random
import time
import threading

BASE_URL = "http://52.87.209.224:5000"

ENDPOINTS = [
    "/", 
    "/delay/1",
    "/delay/2",
    "/random-delay",
    "/error/400",
    "/error/404",
    "/error/500",
    "/exception",
    "/random-failure",
    "/health"
]

# Weight distribution (realistic traffic pattern)
WEIGHTS = {
    "/": 25,
    "/health": 15,
    "/delay/1": 10,
    "/delay/2": 10,
    "/random-delay": 10,
    "/random-failure": 10,
    "/error/400": 5,
    "/error/404": 5,
    "/error/500": 5,
    "/exception": 5
}

def get_random_endpoint():
    return random.choices(
        population=list(WEIGHTS.keys()),
        weights=list(WEIGHTS.values()),
        k=1
    )[0]

def hit_api(thread_id):
    while True:
        endpoint = get_random_endpoint()
        url = BASE_URL + endpoint

        try:
            response = requests.get(url, timeout=5)
            print(f"[Thread-{thread_id}] {endpoint} -> {response.status_code}")
        except Exception as e:
            print(f"[Thread-{thread_id}] ERROR calling {endpoint}: {str(e)}")

        time.sleep(random.uniform(0.1, 1))  # simulate real users


def start_load(concurrency=5):
    threads = []

    for i in range(concurrency):
        t = threading.Thread(target=hit_api, args=(i,))
        t.daemon = True
        t.start()
        threads.append(t)

    # Keep main thread alive
    for t in threads:
        t.join()


if __name__ == "__main__":
    print("🔥 Starting Load Test...")
    start_load(concurrency=10)  # change concurrency here