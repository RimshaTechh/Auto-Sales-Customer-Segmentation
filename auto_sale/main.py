from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

import pandas as pd
import numpy as np
import joblib
import os


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(
    title="Auto Sales Customer Segmentation API",
    description="RFM Customer Segmentation using KMeans",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

FRONTEND_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "frontend")
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "Auto Sales data.csv"
)

MODEL_FILE = os.path.join(
    BASE_DIR,
    "kmeans_model.pkl"
)

SCALER_FILE = os.path.join(
    BASE_DIR,
    "scaler.pkl"
)


# =========================================================
# LOAD DATA
# =========================================================

try:

    df = pd.read_csv(DATA_FILE)

    print("Dataset loaded successfully.")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))

except Exception as e:

    print("ERROR loading dataset:")
    print(e)

    df = pd.DataFrame()


# =========================================================
# LOAD KMEANS MODEL
# =========================================================

try:

    model = joblib.load(MODEL_FILE)

    print("KMeans model loaded successfully.")

except Exception as e:

    print("ERROR loading KMeans model:")
    print(e)

    model = None


# =========================================================
# LOAD SCALER
# =========================================================

try:

    scaler = joblib.load(SCALER_FILE)

    print("Scaler loaded successfully.")

except Exception as e:

    print("ERROR loading scaler:")
    print(e)

    scaler = None


# =========================================================
# PREDICTION INPUT
# =========================================================

class PredictionInput(BaseModel):

    recency: float
    frequency: float
    monetary: float


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message": "Auto Sales Customer Segmentation API is running",
        "dashboard": "/dashboard",
        "documentation": "/docs"
    }


# =========================================================
# DASHBOARD
# =========================================================

@app.get("/dashboard")
def dashboard():

    index_file = os.path.join(
        FRONTEND_DIR,
        "index.html"
    )

    if not os.path.exists(index_file):

        raise HTTPException(
            status_code=404,
            detail="index.html not found"
        )

    return FileResponse(index_file)


# =========================================================
# MODEL INFO
# =========================================================

@app.get("/model-info")
def model_info():

    return {
        "model_loaded": model is not None,
        "scaler_loaded": scaler is not None,
        "model_type": "KMeans",
        "clusters": (
            int(model.n_clusters)
            if model is not None
            and hasattr(model, "n_clusters")
            else None
        )
    }


# =========================================================
# COUNTRIES
# =========================================================

@app.get("/countries")
def countries():

    if df.empty:
        return []

    if "COUNTRY" not in df.columns:
        return []

    result = (
        df["COUNTRY"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    result.sort()

    return result


# =========================================================
# PRODUCT LINES
# =========================================================

@app.get("/product-lines")
def product_lines():

    if df.empty:
        return []

    if "PRODUCTLINE" not in df.columns:
        return []

    result = (
        df["PRODUCTLINE"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    result.sort()

    return result


# =========================================================
# FILTER DATA
# =========================================================

def filter_data(
    country="All",
    product_line="All"
):

    filtered = df.copy()

    if (
        country != "All"
        and "COUNTRY" in filtered.columns
    ):

        filtered = filtered[
            filtered["COUNTRY"].astype(str)
            == str(country)
        ]

    if (
        product_line != "All"
        and "PRODUCTLINE" in filtered.columns
    ):

        filtered = filtered[
            filtered["PRODUCTLINE"].astype(str)
            == str(product_line)
        ]

    return filtered


# =========================================================
# SUMMARY
# =========================================================

@app.get("/summary")
def summary(
    country: str = "All",
    product_line: str = "All"
):

    filtered = filter_data(
        country,
        product_line
    )

    if filtered.empty:

        return {
            "total_orders": 0,
            "total_customers": 0,
            "total_sales": 0,
            "average_sales": 0
        }

    total_orders = (
        filtered["ORDERNUMBER"].nunique()
        if "ORDERNUMBER" in filtered.columns
        else 0
    )

    total_customers = (
        filtered["CUSTOMERNAME"].nunique()
        if "CUSTOMERNAME" in filtered.columns
        else 0
    )

    total_sales = (
        filtered["SALES"].sum()
        if "SALES" in filtered.columns
        else 0
    )

    average_sales = (
        filtered["SALES"].mean()
        if "SALES" in filtered.columns
        else 0
    )

    return {

        "total_orders": int(
            total_orders
        ),

        "total_customers": int(
            total_customers
        ),

        "total_sales": round(
            float(total_sales),
            2
        ),

        "average_sales": round(
            float(average_sales),
            2
        )
    }


# =========================================================
# CREATE RFM
# =========================================================

def create_rfm(filtered):

    required = [
        "CUSTOMERNAME",
        "DAYS_SINCE_LASTORDER",
        "ORDERNUMBER",
        "SALES"
    ]

    for column in required:

        if column not in filtered.columns:
            return pd.DataFrame()

    rfm = (
        filtered
        .groupby("CUSTOMERNAME")
        .agg(

            Recency=(
                "DAYS_SINCE_LASTORDER",
                "min"
            ),

            Frequency=(
                "ORDERNUMBER",
                "nunique"
            ),

            Monetary=(
                "SALES",
                "sum"
            )
        )
        .reset_index()
    )

    rfm["Monetary_log"] = np.log1p(
        rfm["Monetary"]
    )

    return rfm


# =========================================================
# GET CLUSTER PREDICTIONS
# =========================================================

def add_clusters(rfm):

    if rfm.empty:

        return rfm

    if model is None or scaler is None:

        rfm["Cluster"] = 0

        return rfm

    features = rfm[
        [
            "Recency",
            "Frequency",
            "Monetary_log"
        ]
    ]

    try:

        scaled_features = scaler.transform(
            features
        )

        predictions = model.predict(
            scaled_features
        )

        rfm["Cluster"] = predictions

    except Exception as e:

        print(
            "Cluster prediction error:",
            e
        )

        rfm["Cluster"] = 0

    return rfm


# =========================================================
# CUSTOMER SEGMENTS
# =========================================================

@app.get("/segments")
def segments(
    country: str = "All",
    product_line: str = "All"
):

    filtered = filter_data(
        country,
        product_line
    )

    rfm = create_rfm(filtered)

    rfm = add_clusters(rfm)

    if rfm.empty:

        return []

    result = []

    for cluster in sorted(
        rfm["Cluster"].unique()
    ):

        cluster_data = rfm[
            rfm["Cluster"] == cluster
        ]

        result.append({

            "cluster": int(cluster),

            "customers": int(
                len(cluster_data)
            ),

            "average_recency": round(
                float(
                    cluster_data[
                        "Recency"
                    ].mean()
                ),
                2
            ),

            "average_frequency": round(
                float(
                    cluster_data[
                        "Frequency"
                    ].mean()
                ),
                2
            ),

            "average_monetary": round(
                float(
                    cluster_data[
                        "Monetary"
                    ].mean()
                ),
                2
            )
        })

    return result


# =========================================================
# CHART DATA
# =========================================================

@app.get("/chart-data")
def chart_data(
    country: str = "All",
    product_line: str = "All"
):

    filtered = filter_data(
        country,
        product_line
    )

    if filtered.empty:

        return {
            "country_sales": [],
            "product_sales": [],
            "year_sales": []
        }


    # -----------------------------------------------------
    # COUNTRY SALES
    # -----------------------------------------------------

    country_sales = []

    if (
        "COUNTRY" in filtered.columns
        and "SALES" in filtered.columns
    ):

        grouped = (
            filtered
            .groupby("COUNTRY")["SALES"]
            .sum()
            .sort_values(
                ascending=False
            )
            .head(10)
        )

        for name, value in grouped.items():

            country_sales.append({

                "name": str(name),

                "sales": round(
                    float(value),
                    2
                )
            })


    # -----------------------------------------------------
    # PRODUCT LINE SALES
    # -----------------------------------------------------

    product_sales = []

    if (
        "PRODUCTLINE" in filtered.columns
        and "SALES" in filtered.columns
    ):

        grouped = (
            filtered
            .groupby("PRODUCTLINE")["SALES"]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        for name, value in grouped.items():

            product_sales.append({

                "name": str(name),

                "sales": round(
                    float(value),
                    2
                )
            })


    # -----------------------------------------------------
    # YEAR SALES
    # -----------------------------------------------------

    year_sales = []

    if (
        "YEAR_ID" in filtered.columns
        and "SALES" in filtered.columns
    ):

        grouped = (
            filtered
            .groupby("YEAR_ID")["SALES"]
            .sum()
            .sort_index()
        )

        for year, value in grouped.items():

            year_sales.append({

                "year": str(year),

                "sales": round(
                    float(value),
                    2
                )
            })


    return {

        "country_sales":
            country_sales,

        "product_sales":
            product_sales,

        "year_sales":
            year_sales
    }


# =========================================================
# CUSTOMER SEARCH
# =========================================================

@app.get("/customers")
def customers(
    search: str = "",
    country: str = "All",
    product_line: str = "All"
):

    filtered = filter_data(
        country,
        product_line
    )

    rfm = create_rfm(filtered)

    rfm = add_clusters(rfm)

    if rfm.empty:

        return []


    if search:

        rfm = rfm[
            rfm["CUSTOMERNAME"]
            .astype(str)
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    rfm = rfm.head(50)

    result = []

    for _, row in rfm.iterrows():

        result.append({

            "customer": str(
                row["CUSTOMERNAME"]
            ),

            "recency": round(
                float(row["Recency"]),
                2
            ),

            "frequency": round(
                float(row["Frequency"]),
                2
            ),

            "monetary": round(
                float(row["Monetary"]),
                2
            ),

            "cluster": int(
                row["Cluster"]
            )
        })

    return result


# =========================================================
# PREDICT CUSTOMER CLUSTER
# =========================================================

@app.post("/predict")
def predict(
    data: PredictionInput
):

    if model is None:

        raise HTTPException(
            status_code=500,
            detail="KMeans model not loaded."
        )

    if scaler is None:

        raise HTTPException(
            status_code=500,
            detail="Scaler not loaded."
        )


    monetary_log = np.log1p(
        data.monetary
    )


    input_data = pd.DataFrame(

        [[
            data.recency,
            data.frequency,
            monetary_log
        ]],

        columns=[
            "Recency",
            "Frequency",
            "Monetary_log"
        ]
    )


    try:

        scaled_data = scaler.transform(
            input_data
        )

        prediction = model.predict(
            scaled_data
        )

        return {

            "predicted_cluster":
                int(prediction[0])

        }


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
