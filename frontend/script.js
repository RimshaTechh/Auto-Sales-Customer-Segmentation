// =========================================================
// API URL
// =========================================================


const API_URL = "https://auto-sales-customer-segmentation.up.railway.app";


// =========================================================
// CHART VARIABLES
// =========================================================

let countryChart = null;
let productChart = null;
let yearChart = null;


// =========================================================
// SAFE API REQUEST
// =========================================================

async function apiFetch(endpoint) {

    const response = await fetch(
        `${API_URL}${endpoint}`
    );

    const contentType =
        response.headers.get("content-type") || "";

    if (!response.ok) {

        const text = await response.text();

        throw new Error(
            `API error ${response.status} for ${endpoint}: ${text.substring(0, 200)}`
        );
    }

    if (!contentType.includes("application/json")) {

        const text = await response.text();

        throw new Error(
            `Expected JSON from ${endpoint}, but received: ${text.substring(0, 200)}`
        );
    }

    return await response.json();
}


// =========================================================
// LOAD COUNTRIES
// =========================================================

async function loadCountries() {

    const countries =
        await apiFetch("/countries");

    const select =
        document.getElementById("countryFilter");

    countries.forEach(country => {

        const option =
            document.createElement("option");

        option.value = country;
        option.textContent = country;

        select.appendChild(option);

    });
}


// =========================================================
// LOAD PRODUCT LINES
// =========================================================

async function loadProductLines() {

    const products =
        await apiFetch("/product-lines");

    const select =
        document.getElementById("productFilter");

    products.forEach(product => {

        const option =
            document.createElement("option");

        option.value = product;
        option.textContent = product;

        select.appendChild(option);

    });
}


// =========================================================
// GET FILTERS
// =========================================================

function getFilters() {

    const country =
        document.getElementById("countryFilter").value;

    const product =
        document.getElementById("productFilter").value;

    return {

        country: encodeURIComponent(country),

        product: encodeURIComponent(product)

    };
}


// =========================================================
// LOAD SUMMARY
// =========================================================

async function loadSummary() {

    const filters = getFilters();

    const data =
        await apiFetch(
            `/summary?country=${filters.country}&product_line=${filters.product}`
        );

    document.getElementById("totalOrders").textContent =
        Number(data.total_orders).toLocaleString();

    document.getElementById("totalCustomers").textContent =
        Number(data.total_customers).toLocaleString();

    document.getElementById("totalSales").textContent =
        Number(data.total_sales).toLocaleString();

    document.getElementById("averageSales").textContent =
        Number(data.average_sales).toLocaleString();
}


// =========================================================
// LOAD SEGMENTS
// =========================================================

async function loadSegments() {

    const filters = getFilters();

    const data =
        await apiFetch(
            `/segments?country=${filters.country}&product_line=${filters.product}`
        );

    const container =
        document.getElementById("segments");

    container.innerHTML = "";

    data.forEach(segment => {

        const card =
            document.createElement("div");

        card.className = "segment-card";

        card.innerHTML = `

            <h3>
                Cluster ${segment.cluster}
            </h3>

            <p>
                Customers:
                <strong>
                    ${segment.customers}
                </strong>
            </p>

            <p>
                Avg Recency:
                ${segment.average_recency}
            </p>

            <p>
                Avg Frequency:
                ${segment.average_frequency}
            </p>

            <p>
                Avg Monetary:
                ${segment.average_monetary}
            </p>

        `;

        container.appendChild(card);

    });
}


// =========================================================
// LOAD CHARTS
// =========================================================

async function loadCharts() {

    const filters = getFilters();

    const data =
        await apiFetch(
            `/chart-data?country=${filters.country}&product_line=${filters.product}`
        );


    // =====================================================
    // COUNTRY CHART
    // =====================================================

    const countryLabels =
        data.country_sales.map(
            item => item.name
        );

    const countryValues =
        data.country_sales.map(
            item => item.sales
        );

    if (countryChart) {

        countryChart.destroy();

    }

    countryChart = new Chart(

        document.getElementById("countryChart"),

        {

            type: "bar",

            data: {

                labels: countryLabels,

                datasets: [

                    {

                        label: "Sales",

                        data: countryValues

                    }

                ]

            },

            options: {

                responsive: true

            }

        }

    );


    // =====================================================
    // PRODUCT CHART
    // =====================================================

    const productLabels =
        data.product_sales.map(
            item => item.name
        );

    const productValues =
        data.product_sales.map(
            item => item.sales
        );

    if (productChart) {

        productChart.destroy();

    }

    productChart = new Chart(

        document.getElementById("productChart"),

        {

            type: "doughnut",

            data: {

                labels: productLabels,

                datasets: [

                    {

                        data: productValues

                    }

                ]

            },

            options: {

                responsive: true

            }

        }

    );


    // =====================================================
    // YEAR CHART
    // =====================================================

    const yearLabels =
        data.year_sales.map(
            item => item.year
        );

    const yearValues =
        data.year_sales.map(
            item => item.sales
        );

    if (yearChart) {

        yearChart.destroy();

    }

    yearChart = new Chart(

        document.getElementById("yearChart"),

        {

            type: "line",

            data: {

                labels: yearLabels,

                datasets: [

                    {

                        label: "Sales",

                        data: yearValues

                    }

                ]

            },

            options: {

                responsive: true

            }

        }

    );
}


// =========================================================
// APPLY FILTERS
// =========================================================

async function applyFilters() {

    try {

        await loadSummary();

        await loadSegments();

        await loadCharts();

        await searchCustomers();

    }

    catch (error) {

        console.error(
            "Filter loading error:",
            error
        );

    }
}


// =========================================================
// SEARCH CUSTOMERS
// =========================================================

async function searchCustomers() {

    const search =
        encodeURIComponent(
            document.getElementById("customerSearch").value
        );

    const filters = getFilters();

    const customers =
        await apiFetch(
            `/customers?search=${search}&country=${filters.country}&product_line=${filters.product}`
        );

    const table =
        document.getElementById("customerTable");

    table.innerHTML = "";

    customers.forEach(customer => {

        const row =
            document.createElement("tr");

        row.innerHTML = `

            <td>
                ${customer.customer}
            </td>

            <td>
                ${customer.recency}
            </td>

            <td>
                ${customer.frequency}
            </td>

            <td>
                ${customer.monetary}
            </td>

            <td>
                ${customer.cluster}
            </td>

        `;

        table.appendChild(row);

    });
}


// =========================================================
// PREDICT CLUSTER
// =========================================================

async function predictCluster() {

    const recency =
        Number(
            document.getElementById("recency").value
        );

    const frequency =
        Number(
            document.getElementById("frequency").value
        );

    const monetary =
        Number(
            document.getElementById("monetary").value
        );

    if (
        isNaN(recency) ||
        isNaN(frequency) ||
        isNaN(monetary)
    ) {

        document.getElementById(
            "predictionResult"
        ).textContent =
            "Please enter all values.";

        return;
    }

    try {

        const response =
            await fetch(
                `${API_URL}/predict`,
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body: JSON.stringify({

                        recency: recency,

                        frequency: frequency,

                        monetary: monetary

                    })

                }
            );

        const data =
            await response.json();

        if (!response.ok) {

            document.getElementById(
                "predictionResult"
            ).textContent =
                data.detail ||
                "Prediction failed.";

            return;
        }

        document.getElementById(
            "predictionResult"
        ).textContent =
            `Predicted Cluster: ${data.predicted_cluster}`;

    }

    catch (error) {

        console.error(
            "Prediction error:",
            error
        );

        document.getElementById(
            "predictionResult"
        ).textContent =
            "Prediction failed.";

    }
}


// =========================================================
// INITIALIZE DASHBOARD
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    async () => {

        try {

            await loadCountries();

            await loadProductLines();

            await loadSummary();

            await loadSegments();

            await loadCharts();

            await searchCustomers();

        }

        catch (error) {

            console.error(
                "Dashboard loading error:",
                error
            );

        }

    }
);
