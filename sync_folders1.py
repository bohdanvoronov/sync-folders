import os
import shutil
import time
import hashlib
import argparse


def get_file_hash(file_path):
    """Generate MD5 hash for a given file."""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()


def sync_directories(source, replica, log_file):
    """Synchronize contents of source directory with replica directory."""
    with open(log_file, 'a') as log:
        for root, _, files in os.walk(source):
            relative_path = os.path.relpath(root, source)
            replica_root = os.path.join(replica, relative_path)

            os.makedirs(replica_root, exist_ok=True)
            for file in files:
                source_file = os.path.join(root, file)
                replica_file = os.path.join(replica_root, file)

                if not os.path.exists(replica_file) or get_file_hash(source_file) != get_file_hash(replica_file):
                    shutil.copy2(source_file, replica_file)
                    message = f"Copied: {source_file} -> {replica_file}"
                    log.write(message + "\n")
                    print(message)

        for root, _, files in os.walk(replica):
            relative_path = os.path.relpath(root, replica)
            source_root = os.path.join(source, relative_path)

            for file in files:
                replica_file = os.path.join(root, file)
                source_file = os.path.join(source_root, file)

                if not os.path.exists(source_file):
                    os.remove(replica_file)
                    message = f"Removed: {replica_file}"
                    log.write(message + "\n")
                    print(message)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Directories")
    parser.add_argument("source", help="Source directory path")
    parser.add_argument("replica", help="Replica directory path")
    parser.add_argument("log_file", help="Log file path")
    parser.add_argument("interval", type=int, help="Sync interval in seconds")

    args = parser.parse_args()


    while True:
        sync_directories(args.source, args.replica, args.log_file)
        time.sleep(args.interval)