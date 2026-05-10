def welcome(name, greeting="Welcome"):
    print(f"Welcome, {name}!")

welcome("Alice")
welcome("Bob", "Hello")
welcome( greeting="Hi", name="Charlie")

def atzeret(a:int) -> int:
    addtion = atzeret(a-1) if a > 0 else 0
    return a + addtion

print(atzeret(5)) 


def calculate_bonus(salary, bonus_percentage=0.1) -> float:
    """Calculate the bonus based on salary and bonus percentage.
    
    Args:
        salary (float): The base salary.
        bonus_percentage (float, optional): The percentage of the salary to be given as a bonus. Defaults to 0.1 (10%).
    
    Returns:
        float: The calculated bonus amount.
    """
    return salary * bonus_percentage

print(calculate_bonus(50000))  # Output: 5000.0
print(calculate_bonus(50000, 0.2))  # Output: 10000.0

#accessing the docstring
print(calculate_bonus.__doc__)
help(calculate_bonus)