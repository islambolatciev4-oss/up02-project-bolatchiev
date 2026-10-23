price = float(input("Введите цену: "))
percent = float(input("Введите скидку (%): "))

final_price = price * (1 - percent / 100)

print(f"Цена со скидкой: {final_price:.2f} руб.")