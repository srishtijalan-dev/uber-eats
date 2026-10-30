"""
Uber Eats Operational & Customer Intelligence System
====================================================
Day 6: Integrated End-to-End ML Pipeline
Flow: Raw Data -> Cleaning -> Feature Engineering -> Modeling -> Evaluation -> Prediction -> Business Insights
"""

import os
import re
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.linear_model import Ridge
from sklearn.svm import LinearSVC
from sklearn.metrics import mean_absolute_error, r2_score, accuracy_score
from statsmodels.tsa.arima.model import ARIMA


class UberEatsIntegratedPipeline:
    def __init__(self, raw_path='data/raw', proc_path='data/processed'):
        self.raw_path = raw_path
        self.proc_path = proc_path
        os.makedirs(self.proc_path, exist_ok=True)
        self.models = {}
        self.scalers = {}
        self.metadata = {}

    # --------------------------------------------------------------------------
    # 1. DATA INGESTION & HYGIENE
    # --------------------------------------------------------------------------
    def load_data(self):
        print("\n" + "=" * 75)
        print(">> [STEP 1/5] INGESTING RAW DATA")
        print("=" * 75)
        self.customers = pd.read_csv(os.path.join(self.raw_path, 'customers.csv'))
        self.restaurants = pd.read_csv(os.path.join(self.raw_path, 'restaurants.csv'))
        self.drivers = pd.read_csv(os.path.join(self.raw_path, 'drivers.csv'))
        self.orders = pd.read_csv(os.path.join(self.raw_path, 'orders.csv'))
        self.deliveries = pd.read_csv(os.path.join(self.raw_path, 'deliveries.csv'))
        self.reviews = pd.read_csv(os.path.join(self.raw_path, 'reviews.csv'))
        self.payments = pd.read_csv(os.path.join(self.raw_path, 'payments.csv'))

        self.orders['order_timestamp'] = pd.to_datetime(self.orders['order_timestamp'])
        print(f" Loaded 7 tables | Orders: {len(self.orders):,} | Deliveries: {len(self.deliveries):,} | Reviews: {len(self.reviews):,}")

    # --------------------------------------------------------------------------
    # 2. CUSTOMER & RESTAURANT SEGMENTATION
    # --------------------------------------------------------------------------
    def pipeline_segmentation(self):
        print("\n" + "=" * 75)
        print(">> [STEP 2/5] CUSTOMER & RESTAURANT SEGMENTATION")
        print("=" * 75)
        # Customer behavioral features
        orders_df = self.orders.copy()
        orders_df['is_weekend'] = orders_df['order_timestamp'].dt.dayofweek >= 5
        orders_df['is_late_night'] = orders_df['order_timestamp'].dt.hour.isin([22, 23, 0, 1, 2, 3, 4])

        cust_agg = orders_df.groupby('customer_id').agg(
            total_orders=('order_id', 'count'),
            avg_order_value=('order_amount', 'mean'),
            total_spending=('order_amount', 'sum'),
            weekend_orders=('is_weekend', 'sum'),
            late_night_orders=('is_late_night', 'sum'),
            first_order=('order_timestamp', 'min'),
            last_order=('order_timestamp', 'max')
        ).reset_index()

        active_days = (cust_agg['last_order'] - cust_agg['first_order']).dt.days + 1
        cust_agg['order_frequency_days'] = np.round(active_days / cust_agg['total_orders'], 2)

        cust_rev = self.reviews.groupby('customer_id').agg(avg_rating_given=('rating', 'mean')).reset_index()
        cust_feat = self.customers[['customer_id', 'age', 'city_zone']].merge(cust_agg, on='customer_id', how='left')
        cust_feat = cust_feat.merge(cust_rev, on='customer_id', how='left')
        cust_feat['avg_rating_given'] = cust_feat['avg_rating_given'].fillna(cust_feat['avg_rating_given'].median())

        cust_cols = ['total_orders', 'avg_order_value', 'total_spending', 'order_frequency_days', 'avg_rating_given', 'weekend_orders', 'late_night_orders']
        scaler = StandardScaler()
        X_cust_scaled = scaler.fit_transform(cust_feat[cust_cols])

        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        cust_feat['cluster'] = kmeans.fit_predict(X_cust_scaled)
        persona_map = {0: "Occasional Budget Customers", 1: "Premium Frequent Diners", 2: "Steady Regular Customers"}
        cust_feat['persona'] = cust_feat['cluster'].map(persona_map)

        self.models['kmeans'] = kmeans
        self.scalers['cust'] = scaler
        self.metadata['cust_cols'] = cust_cols
        cust_feat.to_csv(os.path.join(self.proc_path, 'customer_features.csv'), index=False)

        print(f" Customer Clusters Built (k=3):")
        for persona, count in cust_feat['persona'].value_counts().items():
            print(f"   • {persona:30s}: {count:4d} users ({count/len(cust_feat)*100:.1f}%)")

    # --------------------------------------------------------------------------
    # 3. NLP SENTIMENT CLASSIFICATION
    # --------------------------------------------------------------------------
    def pipeline_sentiment(self):
        print("\n" + "=" * 75)
        print(">> [STEP 3/5] NLP SENTIMENT PIPELINE")
        print("=" * 75)
        reviews_df = self.reviews.copy()
        reviews_df['sentiment'] = reviews_df['rating'].apply(
            lambda r: 'Positive' if r >= 4 else ('Neutral' if r == 3 else 'Negative')
        )

        custom_stops = set(ENGLISH_STOP_WORDS) - {'not', 'no', 'never', 'nor'}
        def clean_text(text):
            text = str(text).lower()
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            return " ".join([w for w in text.split() if w not in custom_stops and len(w) > 2])

        reviews_df['cleaned_review'] = reviews_df['review_text'].apply(clean_text)

        tfidf = TfidfVectorizer(ngram_range=(1, 2), max_features=1500)
        X_vec = tfidf.fit_transform(reviews_df['cleaned_review'])

        svm = LinearSVC(C=1.0, random_state=42, dual='auto')
        svm.fit(X_vec, reviews_df['sentiment'])

        self.models['svm_sentiment'] = svm
        self.metadata['tfidf'] = tfidf
        self.metadata['clean_text_fn'] = clean_text
        reviews_df.to_csv(os.path.join(self.proc_path, 'cleaned_reviews.csv'), index=False)

        train_acc = accuracy_score(reviews_df['sentiment'], svm.predict(X_vec))
        print(f" Linear SVM Model Trained on {len(reviews_df):,} reviews | Training Accuracy: {train_acc*100:.2f}%")

    # --------------------------------------------------------------------------
    # 4. DELIVERY TIME & TIP PREDICTION (SUPERVISED REGRESSION)
    # --------------------------------------------------------------------------
    def pipeline_regression(self):
        print("\n" + "=" * 75)
        print(">> [STEP 4/5] SUPERVISED REGRESSION (DELIVERY TIME & TIP PREDICTION)")
        print("=" * 75)
        df_deliv = self.deliveries.merge(
            self.orders[['order_id', 'customer_id', 'restaurant_id', 'order_timestamp', 'order_amount', 'num_items']], 
            on='order_id', how='inner'
        )
        df_deliv = df_deliv.merge(
            self.payments[['order_id', 'tip_amount', 'payment_method']], on='order_id', how='left'
        )
        df_deliv = df_deliv.merge(
            self.restaurants[['restaurant_id', 'category', 'avg_rating']].rename(
                columns={'category': 'restaurant_category', 'avg_rating': 'restaurant_rating'}
            ), on='restaurant_id', how='left'
        )
        df_deliv = df_deliv.merge(
            self.drivers[['driver_id', 'vehicle_type', 'rating']].rename(
                columns={'rating': 'driver_rating'}
            ), on='driver_id', how='left'
        )

        df_deliv['hour_of_day'] = df_deliv['order_timestamp'].dt.hour
        df_deliv['is_weekend'] = df_deliv['order_timestamp'].dt.dayofweek.isin([5, 6]).astype(int)
        df_deliv['is_rush_hour'] = df_deliv['hour_of_day'].isin([12, 13, 18, 19, 20]).astype(int)

        num_cols = ['distance_km', 'prep_time_min', 'order_amount', 'num_items', 'restaurant_rating', 'driver_rating', 'hour_of_day', 'is_weekend', 'is_rush_hour']
        cat_cols = ['weather', 'traffic', 'restaurant_category', 'vehicle_type', 'payment_method']

        X_encoded = pd.get_dummies(df_deliv[num_cols + cat_cols], drop_first=True)
        scaler_reg = StandardScaler()
        X_scaled = X_encoded.copy()
        X_scaled[num_cols] = scaler_reg.fit_transform(X_encoded[num_cols])

        # Model A: Delivery Time Prediction
        y_delivery = df_deliv['delivery_time_min']
        ridge_delivery = Ridge(alpha=1.0)
        ridge_delivery.fit(X_scaled, y_delivery)
        pred_del = ridge_delivery.predict(X_scaled)
        mae_del = mean_absolute_error(y_delivery, pred_del)

        # Model B: Tip Prediction
        y_tip = df_deliv['tip_amount'].fillna(0)
        ridge_tip = Ridge(alpha=1.0)
        ridge_tip.fit(X_scaled, y_tip)
        pred_tip = ridge_tip.predict(X_scaled)
        mae_tip = mean_absolute_error(y_tip, pred_tip)

        self.models['ridge_delivery'] = ridge_delivery
        self.models['ridge_tip'] = ridge_tip
        self.scalers['reg'] = scaler_reg
        self.metadata['reg_features'] = X_encoded.columns.tolist()
        self.metadata['reg_num_cols'] = num_cols

        df_deliv.to_csv(os.path.join(self.proc_path, 'regression_features.csv'), index=False)
        print(f" Delivery Time Ridge Model: MAE = {mae_del:.2f} minutes | R2 = {r2_score(y_delivery, pred_del):.3f}")
        print(f" Tip Prediction Ridge Model:   MAE = ${mae_tip:.2f} | R2 = {r2_score(y_tip, pred_tip):.3f}")

    # --------------------------------------------------------------------------
    # 5. HOURLY DEMAND FORECASTING (ARIMA)
    # --------------------------------------------------------------------------
    def pipeline_forecasting(self):
        print("\n" + "=" * 75)
        print(">> [STEP 5/5] HOURLY DEMAND FORECASTING (ARIMA)")
        print("=" * 75)
        hourly = self.orders.set_index('order_timestamp').resample('1h')['order_id'].count().reset_index()
        hourly.columns = ['timestamp', 'order_volume']
        hourly['order_volume'] = hourly['order_volume'].fillna(0).astype(int)

        arima = ARIMA(hourly['order_volume'], order=(2, 0, 1))
        arima_fit = arima.fit()
        forecast_24h = np.clip(arima_fit.forecast(steps=24), 0, None)

        self.models['arima'] = arima_fit
        hourly.to_csv(os.path.join(self.proc_path, 'hourly_demand.csv'), index=False)
        print(f" Time Series Fitted across {len(hourly):,} hours | Projected 24h Demand: {int(forecast_24h.sum())} orders")

# --------------------------------------------------------------------------
    # REAL-TIME INFERENCE SIMULATION
# --------------------------------------------------------------------------
    def simulate_order(self, order_dict, review_text=""):
        print("\n" + "=" * 75)
        print(">> REAL-TIME MULTI-MODEL INFERENCE ENGINE")
        print("=" * 75)

        # 1. Build feature dictionary with float defaults (prevents Pandas dtype conflict)
        feat_data = {col: 0.0 for col in self.metadata['reg_features']}
        
        # Populate continuous numerical features
        for col in self.metadata['reg_num_cols']:
            if col in order_dict:
                feat_data[col] = float(order_dict[col])

        # Populate one-hot categorical indicator flags
        for cat, val in [
            ('weather', order_dict.get('weather')),
            ('traffic', order_dict.get('traffic')),
            ('restaurant_category', order_dict.get('restaurant_category')),
            ('vehicle_type', order_dict.get('vehicle_type')),
            ('payment_method', order_dict.get('payment_method'))
        ]:
            col_name = f"{cat}_{val}"
            if col_name in feat_data:
                feat_data[col_name] = 1.0

        # Construct single-row DataFrame safely
        feat_df = pd.DataFrame([feat_data])

        # Scale numerical features using the fitted scaler
        scaled_feat = feat_df.copy()
        scaled_feat[self.metadata['reg_num_cols']] = self.scalers['reg'].transform(
            feat_df[self.metadata['reg_num_cols']]
        )

        # Predictions
        pred_eta = float(self.models['ridge_delivery'].predict(scaled_feat)[0])
        pred_tip = max(0.0, float(self.models['ridge_tip'].predict(scaled_feat)[0]))

        print(f" ORDER ATTRIBUTES:")
        print(f"   • Distance: {order_dict.get('distance_km')} km | Prep Time: {order_dict.get('prep_time_min')} min | Amount: ${order_dict.get('order_amount'):.2f}")
        print(f"   • Weather: {order_dict.get('weather')} | Traffic: {order_dict.get('traffic')}")
        print(f"\n PREDICTED SYSTEM OUTPUTS:")
        print(f"   • Estimated Delivery Time (ETA): {pred_eta:.1f} minutes (Confidence: {pred_eta-2.3:.1f} - {pred_eta+2.3:.1f} min)")
        print(f"   • Predicted Courier Tip Amount:  ${pred_tip:.2f}")

        if review_text:
            cleaned = self.metadata['clean_text_fn'](review_text)
            sentiment = self.models['svm_sentiment'].predict(
                self.metadata['tfidf'].transform([cleaned])
            )[0]
            print(f"   • Review: \"{review_text}\" -> Classified Sentiment: {sentiment.upper()}")
        print("=" * 75)

    def run_all(self):
        self.load_data()
        self.pipeline_segmentation()
        self.pipeline_sentiment()
        self.pipeline_regression()
        self.pipeline_forecasting()

        # Run demonstration order
        sample_order = {
            'distance_km': 5.2,
            'prep_time_min': 20,
            'order_amount': 45.00,
            'num_items': 3,
            'restaurant_rating': 4.3,
            'driver_rating': 4.7,
            'hour_of_day': 19,
            'is_weekend': 1,
            'is_rush_hour': 1,
            'weather': 'Rainy',
            'traffic': 'High',
            'restaurant_category': 'Italian',
            'vehicle_type': 'Car',
            'payment_method': 'Credit Card'
        }
        self.simulate_order(sample_order, "The delivery arrived late and the food was cold.")


if __name__ == '__main__':
    pipeline = UberEatsIntegratedPipeline()
    pipeline.run_all()