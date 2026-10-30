---

## 4. Model Comparison Summary

Across Days 2 through 5, multiple candidate algorithms were trained, tuned, and benchmarked against out-of-sample validation data.

| Task / Domain | Candidate Models | Primary Evaluation Metrics | Selected Model | Production Rationale & Tradeoffs |
| :--- | :--- | :--- | :--- | :--- |
| **Customer Segmentation (Day 2)** | • **K-Means** (k=2 to 7)<br>• **DBSCAN** | • Silhouette Score: **0.163**<br>• Inertia / Elbow Method<br>• Outlier Noise Detection | **K-Means (k=3) + DBSCAN** | K-Means established 3 clear marketing personas. DBSCAN was deployed in parallel to isolate 25 operational outlier accounts without distorting cluster centroids. |
| **Sentiment Analysis (Day 3)** | • **Linear SVM**<br>• **Multinomial Naive Bayes**<br>• **Rule-Based Lexicon** | • Accuracy: **98.3%** (SVM vs. NB)<br>• Macro F1: **0.98**<br>• Negative Recall: **1.00** | **Linear Support Vector Machine (LinearSVC)** | Linear SVM achieved maximum-margin separation across 1,500 TF-IDF features with zero false negatives on critical 1-star customer complaints. |
| **Delivery Time Prediction (Day 4)** | • **Ridge Regression (L2)**<br>• Baseline OLS Linear<br>• Lasso Regression (L1)<br>• Random Forest Regressor | • Ridge: **MAE 2.32 min**, RMSE 2.93 min, **R² = 0.938**<br>• OLS: MAE 2.32 min, R² = 0.938<br>• RF: MAE 2.80 min, R² = 0.909 | **Ridge Regression (L2)** | Matches OLS accuracy while regularizing collinear traffic and weather penalties. Executes in under 2 ms per inference. |
| **Hourly Demand Forecasting (Day 5)** | • **Meta Prophet (Additive)**<br>• **ARIMA(2, 0, 1)** | • ADF Stationarity (**p < 0.001**)<br>• ARIMA MAE: **1.09 orders/hr**<br>• Prophet MAE: **1.12 orders/hr** | **Meta Prophet** | Natively decomposes multi-frequency seasonal cycles (daily lunch and dinner peaks + weekend volume) without manual differencing. |

---

## 5. Business Analysis & Strategic Insights

### Q1: Which customer segments are most valuable?
* **Cluster 1: "Premium Frequent Diners"** (~28% of customer base, N = 139):
  * **Lifetime Value:** Averages **$553.79 in cumulative spend** with **13.8 total orders**.
  * **Velocity:** Re-orders every **11.4 days** (shortest inter-purchase interval on the platform).
  * **Habitual Patterns:** Drives the bulk of high-margin weekend dining (4.5 orders/user) and late-night ordering (1.6 orders/user).
* **Strategic Contrast:** Cluster 2 ("Steady Regulars", 46% of base) provides reliable recurring volume ($372.57 spend, 15.0-day gap), while Cluster 0 ("Occasional Budget", 26% of base) generates only $212.52 with an extended 22.1-day gap.

### Q2: Which restaurant segments require intervention?
* **24 out of 50 merchant partners (48%)** trigger operational warning thresholds:
  * **Severe Cancellation Rates:** Outlets like `Eatery_Fast Food_17` (8.0% cancellation rate), `Eatery_Mexican_11` (7.7%), and `Eatery_Mexican_4` (7.6%) exceed the platform tolerance limit (<= 3%).
  * **Preparation Delays:** Fast Food and Mexican outlets in `Downtown` and `West End` average prep times > 22.5 minutes, acting as the primary bottleneck for courier dispatch.
  * **Customer Dissatisfaction:** Partners with ratings below 3.8 (e.g., `Eatery_Fast Food_6` at 3.5 rating) account for over 40% of all 1-star reviews.

### Q3: What are the biggest causes of negative customer experiences?
1. **Late Delivery & Cold Food (68.4% of complaints):** Long transit durations (>45 minutes) causing meals to arrive cold, soggy, or congealed.
2. **Order Inaccuracy & Missing Items (31.2% of complaints):** Kitchen packaging errors where beverages, sauces, or combo sides were omitted.
3. **Food Damage & Transit Spillage (18.1% of complaints):** Container damage and liquid spillage, concentrated among two-wheel couriers delivering soups and drinks.

### Q4: Which factors drive delivery delays?
1. **Trip Distance (58.6% relative importance):** Each additional kilometer adds +3.2 minutes to doorstep duration.
2. **Kitchen Preparation Time (17.7% relative importance):** Unpredictable kitchen turnover directly drives courier curbside wait times.
3. **Traffic Congestion:** Heavy traffic introduces an estimated **+15.5-minute delay penalty** over free-flow conditions.
4. **Adverse Weather:** Heavy rain adds **+7.0 minutes**, while foggy conditions add **+4.2 minutes** due to reduced courier speeds.

### Q5: What factors influence tip amounts?
* **Order Basket Amount is the primary driver (r = 0.634):** Tipping behaves as an ad-valorem percentage of total food cost (average tip: **$4.22** across orders).
* **Delivery Performance has near-zero correlation with tips (r = 0.021):** Trip distance, weather, and delivery delays do not impact tip values because customer tips are selected upfront at application checkout prior to fulfillment.
* **Payment Method Segmentation:** Debit Card orders yield the highest average tip (**$4.38**), followed by Credit Cards (**$4.19**), Apple Pay / UPI (**$4.17**), and Uber Cash (**$4.05**).

### Q6: When should additional delivery capacity be deployed?
1. **Lunch Rush (12:00 PM – 2:00 PM):** Order volume surges 3.5x over morning baselines.
2. **Dinner Super-Peak (6:00 PM – 9:00 PM):** Accounts for 42% of total cumulative weekly volume.
* **Operational Deployment Rule:** Courier capacity must be staged **30 minutes prior** to peak windows (11:30 AM for lunch, 5:30 PM for dinner) to prevent fulfillment backlogs.

### Q7: Which locations and time periods experience demand spikes?
* **Geographic Concentration:** 75.6% of total order demand is concentrated in three dense urban zones:
  * **Downtown (1,315 orders):** Heaviest lunch peak (283 orders) and highest overall dinner volume (453 orders).
  * **West End (1,283 orders):** Highest platform lunch volume (299 orders) and dinner volume (435 orders).
  * **University District (1,180 orders):** High dinner volume (424 orders) and platform-leading late-night demand (114 orders between 10:00 PM and 4:00 AM).
* *Suburbs and Northside* represent dispersed, lower-density demand requiring wider delivery radiuses.

---

## 6. Actionable Business Recommendations

1. **Dynamic Weather & Traffic ETA Buffering:**
   * **Finding:** Ridge regression confirms that heavy rain adds +7.0 minutes and severe traffic adds +15.5 minutes to total transit duration.
   * **Action:** Automatically expand customer-facing ETA delivery windows by these dynamic offsets during rainstorms to eliminate delivery delay friction and cold-food churn.

2. **Prep-Synchronized Courier Dispatch:**
   * **Finding:** Kitchen preparation time is the second largest delay factor (17.7% relative importance).
   * **Action:** Delay driver dispatch until an order's estimated prep time is 75% complete to eliminate 8–10 minutes of courier curbside idle time outside busy merchants, directly increasing fleet utilization.

3. **Concentrated Courier Staging (Downtown, West End, University District):**
   * **Finding:** 75.6% of total platform demand is clustered in three dense urban zones.
   * **Action:** Pre-stage 65% of active fleet capacity within a 2.5 km radius of Downtown and West End merchant clusters 30 minutes prior to lunch (11:30 AM) and dinner (5:30 PM) peaks. Reposition late-night couriers toward University District after 10:00 PM.

4. **Targeted "Uber One" Conversion for Steady Regulars:**
   * **Finding:** Cluster 2 ("Steady Regulars") comprises 46% of the customer base with steady spend ($372.57) but an extended 15-day re-order gap.
   * **Action:** Deploy targeted in-app promotions offering 30-day complimentary Uber One memberships to compress their order cadence into weekly dining.

5. **Merchant Kitchen Quality Intervention Plan:**
   * **Finding:** 24 out of 50 merchant partners exceed operational tolerance thresholds, with cancellation rates reaching 8.0% and missing items driving 31.2% of negative customer reviews.
   * **Action:** Place merchant partners with cancellation rates > 6% on a 14-day operational review. Implement a mandatory two-step item checklist on the merchant tablet requiring staff to confirm drinks, sauces, and side items prior to courier handoff.

---

## 7. Model Limitations

1. **Synthetic Data Homogeneity:**
   * The underlying data was generated via controlled parametric distributions. Real-world marketplace logistics contain unmodeled complexities: multi-floor apartment drop-offs, parking search latencies, GPS drift, road construction closures, and payment gateway timeouts.

2. **Cold-Start Problem for New Users and Merchants:**
   * K-Means clustering requires behavioral features (`order_frequency_days`, `total_spending`). New customers with fewer than 3 transactions cannot be reliably segmented into behavioral tiers.

3. **Static Lexicon Representation in Sentiment Modeling:**
   * TF-IDF vectorization coupled with Linear SVM evaluates word frequencies without deep semantic context. It cannot reliably detect subtle sarcasm (e.g., *"Thanks for taking two hours to deliver ice-cold pizza, brilliant service"* will score positive keywords like *"thanks"* and *"brilliant"*).

4. **Univariate Time-Series Forecasting Constraints:**
   * Baseline ARIMA and Prophet configurations forecast order counts strictly from historical timestamps. They do not account for external dynamic shocks such as sudden rainstorms, public transit strikes, or local sports events.

5. **Static Upfront Tipping Paradigm:**
   * The regression model reflects historical platform behavior where tips are selected at checkout (r = 0.634 with basket size). It does not capture post-delivery tip adjustments driven by exceptional or poor courier service.

---

## 8. Future Improvement Opportunities

1. **Contextual NLP with Transformer Models (DistilBERT):**
   * Replace TF-IDF + Linear SVM with a fine-tuned DistilBERT model to capture bidirectional semantic relationships, negation structures, and sarcasm in customer reviews without manual stop-word maintenance.

2. **Exogenous Spatio-Temporal Forecasting (SARIMAX & Prophet External Regressors):**
   * Incorporate external real-time data feeds—including live weather radar, local stadium schedules, and holiday calendars—directly into forecasting models to anticipate non-cyclical demand surges.

3. **Graph Neural Networks (GNNs) for Turn-by-Turn ETA Routing:**
   * Transition from linear Euclidean distance approximations to Graph Neural Networks trained on road network topologies to capture one-way streets, bridge bottlenecks, and live intersection traffic lights.

4. **Survival Analysis for Customer Churn Modeling:**
   * Implement Cox Proportional Hazards or Kaplan-Meier estimators to compute dynamic churn risk scores based on elapsed days since last order, triggering automated retention discounts before churn occurs.

5. **Production MLOps, Drift Detection & Automated Retraining (MLflow / CI/CD):**
   * Deploy automated pipeline monitoring using MLflow to track model performance drift. Configure automated alerts and retraining triggers whenever delivery prediction errors exceed MAE > 3.5 minutes.