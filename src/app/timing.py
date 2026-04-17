import time

def start_timer() -> float:
    start = time.perf_counter()
    return start

def end_timer(start : float) -> None:
    elapsed = time.perf_counter() - start

    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = elapsed % 60

    if hours > 0:
        print(f"\nTotal runtime: {hours}h {minutes}m {seconds:.2f}s")
    elif minutes > 0:
        print(f"\nTotal runtime: {minutes}m {seconds:.2f}s")
    else:
        print(f"\nTotal runtime: {seconds:.2f}s")