from datetime import datetime


def log(message, level="INFO"):
    timestamp = datetime.now()
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")

    message = f"{timestamp_str} {level}\t{message}"
    if level == "WARNING":
        print(f"\033[93m{message}\033[0m")
    elif level == "ERROR":
        print(f"\033[91m{message}\033[0m")
    elif level == "DEBUG":
        print(f"\033[94m{message}\033[0m")
    elif level == "INFO":
        print(f"\033[92m{message}\033[0m")
    else:
        pass
