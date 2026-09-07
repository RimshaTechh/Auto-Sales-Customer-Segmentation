# =========================================================
# AUTO SALES - CUSTOMER SEGMENTATION
# FASTAPI BACKEND
# =========================================================

# ---------------------------------------------------------
# IMPORT LIBRARIES
# ---------------------------------------------------------

from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

import pandas as pd
import numpy as np
import joblib
import os


# ---------------------------------------------------------
# CREATE FASTAPI APP
# ---------------------------------------------------------

app = FastAPI(
    title="Auto Sales - Customer Segmentation API",
    description="RFM Analysis and KMeans Customer Segmentation",
    version="2.0.0"
)


# ---------------------------------------------------------
# BASE DIRECTORY
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# ---------------------------------------------------------
# FILE PATHS
# ---------------------------------------------------------

DATA_PATH = os.path.join(
    BASE_DIR,
    "Auto Sales data.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "kmeans_model.pkl"
)

SCALER_PATH = os.path.join(
    BASE_DIR,
    "scaler.pkl"
)


# ---------------------------------------------------------
# LOAD DATASET
# ---------------------------------------------------------

if not os.path.exists(DATA_PATH):

    raise FileNotFoundError(
        f"Dataset not found: {DATA_PATH}"
    )


df = pd.read_csv(DATA_PATH)

df = df.dropna(how="all")


# ---------------------------------------------------------
# LOAD TRAINED MODEL
# ---------------------------------------------------------

model = None

if os.path.exists(MODEL_PATH):

    model = joblib.load(
        MODEL_PATH
    )


# ---------------------------------------------------------
# LOAD SCALER
# ---------------------------------------------------------

scaler = None

if os.path.exists(SCALER_PATH):

    scaler = joblib.load(
        SCALER_PATH
    )


# ---------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------

STATIC_DIR = os.path.join(
    BASE_DIR,
    "static"
)


app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static"
)


# =========================================================
# FILTER DATA
# =========================================================

def filter_data(
    country="All",
    product_line="All"
):

    filtered = df.copy()


    # Country filter
    if (
        country != "All"
        and country != ""
    ):

        filtered = filtered[
            filtered["COUNTRY"]
            == country
        ]


    # Product line filter
    if (
        product_line != "All"
        and product_line != ""
    ):

        filtered = filtered[
            filtered["PRODUCTLINE"]
            == product_line
        ]


    return filtered


# =========================================================
# RFM CALCULATION
# =========================================================

def calculate_rfm(data):

    rfm = data.groupby(
        "CUSTOMERNAME"
    ).agg({

        "DAYS_SINCE_LASTORDER": "min",

        "ORDERNUMBER": "nunique",

        "SALES": "sum"

    }).reset_index()


    rfm.rename(
        columns={
            "DAYS_SINCE_LASTORDER": "Recency",
            "ORDERNUMBER": "Frequency",
            "SALES": "Monetary"
        },
        inplace=True
    )


    # Log transformation
    rfm["Monetary_log"] = np.log1p(
        rfm["Monetary"]
    )


    return rfm


# =========================================================
# DASHBOARD PAGE
# =========================================================

@app.get("/dashboard")
def dashboard():

    return FileResponse(
        os.path.join(
            BASE_DIR,
            "templates",
            "index.html"
        )
    )


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "message":
            "Auto Sales Customer Segmentation API is running",

        "dashboard":
            "/dashboard",

        "documentation":
            "/docs"
    }


# =========================================================
# MODEL INFORMATION
# =========================================================

@app.get("/model-info")
def model_info():

    return {

        "model_loaded":
            model is not None,

        "scaler_loaded":
            scaler is not None,

        "model_type":
            type(model).__name__
            if model is not None
            else None

    }


# =========================================================
# SUMMARY WITH FILTERS
# =========================================================

@app.get("/summary")
def summary(

    country: str = Query(
        default="All"
    ),

    product_line: str = Query(
        default="All"
    )

):

    # Get filtered data
    filtered = filter_data(
        country,
        product_line
    )


    # Total orders
    total_orders = filtered[
        "ORDERNUMBER"
    ].nunique()


    # Total customers
    total_customers = filtered[
        "CUSTOMERNAME"
    ].nunique()


    # Total sales
    total_sales = filtered[
        "SALES"
    ].sum()


    # Average sales
    average_order_value = filtered[
        "SALES"
    ].mean()


    return {

        "total_orders":
            int(total_orders),

        "total_customers":
            int(total_customers),

        "total_sales":
            round(
                float(total_sales),
                2
            ),

        "average_order_value":
            round(
                float(average_order_value),
                2
            )

    }


# =========================================================
# COUNTRIES
# =========================================================

@app.get("/countries")
def countries():

    country_list = sorted(
        df[
            "COUNTRY"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    return {
        "countries":
            country_list
    }


# =========================================================
# PRODUCT LINES
# =========================================================

@app.get("/product-lines")
def product_lines():

    product_list = sorted(
        df[
            "PRODUCTLINE"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    return {
        "product_lines":
            product_list
    }


# =========================================================
# SEGMENTS
# =========================================================

@app.get("/segments")
def segments(

    country: str = Query(
        default="All"
    ),

    product_line: str = Query(
        default="All"
    )

):

    # Filter data
    filtered_df = filter_data(
        country,
        product_line
    )


    # Calculate RFM
    rfm = calculate_rfm(
        filtered_df
    )


    # Predict clusters
    if (
        model is not None
        and scaler is not None
        and len(rfm) > 0
    ):

        features = rfm[
            [
                "Recency",
                "Frequency",
                "Monetary_log"
            ]
        ]


        scaled_features = scaler.transform(
            features
        )


        rfm["Cluster"] = model.predict(
            scaled_features
        )

    else:

        rfm["Cluster"] = 0


    # Cluster results
    result = []


    for cluster in sorted(
        rfm["Cluster"].unique()
    ):

        cluster_data = rfm[
            rfm["Cluster"] == cluster
        ]


        result.append({

            "cluster":
                int(cluster),

            "customers":
                int(
                    len(cluster_data)
                ),

            "average_recency":
                round(
                    float(
                        cluster_data[
                            "Recency"
                        ].mean()
                    ),
                    2
                ),

            "average_frequency":
                round(
                    float(
                        cluster_data[
                            "Frequency"
                        ].mean()
                    ),
                    2
                ),

            "average_monetary":
                round(
                    float(
                        cluster_data[
                            "Monetary"
                        ].mean()
                    ),
                    2
                )

        })


    return {

        "segments":
            result,

        "total_customers":
            int(len(rfm))

    }


# =========================================================
# CHART DATA
# =========================================================

@app.get("/chart-data")
def chart_data(

    country: str = Query(
        default="All"
    ),

    product_line: str = Query(
        default="All"
    )

):

    filtered_df = filter_data(
        country,
        product_line
    )


    # -----------------------------------------------------
    # SALES BY COUNTRY
    # -----------------------------------------------------

    country_sales = (
        filtered_df
        .groupby("COUNTRY")["SALES"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )


    # -----------------------------------------------------
    # SALES BY PRODUCT LINE
    # -----------------------------------------------------

    product_sales = (
        filtered_df
        .groupby("PRODUCTLINE")["SALES"]
        .sum()
        .sort_values(
            ascending=False
        )
    )


    # -----------------------------------------------------
    # SALES BY YEAR
    # -----------------------------------------------------

    if "YEAR_ID" in filtered_df.columns:

        yearly_sales = (
            filtered_df
            .groupby("YEAR_ID")["SALES"]
            .sum()
            .sort_index()
        )


        years = [
            str(x)
            for x in yearly_sales.index
        ]


        year_sales = [
            round(
                float(x),
                2
            )
            for x in yearly_sales.values
        ]

    else:

        years = []

        year_sales = []


    return {

        "country_names":
            country_sales.index.tolist(),

        "country_sales":
            [
                round(
                    float(x),
                    2
                )
                for x in country_sales.values
            ],

        "product_names":
            product_sales.index.tolist(),

        "product_sales":
            [
                round(
                    float(x),
                    2
                )
                for x in product_sales.values
            ],

        "years":
            years,

        "year_sales":
            year_sales

    }


# =========================================================
# CUSTOMER LOOKUP
# =========================================================

@app.get("/customers")
def customers(

    search: str = Query(
        default=""
    ),

    country: str = Query(
        default="All"
    ),

    product_line: str = Query(
        default="All"
    )

):

    # Filter data
    filtered_df = filter_data(
        country,
        product_line
    )


    # RFM
    rfm = calculate_rfm(
        filtered_df
    )


    # Cluster
    if (
        model is not None
        and scaler is not None
        and len(rfm) > 0
    ):

        features = rfm[
            [
                "Recency",
                "Frequency",
                "Monetary_log"
            ]
        ]


        scaled_features = scaler.transform(
            features
        )


        rfm["Cluster"] = model.predict(
            scaled_features
        )

    else:

        rfm["Cluster"] = 0


    # Search
    if search:

        rfm = rfm[
            rfm["CUSTOMERNAME"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        ]


    # Maximum 50 customers
    rfm = rfm.head(50)


    customers_list = []


    for _, row in rfm.iterrows():

        customers_list.append({

            "customer":
                row["CUSTOMERNAME"],

            "recency":
                round(
                    float(
                        row["Recency"]
                    ),
                    2
                ),

            "frequency":
                int(
                    row["Frequency"]
                ),

            "monetary":
                round(
                    float(
                        row["Monetary"]
                    ),
                    2
                ),

            "cluster":
                int(
                    row["Cluster"]
                )

        })


    return {
        "customers":
            customers_list
    }


# =========================================================
# CUSTOMER INPUT
# =========================================================

class CustomerInput(BaseModel):

    recency: float

    frequency: float

    monetary: float


# =========================================================
# PREDICT CUSTOMER CLUSTER
# =========================================================

@app.post("/predict")
def predict(
    customer: CustomerInput
):

    # Check model
    if model is None:

        return {
            "error":
                "KMeans model not found."
        }


    # Check scaler
    if scaler is None:

        return {
            "error":
                "Scaler not found."
        }


    # Log transform
    monetary_log = np.log1p(
        customer.monetary
    )


    # Create dataframe
    input_data = pd.DataFrame({

        "Recency": [
            customer.recency
        ],

        "Frequency": [
            customer.frequency
        ],

        "Monetary_log": [
            monetary_log
        ]

    })


    # Scale
    scaled_data = scaler.transform(
        input_data
    )


    # Prediction
    prediction = model.predict(
        scaled_data
    )


    predicted_cluster = int(
        prediction[0]
    )


    return {

        "predicted_cluster":
            predicted_cluster,

        "recency":
            customer.recency,

        "frequency":
            customer.frequency,

        "monetary":
            customer.monetary

    }
