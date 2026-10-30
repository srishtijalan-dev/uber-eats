"""
Uber Eats Operational & Customer Intelligence System
Day 1: Synthetic Data Generation Script
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_uber_eats_data(output_dir="data/raw"):
    os.makedirs(output_dir, exist_ok=True)
    random.seed(42)
    np.random.seed(42)
    print("Starting data generation...")

    # 1. Customers (500)
    n_customers = 500
    customer_ids = [f"CUST_{i:04d}" for i in range(1, n_customers + 1)]
    ages = np.random.randint(18, 65, size=n_customers)
    genders = np.random.choice(
        ["Female", "Male", "Non-Binary"], size=n_customers, p=[0.48, 0.48, 0.04]
    )
    zones = [
        "Downtown",
        "Suburbs",
        "Northside",
        "West End",
        "University District",
    ]
    customer_zones = np.random.choice(zones, size=n_customers)
    signup_dates = pd.date_range(
        start="2025-01-01", periods=n_customers, freq="10h"
    ).strftime("%Y-%m-%d")

    df_customers = pd.DataFrame(
        {
            "customer_id": customer_ids,
            "age": ages,
            "gender": genders,
            "city_zone": customer_zones,
            "signup_date": signup_dates,
        }
    )
    df_customers.to_csv(f"{output_dir}/customers.csv", index=False)
    print("[1/7] Generated customers.csv")

    # 2. Restaurants (50)
    n_restaurants = 50
    restaurant_ids = [f"REST_{i:03d}" for i in range(1, n_restaurants + 1)]
    categories = [
        "Fast Food",
        "Indian",
        "Italian",
        "Healthy/Salads",
        "Asian/Sushi",
        "Mexican",
        "Desserts/Bakery",
    ]
    rest_cats = np.random.choice(categories, size=n_restaurants)
    rest_ratings = np.round(np.random.uniform(3.5, 4.9, size=n_restaurants), 1)
    rest_prep_times = np.random.randint(15, 35, size=n_restaurants)
    rest_zones = np.random.choice(zones, size=n_restaurants)

    df_restaurants = pd.DataFrame(
        {
            "restaurant_id": restaurant_ids,
            "restaurant_name": [
                f"Eatery_{c.split('/')[0]}_{i}"
                for i, c in enumerate(rest_cats, 1)
            ],
            "category": rest_cats,
            "avg_rating": rest_ratings,
            "avg_prep_time_min": rest_prep_times,
            "city_zone": rest_zones,
        }
    )
    df_restaurants.to_csv(f"{output_dir}/restaurants.csv", index=False)
    print("[2/7] Generated restaurants.csv")

    # 3. Drivers (100)
    n_drivers = 100
    driver_ids = [f"DRV_{i:03d}" for i in range(1, n_drivers + 1)]
    vehicles = ["Bike", "Scooter", "Car", "EV"]
    driver_vehicles = np.random.choice(
        vehicles, size=n_drivers, p=[0.25, 0.40, 0.25, 0.10]
    )
    driver_ratings = np.round(np.random.uniform(4.2, 5.0, size=n_drivers), 1)

    df_drivers = pd.DataFrame(
        {
            "driver_id": driver_ids,
            "name": [f"Driver_{i}" for i in range(1, n_drivers + 1)],
            "vehicle_type": driver_vehicles,
            "rating": driver_ratings,
        }
    )
    df_drivers.to_csv(f"{output_dir}/drivers.csv", index=False)
    print("[3/7] Generated drivers.csv")

    # 4. Orders (5,000)
    n_orders = 5000
    start_date = datetime(2026, 1, 1)
    date_offsets = np.random.randint(0, 180, size=n_orders)

    # Hourly distribution with lunch and dinner spikes
    hour_weights = np.array(
        [
            0.01,
            0.01,
            0.01,
            0.01,
            0.01,
            0.01,
            0.02,
            0.03,
            0.05,
            0.04,
            0.04,
            0.08,
            0.10,
            0.10,
            0.06,
            0.04,
            0.04,
            0.06,
            0.11,
            0.12,
            0.10,
            0.06,
            0.04,
            0.02,
        ]
    )
    hour_weights = hour_weights / hour_weights.sum()
    order_hours = np.random.choice(range(24), size=n_orders, p=hour_weights)
    order_minutes = np.random.randint(0, 60, size=n_orders)

    order_timestamps = [
        start_date + timedelta(days=int(d), hours=int(h), minutes=int(m))
        for d, h, m in zip(date_offsets, order_hours, order_minutes)
    ]
    order_timestamps.sort()

    order_ids = [f"ORD_{i:05d}" for i in range(1, n_orders + 1)]
    cust_refs = np.random.choice(customer_ids, size=n_orders)
    rest_refs = np.random.choice(restaurant_ids, size=n_orders)
    order_amounts = np.round(
        np.random.exponential(scale=26, size=n_orders) + 12, 2
    )
    order_amounts = np.clip(order_amounts, 10.0, 180.0)
    items_count = np.random.choice(
        [1, 2, 3, 4, 5, 6, 7],
        size=n_orders,
        p=[0.25, 0.35, 0.20, 0.10, 0.05, 0.03, 0.02],
    )
    order_status = np.random.choice(
        ["Delivered", "Cancelled"], size=n_orders, p=[0.95, 0.05]
    )

    df_orders = pd.DataFrame(
        {
            "order_id": order_ids,
            "customer_id": cust_refs,
            "restaurant_id": rest_refs,
            "order_timestamp": [
                t.strftime("%Y-%m-%d %H:%M:%S") for t in order_timestamps
            ],
            "order_amount": order_amounts,
            "num_items": items_count,
            "order_status": order_status,
        }
    )
    df_orders.to_csv(f"{output_dir}/orders.csv", index=False)
    print("[4/7] Generated orders.csv")

    # 5. Deliveries
    delivered_orders = df_orders[df_orders["order_status"] == "Delivered"].copy()
    n_deliv = len(delivered_orders)

    distances = np.round(
        np.random.gamma(shape=2.5, scale=1.8, size=n_deliv) + 0.8, 1
    )
    weathers = np.random.choice(
        ["Clear", "Rainy", "Foggy", "Windy"],
        size=n_deliv,
        p=[0.65, 0.20, 0.10, 0.05],
    )
    traffics = np.random.choice(
        ["Low", "Medium", "High", "Congested"],
        size=n_deliv,
        p=[0.30, 0.40, 0.20, 0.10],
    )

    prep_times = np.round(
        14
        + delivered_orders["num_items"].values * 2.8
        + np.random.normal(0, 3, size=n_deliv)
    ).astype(int)
    prep_times = np.clip(prep_times, 10, 60)

    traffic_pen = {"Low": 0, "Medium": 4, "High": 9, "Congested": 16}
    weather_pen = {"Clear": 0, "Rainy": 7, "Foggy": 4, "Windy": 2}
    t_pen = np.array([traffic_pen[t] for t in traffics])
    w_pen = np.array([weather_pen[w] for w in weathers])

    deliv_times = np.round(
        prep_times
        + distances * 3.2
        + t_pen
        + w_pen
        + np.random.normal(0, 3, size=n_deliv)
    ).astype(int)
    deliv_times = np.clip(deliv_times, 15, 95)

    df_deliveries = pd.DataFrame(
        {
            "delivery_id": [f"DEL_{i:05d}" for i in range(1, n_deliv + 1)],
            "order_id": delivered_orders["order_id"].values,
            "driver_id": np.random.choice(driver_ids, size=n_deliv),
            "distance_km": distances,
            "prep_time_min": prep_times,
            "delivery_time_min": deliv_times,
            "weather": weathers,
            "traffic": traffics,
        }
    )
    df_deliveries.to_csv(f"{output_dir}/deliveries.csv", index=False)
    print("[5/7] Generated deliveries.csv")

    # 6. Payments
    payment_methods = np.random.choice(
        ["Credit Card", "Debit Card", "Apple Pay / UPI", "Uber Cash"],
        size=n_orders,
        p=[0.45, 0.25, 0.20, 0.10],
    )
    has_tip = np.random.choice([0, 1], size=n_orders, p=[0.28, 0.72])
    base_tips = df_orders["order_amount"] * np.random.uniform(
        0.10, 0.22, size=n_orders
    )
    tips = np.round(has_tip * base_tips, 2)
    tips = np.where(df_orders["order_status"] == "Cancelled", 0.0, tips)
    total_paids = np.round(df_orders["order_amount"] + tips + 3.99, 2)

    df_payments = pd.DataFrame(
        {
            "payment_id": [f"PAY_{i:05d}" for i in range(1, n_orders + 1)],
            "order_id": df_orders["order_id"].values,
            "payment_method": payment_methods,
            "tip_amount": tips,
            "total_paid": total_paids,
            "payment_status": np.where(
                df_orders["order_status"] == "Cancelled", "Refunded", "Success"
            ),
        }
    )
    df_payments.to_csv(f"{output_dir}/payments.csv", index=False)
    print("[6/7] Generated payments.csv")

    # 7. Reviews
    review_sample = delivered_orders.sample(frac=0.60, random_state=42)
    n_rev = len(review_sample)
    merged_deliv = review_sample.merge(
        df_deliveries[["order_id", "delivery_time_min"]], on="order_id"
    )

    pos_reviews = [
        "Food arrived piping hot and was delicious! Great packaging.",
        "Super fast delivery and fresh food. Will definitely order again.",
        "Driver was polite, friendly, and followed delivery instructions perfectly.",
        "Best burgers in town! Crispy fries and arrived ahead of estimated time.",
        "Amazing experience, the meal was fresh, hot, and authentic.",
        "Everything was accurate, napkins and extra sauces included. 10/10!",
        "Great portion sizes and rapid delivery. Highly recommended!",
    ]
    neg_reviews = [
        "Food took over an hour and arrived freezing cold. Very disappointed.",
        "Missing items in my order! The drink and sides were completely missing.",
        "Delivery driver dumped the bag sideways and soup spilled everywhere.",
        "Terrible customer service. Late delivery and the food was stale and soggy.",
        "The fries were soggy and ice cold. Order was delayed by 40 minutes.",
        "Driver didn't ring bell or follow notes, food sat outside getting cold.",
        "Wrong order delivered completely! Ruined our dinner experience.",
    ]
    neu_reviews = [
        "Food was okay, but portion was smaller than expected for the price.",
        "Average taste. Delivery was on time but packaging was slightly crushed.",
        "Decent food, nothing extraordinary. Driver was quick.",
        "Took a bit longer than estimated, but food quality was acceptable.",
    ]

    ratings, texts = [], []
    for _, row in merged_deliv.iterrows():
        dt = row["delivery_time_min"]
        if dt > 55:
            r = np.random.choice([1, 2, 3], p=[0.65, 0.25, 0.10])
            t = np.random.choice(neg_reviews)
        elif dt < 35:
            r = np.random.choice([4, 5], p=[0.25, 0.75])
            t = np.random.choice(pos_reviews)
        else:
            r = np.random.choice([2, 3, 4, 5], p=[0.10, 0.35, 0.35, 0.20])
            t = np.random.choice(
                neu_reviews
                if r == 3
                else (pos_reviews if r > 3 else neg_reviews)
            )
        ratings.append(r)
        texts.append(t)

    order_times_dt = pd.to_datetime(merged_deliv["order_timestamp"])
    rev_times = order_times_dt + pd.to_timedelta(
        np.random.randint(45, 180, size=n_rev), unit="m"
    )

    df_reviews = pd.DataFrame(
        {
            "review_id": [f"REV_{i:05d}" for i in range(1, n_rev + 1)],
            "order_id": merged_deliv["order_id"].values,
            "customer_id": merged_deliv["customer_id"].values,
            "rating": ratings,
            "review_text": texts,
            "review_timestamp": rev_times.dt.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )
    df_reviews.to_csv(f"{output_dir}/reviews.csv", index=False)
    print("[7/7] Generated reviews.csv")
    print("\nSuccess: All 7 synthetic tables generated in data/raw/")


if __name__ == "__main__":
    generate_uber_eats_data()