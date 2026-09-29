import sys

# Reducer 2: Tổng hợp số lượng sản phẩm theo từng nguồn

current_source = None
current_count = 0

print("SOURCE\tTOTAL_PRODUCTS")
print("-" * 30)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
        
    try:
        source, count_str = line.split('\t', 1)
        count = int(count_str)
    except ValueError:
        continue

    if current_source == source:
        current_count += count
    else:
        if current_source:
            print(f"{current_source}\t{current_count}")
        current_source = source
        current_count = count

# In ra nguồn cuối cùng
if current_source == source:
    print(f"{current_source}\t{current_count}")
