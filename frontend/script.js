// =========================================================
// GLOBAL VARIABLES
// =========================================================

let countryChart = null;
let productChart = null;
let yearChart = null;


// =========================================================
// GET FILTER VALUES
// =========================================================

function getFilters() {

    const country =
        document.getElementById(
            "countryFilter"
        ).value;


    const product =
        document.getElementById(
            "productFilter"
        ).value;


    return {
        country: country,
        product: product
    };

}


// =========================================================
// LOAD SUMMARY
// =========================================================

async function loadSummary() {

    try {

        const filters =
            getFilters();


        const url =
            "/summary?country=" +
            encodeURIComponent(
                filters.country
            ) +
            "&product_line=" +
            encodeURIComponent(
                filters.product
            );


        const response =
            await fetch(url);


        const data =
            await response.json();


        document.getElementById(
            "totalOrders"
        ).textContent =
            Number(
                data.total_orders
            ).toLocaleString();


        document.getElementById(
            "totalCustomers"
        ).textContent =
            Number(
                data.total_customers
            ).toLocaleString();


        document.getElementById(
            "totalSales"
        ).textContent =
            "$" +
            Number(
                data.total_sales
            ).toLocaleString();


        document.getElementById(
            "averageOrder"
        ).textContent =
            "$" +
            Number(
                data.average_order_value
            ).toLocaleString(
                undefined,
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            );


    } catch (error) {

        console.error(
            "Summary error:",
            error
        );

    }

}


// =========================================================
// LOAD COUNTRIES
// =========================================================

async function loadCountries() {

    try {

        const response =
            await fetch(
                "/countries"
            );


        const data =
            await response.json();


        const select =
            document.getElementById(
                "countryFilter"
            );


        data.countries.forEach(
            function (country) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    country;


                option.textContent =
                    country;


                select.appendChild(
                    option
                );

            }
        );


    } catch (error) {

        console.error(
            "Country error:",
            error
        );

    }

}


// =========================================================
// LOAD PRODUCT LINES
// =========================================================

async function loadProductLines() {

    try {

        const response =
            await fetch(
                "/product-lines"
            );


        const data =
            await response.json();


        const select =
            document.getElementById(
                "productFilter"
            );


        data.product_lines.forEach(
            function (product) {

                const option =
                    document.createElement(
                        "option"
                    );


                option.value =
                    product;


                option.textContent =
                    product;


                select.appendChild(
                    option
                );

            }
        );


    } catch (error) {

        console.error(
            "Product error:",
            error
        );

    }

}


// =========================================================
// LOAD SEGMENTS
// =========================================================

async function loadSegments() {

    try {

        const filters =
            getFilters();


        const url =
            "/segments?country=" +
            encodeURIComponent(
                filters.country
            ) +
            "&product_line=" +
            encodeURIComponent(
                filters.product
            );


        const response =
            await fetch(url);


        const data =
            await response.json();


        const cards =
            document.getElementById(
                "segmentCards"
            );


        const table =
            document.getElementById(
                "clusterTable"
            );


        cards.innerHTML = "";

        table.innerHTML = "";


        if (
            !data.segments ||
            data.segments.length === 0
        ) {

            cards.innerHTML =
                "<p>No segments found.</p>";

            return;

        }


        data.segments.forEach(
            function (segment) {

                // Create card
                const card =
                    document.createElement(
                        "div"
                    );


                card.className =
                    "segment-card";


                card.innerHTML = `

                    <h3>
                        Cluster ${segment.cluster}
                    </h3>

                    <div class="customers">
                        ${segment.customers}
                    </div>

                    <p>
                        Customers
                    </p>

                    <p>
                        Recency:
                        ${segment.average_recency}
                    </p>

                    <p>
                        Frequency:
                        ${segment.average_frequency}
                    </p>

                    <p>
                        Monetary:
                        $${Number(
                            segment.average_monetary
                        ).toLocaleString()}
                    </p>

                `;


                cards.appendChild(
                    card
                );


                // Create table row
                const row =
                    document.createElement(
                        "tr"
                    );


                row.innerHTML = `

                    <td>
                        Cluster ${segment.cluster}
                    </td>

                    <td>
                        ${segment.customers}
                    </td>

                    <td>
                        ${segment.average_recency}
                    </td>

                    <td>
                        ${segment.average_frequency}
                    </td>

                    <td>
                        $${Number(
                            segment.average_monetary
                        ).toLocaleString()}
                    </td>

                `;


                table.appendChild(
                    row
                );

            }
        );


    } catch (error) {

        console.error(
            "Segment error:",
            error
        );

    }

}


// =========================================================
// LOAD CHARTS
// =========================================================

async function loadCharts() {

    try {

        const filters =
            getFilters();


        const url =
            "/chart-data?country=" +
            encodeURIComponent(
                filters.country
            ) +
            "&product_line=" +
            encodeURIComponent(
                filters.product
            );


        const response =
            await fetch(url);


        const data =
            await response.json();


        // Destroy previous charts
        if (countryChart) {

            countryChart.destroy();

        }


        if (productChart) {

            productChart.destroy();

        }


        if (yearChart) {

            yearChart.destroy();

        }


        // -------------------------------------------------
        // COUNTRY CHART
        // -------------------------------------------------

        countryChart =
            new Chart(

                document.getElementById(
                    "countryChart"
                ),

                {

                    type: "bar",

                    data: {

                        labels:
                            data.country_names,

                        datasets: [

                            {

                                label:
                                    "Sales",

                                data:
                                    data.country_sales

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false

                    }

                }

            );


        // -------------------------------------------------
        // PRODUCT CHART
        // -------------------------------------------------

        productChart =
            new Chart(

                document.getElementById(
                    "productChart"
                ),

                {

                    type: "doughnut",

                    data: {

                        labels:
                            data.product_names,

                        datasets: [

                            {

                                label:
                                    "Sales",

                                data:
                                    data.product_sales

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false

                    }

                }

            );


        // -------------------------------------------------
        // YEAR CHART
        // -------------------------------------------------

        yearChart =
            new Chart(

                document.getElementById(
                    "yearChart"
                ),

                {

                    type: "line",

                    data: {

                        labels:
                            data.years,

                        datasets: [

                            {

                                label:
                                    "Sales",

                                data:
                                    data.year_sales,

                                tension:
                                    0.3

                            }

                        ]

                    },

                    options: {

                        responsive: true,

                        maintainAspectRatio: false

                    }

                }

            );


    } catch (error) {

        console.error(
            "Chart error:",
            error
        );

    }

}


// =========================================================
// APPLY FILTERS
// =========================================================

async function applyFilters() {

    // Update metrics
    await loadSummary();


    // Update segmentation
    await loadSegments();


    // Update charts
    await loadCharts();

}


// =========================================================
// SEARCH CUSTOMERS
// =========================================================

async function searchCustomers() {

    const search =
        document.getElementById(
            "customerSearch"
        ).value;


    const filters =
        getFilters();


    try {

        const url =
            "/customers?search=" +
            encodeURIComponent(
                search
            ) +
            "&country=" +
            encodeURIComponent(
                filters.country
            ) +
            "&product_line=" +
            encodeURIComponent(
                filters.product
            );


        const response =
            await fetch(url);


        const data =
            await response.json();


        const table =
            document.getElementById(
                "customerTable"
            );


        table.innerHTML = "";


        if (
            !data.customers ||
            data.customers.length === 0
        ) {

            table.innerHTML = `

                <tr>

                    <td colspan="5">
                        No customers found.
                    </td>

                </tr>

            `;

            return;

        }


        data.customers.forEach(
            function (customer) {

                const row =
                    document.createElement(
                        "tr"
                    );


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
                        $${Number(
                            customer.monetary
                        ).toLocaleString()}
                    </td>

                    <td>
                        Cluster
                        ${customer.cluster}
                    </td>

                `;


                table.appendChild(
                    row
                );

            }
        );


    } catch (error) {

        console.error(
            "Customer error:",
            error
        );

    }

}


// =========================================================
// PREDICT CLUSTER
// =========================================================

async function predictCluster() {

    const recency =
        Number(
            document.getElementById(
                "recency"
            ).value
        );


    const frequency =
        Number(
            document.getElementById(
                "frequency"
            ).value
        );


    const monetary =
        Number(
            document.getElementById(
                "monetary"
            ).value
        );


    // Validation
    if (
        isNaN(recency) ||
        isNaN(frequency) ||
        isNaN(monetary)
    ) {

        alert(
            "Please enter valid values."
        );

        return;

    }


    if (
        recency < 0 ||
        frequency <= 0 ||
        monetary < 0
    ) {

        alert(
            "Please enter valid positive values."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/predict",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            recency:
                                recency,

                            frequency:
                                frequency,

                            monetary:
                                monetary

                        })

                }
            );


        const data =
            await response.json();


        if (data.error) {

            alert(
                data.error
            );

            return;

        }


        document.getElementById(
            "predictionResult"
        ).style.display =
            "block";


        document.getElementById(
            "clusterResult"
        ).textContent =
            "Cluster " +
            data.predicted_cluster;


    } catch (error) {

        console.error(
            "Prediction error:",
            error
        );


        alert(
            "Could not connect to FastAPI."
        );

    }

}


// =========================================================
// INITIALIZE DASHBOARD
// =========================================================

async function initializeDashboard() {

    await loadCountries();

    await loadProductLines();

    await loadSummary();

    await loadSegments();

    await loadCharts();

    await searchCustomers();

}


// =========================================================
// START
// =========================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        initializeDashboard();

    }
);