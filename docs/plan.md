# Player Churn Prediction — Project Plan & Implementation

> A complete hands‑on plan, instructions, and files to build a production-ready player churn prediction system for online casino operators (Adjarabet / Europebet style). This document is meant to be used as the central project artifact you can iterate on.

---

## 1. Project Summary

**Goal:** Predict which players are likely to stop playing soon (churn) so the casino can intervene with targeted retention actions.

**Scope:** From data collection and simulation → feature engineering → model training → threshold tuning → deployment (API) → monitoring and business integration.

**Deliverables:**

* Synthetic dataset generator (Python)
* Data schema & ETL checklist
* Baseline models (Logistic Regression, RandomForest) and a strong model (XGBoost / LightGBM) + ANN example
* Threshold tuning and campaign simulation (cost-benefit)
* FastAPI serving example + containerization instructions
* Monitoring & retraining plan, and governance checklist

---

## 2. Minimal Required Data (per player, time window = last 30 days unless otherwise noted)

> **Primary identifiers & labels**

* `player_id` (unique)
* `timestamp` (for events/aggregations)
* `churn_label` (0/1) — label computed by business rule: e.g. `days_since_last_login > 14` or `no bets in last 14 days`.

> **Behavioral features**

* `days_active_last_30` (0–30)
* `sessions_last_30` or `sessions_per_week`
* `avg_session_length` (minutes)
* `days_since_last_login`
* `total_bets` (count)
* `total_bet_amount` (sum currency)
* `avg_bet_size`
* `bets_per_session`
* `unique_games_played`
* `games_played_breakdown` (categorical or top-N games)

> **Monetary / Financial features**

* `total_deposit`, `total_withdrawal`
* `net_ggr` (gross gaming revenue) or `net_loss_win`
* `num_deposit_transactions`
* `avg_deposit_amount`
* `first_deposit_date` / `days_since_first_deposit`

> **Engagement / Social**

* `friends_count`
* `messages_sent`
* `tournaments_participated`
* `vip_level` or loyalty tier

> **Promotions & Offers**

* `bonus_used` (0/1), `bonus_amount_used`
* `num_offers_received_last_30`
* `num_offers_redeemed_last_30`

> **Device & Technical**

* `platform` (mobile/desktop)
* `os_family` (iOS/Android/Windows)
* `country` (geo)

> **Derived / Temporal features (very valuable)**

* `trend_session_count` (slope of sessions over last 4 weeks)
* `trend_deposit_amount`
* `time_between_sessions` statistics (mean, std)
* `recency_frequency_monetary` style RFM features

---

## 3. Optional / Helpful External Data

* Marketing touchpoints (email sent, push sent, campaign id)
* Customer support interactions (tickets, sentiment)
* Ad attribution / acquisition source
* Day-of-week / seasonality signals and big events (e.g., tournaments)

> **Privacy & Compliance note:** Always avoid storing highly sensitive PII unnecessarily. Keep geolocation aggregated (country/region) when possible and follow local gambling advertising and data protection laws (GDPR, local gambling regulators).

---

## 4. Synthetic Data Generator (what we will ship)

Files to produce:

* `data/generate_synthetic_players.py` — generates ~10k players with distributions mimicking real behavior.
* `data/README.md` — explains distributions and assumptions.

This generator will allow experiments and reproducibility before real data is available.

---

## 5. Modeling Plan & Baselines

**Baseline models:**

* Logistic Regression (with calibrated probabilities)
* Random Forest
* XGBoost / LightGBM (production candidate for tabular)
* Feed-forward ANN (Keras) — optional as an ensemble component

**Modeling steps:**

1. Split: train / val / test by time (temporal split) to avoid leakage. E.g., train on months 1–3, validate month 4, test month 5.
2. Imputation & scaling: numeric impute (median), rare categories grouped, one-hot or target encoding for high-card categorical features.
3. Feature importance & SHAP explainability for business visibility.
4. Calibrate probabilities (Platt scaling / isotonic) if needed.
5. Threshold optimization: optimize for recall at precision constraint or vice versa, or maximize expected profit using campaign cost model.

**Evaluation metrics:**

* Precision, Recall, F1
* ROC AUC and PR AUC (PR is better for imbalanced churn problems)
* Confusion matrix at candidate thresholds
* Business KPIs: retention lift, expected ROI per offer

---

## 6. Threshold & Campaign Simulation

Create a small cost model to decide threshold. Example inputs:

* `cost_per_contact` (e.g. 1.0 EUR for sending offer)
* `expected_value_saved_per_retained_player` (e.g. CLTV incremental)
* `offer_conversion_rate` (probability a contacted at-risk player is retained)

Simulate expected profit = (TP * value_saved * conversion) - (PredictedPositives * cost_per_contact) and choose threshold that maximizes profit.

---

## 7. Implementation Roadmap (sprints)

**Sprint 0 (1 week)**: Requirements, data access, synthetic dataset generator.
**Sprint 1 (2 weeks)**: Baseline models (LR / RF), metrics, feature importance.
**Sprint 2 (2 weeks)**: Strong model (XGBoost), calibration, threshold tuning with cost simulation.
**Sprint 3 (2 weeks)**: Explainability (SHAP), dashboard mockups, A/B test plan.
**Sprint 4 (2–3 weeks)**: Deploy model as FastAPI, containerize, connect to data pipeline.
**Sprint 5 (ongoing)**: Monitoring, retraining pipeline, reporting and handover.

---

## 8. Deployment & Serving

**Prototype stack**

* Model server: FastAPI
* Model serialization: `joblib` (sklearn) / `xgboost` native save / `onnx` for cross-platform
* Container: Dockerfile + CI pipeline
* Hosting: Railway / Render / AWS / GCP / Azure depending on infra

**API endpoints**

* `POST /predict` → returns `player_id`, `churn_prob`, `action_recommendation`
* `POST /batch-predict` → bulk predictions
* `GET /model-metrics` → recent performance stats

**Integration**

* Connect predictions to CRM to trigger campaigns via event stream (Kafka / PubSub) or scheduled batch export.

---

## 9. Monitoring & Retraining

Track:

* Data drift (feature distributions)
* Label drift (churn rate changes)
* Model performance (precision/recall) over time
* Prediction volume and latency

Automate retraining when performance drops below threshold or monthly schedule. Keep a fresh validation holdout.

---

## 10. Governance, Privacy, and Legal

* Document data lineage and retention policy.
* Mask or hash personal identifiers for storage.
* Ensure opt-in for marketing messages where required.
* Adhere to gambling advertising rules per jurisdiction (consult legal team).

---

## 11. Files to Create Immediately (repo layout)

```
player-churn-project/
├─ data/
│  ├─ generate_synthetic_players.py
│  └─ README.md
├─ notebooks/
│  ├─ 01_explore.ipynb
│  ├─ 02_model_baselines.ipynb
│  └─ 03_threshold_simulation.ipynb
├─ src/
│  ├─ features.py
│  ├─ train.py
│  ├─ predict.py
│  └─ utils.py
├─ api/
│  ├─ app.py  # FastAPI
│  └─ Dockerfile
├─ tests/
├─ requirements.txt
└─ README.md
```

---

## 12. Next actions (what I will create if you ask)

* A runnable `generate_synthetic_players.py` that produces a 10k-player dataset + README.
* A starter Jupyter notebook (`01_explore.ipynb`) showing EDA and baseline model training (RandomForest + metrics).
* A FastAPI minimal server `api/app.py` that serves `POST /predict`.

If you want me to start building these files now, tell me which file to create first and I'll generate it directly in the project canvas.

---

## 13. Notes on using real casino data (short)

* Use time-based splits to avoid leakage.
* Keep labeling rules explicit and versioned (how you define churn matters).
* Prioritize explainability: business teams must understand why a player was flagged.

---

*End of plan.*
