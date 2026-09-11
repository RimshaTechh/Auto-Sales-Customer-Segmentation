# Auto Sales Customer Segmentation

An end-to-end customer segmentation platform for automotive sales data, built with **RFM analysis** and **K-Means clustering**. The system exposes a FastAPI backend for data processing and predictions, paired with an interactive analytics dashboard for visualizing customer segments, sales trends, and cluster predictions.

**Live demo:**
- Frontend: [auto-sales-segmentation.up.railway.app](https://auto-sales-segmentation.up.railway.app)
- Backend API: [auto-sales-customer-segmentation.up.railway.app](https://auto-sales-customer-segmentation.up.railway.app)
- API Docs (Swagger): [/docs](https://auto-sales-customer-segmentation.up.railway.app/docs)

---

## Overview

This project analyzes automotive sales transactions to segment customers using **RFM (Recency, Frequency, Monetary)** metrics combined with a trained **K-Means clustering model**. Users can explore segment-level insights, filter by country and product line, look up individual customers, and predict which cluster a new customer profile would belong to.

---

## Features

- **Interactive Dashboard** — Real-time metrics, charts, and segment breakdowns
- **RFM Analysis** — Automatic computation of Recency, Frequency, and Monetary value per customer
- **Customer Segmentation** — Pre-trained K-Means model classifies customers into behavioral clusters
- **Dynamic Filtering** — Filter all views by country and product line
- **Sales Visualizations** — Sales by country, product line, and year (bar, doughnut, and line charts)
- **Customer Lookup** — Search and inspect individual customer RFM profiles and cluster assignment
- **Cluster Prediction** — Submit custom Recency/Frequency/Monetary values to predict a customer's segment
- **REST API** — Fully documented, interactive Swagger UI at `/docs`

---

## Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API framework
- [pandas](https://pandas.pydata.org/) / [NumPy](https://numpy.org/) — Data processing
- [scikit-learn](https://scikit-learn.org/) — K-Means clustering model (via `joblib`)
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

**Frontend**
- HTML5, CSS3 (Grid & Flexbox, responsive design)
- Vanilla JavaScript (Fetch API)
- [Chart.js](https://www.chartjs.org/) — Data visualization

**Deployment**
- [Railway](https://railway.com/) — Two independent services (backend API + static frontend)

---

## Project Structure

```
auto_sale_segmentation/
│
├── auto_sale/                     # Backend service
│   ├── main.py                    # FastAPI application & API routes
│   ├── requirements.txt           # Python dependencies
│   ├── kmeans_model.pkl           # Trained K-Means clustering model
│   ├── scaler.pkl                 # Fitted feature scaler
│   └── Auto Sales data.csv        # Source dataset
│
└── frontend/                      # Frontend service
    ├── index.html                 # Dashboard markup
    ├── style.css                  # Styling
    └── script.js                  # Dashboard logic & API integration
```

---

## API Reference

| Method | Endpoint         | Description                                      |
|--------|------------------|---------------------------------------------------|
| GET    | `/`              | Health check / API status                        |
| GET    | `/docs`          | Interactive Swagger documentation                 |
| GET    | `/model-info`    | Loaded model/scaler status and cluster count      |
| GET    | `/countries`     | List of available countries                       |
| GET    | `/product-lines` | List of available product lines                   |
| GET    | `/summary`       | Aggregate metrics (orders, customers, sales)       |
| GET    | `/segments`      | Cluster-level summary statistics                   |
| GET    | `/chart-data`    | Sales breakdown by country, product line, and year |
| GET    | `/customers`     | Searchable customer RFM table                      |
| POST   | `/predict`       | Predict cluster from Recency/Frequency/Monetary    |

All `GET` endpoints (except `/`, `/docs`, `/model-info`) accept optional query parameters:
- `country` (default: `"All"`)
- `product_line` (default: `"All"`)

**Example — Predict a customer's cluster:**
```bash
curl -X POST "https://auto-sales-customer-segmentation.up.railway.app/predict" \
  -H "Content-Type: application/json" \
  -d '{"recency": 45, "frequency": 6, "monetary": 12000}'
```

Response:
```json
{ "predicted_cluster": 2 }
```

---

## Dataset

The model is trained on historical automotive sales transaction data, including order details, customer information, product lines, and sales figures across multiple countries. Recency, Frequency, and Monetary values are computed per customer and used as input features for the K-Means clustering model.

---

