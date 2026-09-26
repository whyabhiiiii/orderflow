import random

from workers.celery_app import celery


@celery.task(name="calculate_eta")
def calculate_eta(order_id: int, restaurant_lat: float, restaurant_lng: float,
                  delivery_lat: float, delivery_lng: float):
    lat_diff = abs(restaurant_lat - delivery_lat)
    lng_diff = abs(restaurant_lng - delivery_lng)
    distance_km = ((lat_diff ** 2 + lng_diff ** 2) ** 0.5) * 111

    speed_kmh = 30
    travel_minutes = (distance_km / speed_kmh) * 60
    prep_minutes = random.randint(10, 25)

    eta = int(travel_minutes + prep_minutes)
    return {"order_id": order_id, "estimated_minutes": max(eta, 15)}


@celery.task(name="send_notification")
def send_notification(user_id: int, message: str, channel: str = "push"):
    print(f"[notification] user={user_id} channel={channel} message={message}")
    return {"sent": True, "user_id": user_id}


@celery.task(name="find_nearby_drivers")
def find_nearby_drivers(restaurant_lat: float, restaurant_lng: float, radius_km: float = 5.0):
    print(f"[driver_search] looking near ({restaurant_lat}, {restaurant_lng}) within {radius_km}km")
    return {"searched": True, "radius_km": radius_km}
