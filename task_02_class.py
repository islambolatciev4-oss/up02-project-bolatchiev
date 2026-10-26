class Product:
    def __init__(self, name, price, qty):
        self.name = name
        self.price = price
        self.qty = qty

    def total(self):
        return self.price * self.qty

    def info(self):
        return f"{self.name}: {self.price} × {self.qty} = {self.total()} руб."


products = [
    Product("Кроссовки", 8500, 3),
    Product("Ботинки", 15000, 1),
    Product("Туфли", 12000, 5),
]

for p in products:
    print(p.info())
