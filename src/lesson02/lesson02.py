def done():    print("--------------\r\n")

"""
# Input from command line function
name = input("What is your name? ")
print(f"Hello, {name}!")

# Simple loop from 0 to 2
for i in range(3):
    print(i)

# Loop with a step of 2
for i in range(2, 10, 2):
    print(i)

# Loop through a list of prices and print each price
prices = [1000, 50, 300]

for price in prices:
    print(price)

for i, price in enumerate(prices):
    print(f"Price {i}: {price}")

# Print numbers from 1 to 5 using a while loop
count = 1
while count <= 5:
    print(count)
    count += 1

done()

name = "Alice"
match name:
    case "Alice":
        print("Hello, Alice!")
    case "Bob":
        print("Hello, Bob!")
    case _:
        print("Hello, stranger!")

done()

"""

# Continue and break in loops
for i in range(10):
    if i % 2 == 0:
        continue  # Skip even numbers
    if i > 5:
        break  # Stop the loop if i is greater than 5
    print(i)

done()