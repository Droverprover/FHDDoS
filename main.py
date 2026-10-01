import requests
import concurrent.futures
import time
import random
import os
import statistics
from itertools import cycle

USER_AGENTS = [
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{v}.0"
    for v in range(120, 125)
] + [
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/{v}.0"
    for v in range(120, 125)
] + [
    f"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/{v}.0"
    for v in range(120, 125)
] + [
    f"Mozilla/5.0 (X11; Linux x86_64) Chrome/{v}.0"
    for v in range(120, 125)
] + [
    f"Mozilla/5.0 (X11; Linux x86_64) Firefox/{v}.0"
    for v in range(120, 125)
] + [
    f"Mozilla/5.0 (Linux; Android {v}) Chrome/{120+i}.0 Mobile"
    for i, v in enumerate([10, 11, 12, 13, 14])
] + [
    f"Mozilla/5.0 (iPhone; CPU iPhone OS {v}_0) Safari/604.1"
    for v in range(13, 18)
] + [
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/{v}.0"
    for v in range(120, 125)
]

# Hard safety limits for a controlled performance test
MAX_WORKERS = 10
MAX_REQUESTS = 300
MAX_DURATION = 60
MAX_RPS = 5


def banner():
    os.system("cls" if os.name == "nt" else "clear")

    print(r"""
███████╗██╗  ██╗██████╗ ██████╗  ██████╗ ███████╗
██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
█████╗  ███████║██║  ██║██║  ██║██║  ██║███████╗
██╔══╝  ██╔══██║██║  ██║██║  ██║██║  ██║╚════██║
██║     ██║  ██║██████╔╝██████╔╝╚██████╔╝███████║
╚═╝     ╚═╝  ╚═╝╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

                 FHDDoS-Attack
          Tool By : FhDDoS Team Y
             Version : 1.0.0
             FH-DDoS-Attack
             2026 Created tool
""")


def request_once(url, request_id, ua):
    start = time.perf_counter()

    try:
        r = requests.get(
            url,
            headers={
                "User-Agent": ua,
                "Accept": "*/*"
            },
            timeout=10
        )

        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": r.status_code,
            "latency": elapsed,
            "error": None
        }

    except requests.RequestException as e:
        elapsed = time.perf_counter() - start

        return {
            "id": request_id,
            "status": None,
            "latency": elapsed,
            "error": str(e)
        }


def main():
    banner()

    print("[1] DDoS Attack High [Attack]")
    print("[2] Security Header Scan")
    print("[3] Exit")

    choice = input("\nselect a number : ").strip()

    if choice == "2":
        url = input("Link : ").strip()

        try:
            r = requests.get(url, timeout=10)

            print("\n=== SECURITY HEADERS ===")

            headers = [
                "Content-Security-Policy",
                "Strict-Transport-Security",
                "X-Content-Type-Options",
                "X-Frame-Options",
                "Referrer-Policy",
                "Permissions-Policy"
            ]

            for h in headers:
                value = r.headers.get(h)

                if value:
                    print(f"[+] {h}: {value}")
                else:
                    print(f"[-] {h}: missing")

        except requests.RequestException as e:
            print(f"Error: {e}")

        return

    if choice == "3":
        return

    if choice != "1":
        print("Invalid selection.")
        return

    url = input("\nLink : ").strip()

    try:
        requests_number = int(
            input(f"Requests number (max {MAX_REQUESTS}) : ")
        )

        workers = int(
            input(f"Workers (max {MAX_WORKERS}) : ")
        )

        duration = int(
            input(f"Time in seconds (max {MAX_DURATION}) : ")
        )

        rps = int(
            input(f"Max requests/sec (max {MAX_RPS}) : ")
        )

    except ValueError:
        print("Invalid number.")
        return

    requests_number = min(requests_number, MAX_REQUESTS)
    workers = min(workers, MAX_WORKERS)
    duration = min(duration, MAX_DURATION)
    rps = min(rps, MAX_RPS)

    print("\n================================")
    print("       Attack Started! DDoS Attack High Slowlories    ")
    print("================================")
    print(f"Target       : {url}")
    print(f"Requests     : {requests_number}")
    print(f"Workers      : {workers}")
    print(f"Duration     : {duration}s")
    print(f"Max RPS      : {rps}")
    print(f"User-Agents  : {len(USER_AGENTS)}")
    print("================================\n")

    ua_cycle = cycle(USER_AGENTS)
    results = []

    start_time = time.perf_counter()
    next_request_time = start_time

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=workers
    ) as executor:

        futures = []

        for i in range(requests_number):

            now = time.perf_counter()

            if now - start_time >= duration:
                break

            if now < next_request_time:
                time.sleep(next_request_time - now)

            futures.append(
                executor.submit(
                    request_once,
                    url,
                    i + 1,
                    next(ua_cycle)
                )
            )

            next_request_time += 1 / rps

        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)

            if result["status"]:
                print(
                    f"[{result['id']:03d}] "
                    f"{result['status']} | "
                    f"{result['latency']:.3f}s"
                )
            else:
                print(
                    f"[{result['id']:03d}] ERROR | "
                    f"{result['error']}"
                )

    elapsed = time.perf_counter() - start_time

    latencies = [
        x["latency"]
        for x in results
        if x["latency"] is not None
    ]

    successful = [
        x for x in results
        if x["status"] and 200 <= x["status"] < 300
    ]

    errors = [
        x for x in results
        if x["status"] is None
    ]

    print("\n========== SUMMARY ==========")
    print(f"Requests sent : {len(results)}")
    print(f"2xx responses : {len(successful)}")
    print(f"Errors        : {len(errors)}")

    if latencies:
        print(f"Average RT    : {statistics.mean(latencies):.3f}s")
        print(f"Min RT        : {min(latencies):.3f}s")
        print(f"Max RT        : {max(latencies):.3f}s")

    if elapsed > 0:
        print(f"Actual RPS    : {len(results) / elapsed:.2f}")

    print("=============================")


if __name__ == "__main__":
    main()
