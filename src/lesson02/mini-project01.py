customerType = input("What type of customer are you? (vip/business/regular) ")

dicount = 0
match customerType:
    case "vip":
        dicount = 0.2
    case "business":    
        dicount = 0.15
    case _:
        dicount = 0

purchaseAmount = float(input("Enter your purchase amount: "))

if purchaseAmount > 500:
    dicount += 0.05

finalAmount = purchaseAmount * (1 - dicount)
print(f"Your total discount amount is: {dicount * purchaseAmount:.2f}")
print(f"Your final amount after discount is: {finalAmount:.2f}")
print(f"You todal discount percentage is: {dicount * 100:.2f}%")
