import random
from datetime import datetime, timedelta

first_names = ["Иван", "Петр", "Алексей", "Мария", "Анна"]
last_names = ["Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов"]
patronymics = ["Иванович", "Петрович", "Алексеевич", "Михайлович", "Андреевна"]

def generate_clients(n):

    clients = []
    for _ in range(n):
        name = f"{random.choice(last_names)} {random.choice(first_names)} {random.choice(patronymics)}"
        clients.append({"name": name})
    return clients

car_models = ["Toyota Camry", "Ford Focus", "Nissan X-Trail", "Honda Civic"]
def generate_cars(n, client_ids):

    cars = []
    for _ in range(n):
        owner_id = random.choice(client_ids)
        model = random.choice(car_models)
        year = random.randint(1990, 2023)
        cars.append({"client_id": owner_id, "model": model, "year": year})
    return cars

def generate_orders(n, car_ids, master_ids):

    orders = []
    today = datetime.today().date()
    for _ in range(n):
        car = random.choice(car_ids)
        master = random.choice(master_ids)

        days_back = random.randint(0, 365)
        order_date = today - timedelta(days=days_back)
        orders.append({"car_id": car, "master_id": master, "order_date": order_date})
    return orders

def generate_order_services(order_ids, service_ids):

    entries = []
    for oid in order_ids:

        num_services = random.randint(1, 3)
        chosen = random.sample(service_ids, num_services)
        for sid in chosen:
            qty = random.randint(1, 5)
            entries.append({"order_id": oid, "service_id": sid, "quantity": qty})
    return entries