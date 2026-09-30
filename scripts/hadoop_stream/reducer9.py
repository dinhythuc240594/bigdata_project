#!/usr/bin/env python3
import sys

def reducer():
    current_source = None
    current_count = 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            source, count = line.split('\t', 1)
            count = int(count)
        except ValueError:
            continue

        if current_source == source:
            current_count += count
        else:
            if current_source:
                print(f"{current_source}\t{current_count}")
            current_source = source
            current_count = count

    if current_source:
        print(f"{current_source}\t{current_count}")

if __name__ == "__main__":
    reducer()