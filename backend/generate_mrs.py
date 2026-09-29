import os

mr_dir = r"c:\Users\Laptop\Documents\GitHub\bigdata_project\backend\core_api\utils\mapreduce"

# Fix mapper2
mapper2 = """#!/usr/bin/env python3
import sys

# MapReduce 2: Đếm số lượng sản phẩm theo nguồn dữ liệu (Source)
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\\t')
    if len(parts) >= 15:
        source = parts[13].strip()
        print(f"{source}\\t1")
"""
with open(os.path.join(mr_dir, "mapper2.py"), "w", encoding="utf-8") as f: f.write(mapper2)

# Fix reducer2
reducer2 = """#!/usr/bin/env python3
import sys

current_source = None
count = 0

print("SOURCE\\tTOTAL_PRODUCTS")
print("-" * 30)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    
    try:
        source, val = line.split('\\t', 1)
        val = int(val)
    except ValueError:
        continue

    if current_source == source:
        count += val
    else:
        if current_source:
            print(f"{current_source}\\t{count}")
        current_source = source
        count = val

if current_source == source:
    print(f"{current_source}\\t{count}")
"""
with open(os.path.join(mr_dir, "reducer2.py"), "w", encoding="utf-8") as f: f.write(reducer2)

# Create mr3 to mr8
mrs = {
    3: ("Min price by brand", "brand = parts[0]", "price = parts[7]", "MIN_PRICE", "min_price = min(min_price, price)"),
    4: ("Max price by brand", "brand = parts[0]", "price = parts[7]", "MAX_PRICE", "max_price = max(max_price, price)"),
    5: ("Count products by price range", 
        "price = float(parts[7]); range_name = '<10M' if price < 10000000 else ('10M-20M' if price <= 20000000 else '>20M')", 
        "1", "COUNT", "count += val"),
    6: ("Average price by source", "source = parts[13]", "price = parts[7]", "AVG_PRICE", "total += price; count += 1"),
    7: ("Count products by brand", "brand = parts[0]", "1", "COUNT", "count += val"),
    8: ("Max price by source", "source = parts[13]", "price = parts[7]", "MAX_PRICE", "max_price = max(max_price, price)")
}

for i in range(3, 9):
    desc, key_logic, val_logic, out_col, agg_logic = mrs[i]
    
    mapper_code = f"""#!/usr/bin/env python3
import sys
# MR {i}: {desc}
for line in sys.stdin:
    line = line.strip()
    if not line: continue
    parts = line.split('\\t')
    if len(parts) >= 5:
        try:
            {key_logic}
            key = str({key_logic.split(' = ')[0]})
            val = str({val_logic.split(' = ')[0]})
            print(f"{{key}}\\t{{val}}")
        except: pass
"""
    with open(os.path.join(mr_dir, f"mapper{i}.py"), "w", encoding="utf-8") as f: f.write(mapper_code)

    reducer_code = f"""#!/usr/bin/env python3
import sys

current_key = None
total = 0.0
count = 0
min_price = float('inf')
max_price = 0.0

print("KEY\\t{out_col}")
print("-" * 30)

for line in sys.stdin:
    line = line.strip()
    if not line: continue
    
    try:
        key, val_str = line.split('\\t', 1)
        val = float(val_str)
        price = float(val_str)
    except:
        continue

    if current_key == key:
        {agg_logic}
    else:
        if current_key:
            if "{out_col}" == "AVG_PRICE": print(f"{{current_key}}\\t{{total/count:.2f}}")
            elif "{out_col}" == "MIN_PRICE": print(f"{{current_key}}\\t{{min_price}}")
            elif "{out_col}" == "MAX_PRICE": print(f"{{current_key}}\\t{{max_price}}")
            else: print(f"{{current_key}}\\t{{count}}")
        
        current_key = key
        total = price
        count = int(val)
        min_price = price
        max_price = price

if current_key == key:
    if "{out_col}" == "AVG_PRICE": print(f"{{current_key}}\\t{{total/count:.2f}}")
    elif "{out_col}" == "MIN_PRICE": print(f"{{current_key}}\\t{{min_price}}")
    elif "{out_col}" == "MAX_PRICE": print(f"{{current_key}}\\t{{max_price}}")
    else: print(f"{{current_key}}\\t{{count}}")
"""
    with open(os.path.join(mr_dir, f"reducer{i}.py"), "w", encoding="utf-8") as f: f.write(reducer_code)

print("Created 8 MapReduce scripts successfully!")
