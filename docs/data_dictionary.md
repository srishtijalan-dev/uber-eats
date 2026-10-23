# Uber Eats Analytics - Data Dictionary

### 1. `customers.csv` (500 records)
* `customer_id` (PK): Unique customer identifier (`CUST_0001`)
* `age`: Age in years (18–64)
* `gender`: Customer gender (`Female`, `Male`, `Non-Binary`)
* `city_zone`: Living zone (`Downtown`, `Suburbs`, etc.)
* `signup_date`: Account creation date

### 2. `restaurants.csv` (50 records)
* `restaurant_id` (PK): Unique merchant identifier (`REST_001`)
* `restaurant_name`: Name of eatery
* `category`: Cuisine type (`Fast Food`, `Italian`, `Indian`, etc.)
* `avg_rating`: Historical restaurant rating (3.5–4.9)
* `avg_prep_time_min`: Average kitchen preparation time in minutes
* `city_zone`: Merchant neighborhood

### 3. `drivers.csv` (100 records)
* `driver_id` (PK): Unique driver identifier (`DRV_001`)
* `name`: Driver name
* `vehicle_type`: Vehicle mode (`Bike`, `Scooter`, `Car`, `EV`)
* `rating`: Historical driver rating (4.2–5.0)

### 4. `orders.csv` (5,000 records)
* `order_id` (PK): Unique transaction identifier (`ORD_00001`)
* `customer_id` (FK): Customer placing the order
* `restaurant_id` (FK): Restaurant fulfilling the order
* `order_timestamp`: Exact timestamp of order placement
* `order_amount`: Meal subtotal in USD ($)
* `num_items`: Number of items ordered
* `order_status`: Order status (`Delivered`, `Cancelled`)

### 5. `deliveries.csv` (~4,750 records)
* `delivery_id` (PK): Unique dispatch identifier (`DEL_00001`)
* `order_id` (FK): Associated order
* `driver_id` (FK): Assigned courier
* `distance_km`: Trip distance in kilometers
* `prep_time_min`: Kitchen preparation time in minutes
* `delivery_time_min`: Doorstep delivery duration in minutes
* `weather`: Weather condition (`Clear`, `Rainy`, `Foggy`, `Windy`)
* `traffic`: Congestion level (`Low`, `Medium`, `High`, `Congested`)

### 6. `payments.csv` (5,000 records)
* `payment_id` (PK): Unique billing identifier (`PAY_00001`)
* `order_id` (FK): Associated order
* `payment_method`: Channel (`Credit Card`, `Debit Card`, `Apple Pay / UPI`, `Uber Cash`)
* `tip_amount`: Tip paid by customer ($)
* `total_paid`: Total charge amount ($)
* `payment_status`: Transaction status (`Success`, `Refunded`)

### 7. `reviews.csv` (~2,850 records)
* `review_id` (PK): Unique review identifier (`REV_00001`)
* `order_id` (FK): Associated order
* `customer_id` (FK): Customer authoring the review
* `rating`: Star rating (1 to 5)
* `review_text`: Natural language customer feedback
* `review_timestamp`: Timestamp when review was submitted