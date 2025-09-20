# Copyright (c) 2025 Kyle Lopin (Naresuan University) <kylel@nu.ac.th>

"""

"""

__author__ = "Kyle Vitautas Lopin"

import time

def using_modulo(nums):
    count = 0
    for n in nums:
        if n % 2 == 1:  # check for odd
            count += 1
    return count

def using_bitwise(nums):
    count = 0
    for n in nums:
        if n & 0x01:  # check for odd
            count += 1
    return count

# Generate a list of test numbers
RANGE = 10_000_000
nums = list(range(RANGE))  # 10 million numbers

# Time using bitwise 1
start = time.perf_counter()
bit_result = using_bitwise(nums)
bit_time = time.perf_counter() - start
print(f"Using bitwise:  {RANGE} numbers in {bit_time:.4f} seconds")

# Time using modulo
start = time.perf_counter()
mod_result = using_modulo(nums)
mod_time = time.perf_counter() - start

# Time using bitwise 2
start = time.perf_counter()
bit_result = using_bitwise(nums)
bit_time = time.perf_counter() - start

# Display results
print(f"Using modulo:   {RANGE} numbers in {mod_time:.4f} seconds")
print(f"Using bitwise:  {RANGE} numbers in {bit_time:.4f} seconds")

