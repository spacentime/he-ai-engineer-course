sales = [[150, 300, 200], [500, 400, 100], [300, 200, 600]]

total_sales = 0
avaerage_daily_sales = 0
daily_averages = []
total_averages = 0

for day, day_sales in enumerate(sales):
    daily_total = sum(day_sales)
    daily_average = daily_total / len(day_sales)
    daily_averages.append(daily_average)
    for sale in day_sales:
        print(f"Day {day + 1} Sale: {sale}")
        total_sales += sale

print(f"Total sales: {total_sales}")

for average in daily_averages:
    total_averages += average
    print(f"Day {day + 1} Average Sale: {average:.2f}")

print(f"Overall Average Sale: {total_averages / len(daily_averages):.2f}")