def done():    print("--------------\r\n")

list = [80,9,17,5,60]

for i in range(len(list)):
    print(f"Index {i}: {list[i]}")

done()

for i, value in enumerate(list):
    print(f"Index {i}: {value}")

done()

# Break example: Stop the loop after index 2

for i, value in enumerate(list):
    if i > 2:
        break
    print(f"Index {i}: {value}")

done()

# Continue example: Skip the value 17
for i, value in enumerate(list):
    if value == 17:
        continue
    print(f"Index {i}: {value}")

done()
