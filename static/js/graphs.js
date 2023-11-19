import * as data from "./data.js";

var mobile =
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );

var defaultVisibility = [true, false, false, false, false];

var locStorageEnableData = localStorage.getItem("chart_enabled");
window.chartCategoriesEnabled = defaultVisibility;
if (locStorageEnableData) {
    chartCategoriesEnabled = JSON.parse(locStorageEnableData).data;
    console.info(
        "Loaded enabled categories from local storage",
        chartCategoriesEnabled
    );
}

var updatingData = false;

document.addEventListener("DOMContentLoaded", function () {
    updateData();
    setInterval(updateData, 60 * 1000);
    setInterval(updateVisibilities, 500);
    console.info("Initialized interval loops");
});

window.updateData = updateData;

var chartData = [
    {
        id: "day",
        lastChartObj: null,
        callables: [
            {
                call: data.getTemperature,
                args: ["day"],
                label: "Temperatur",
                color: [50, 168, 162],
            },
            {
                call: data.getWindSpeed,
                args: ["day"],
                label: "Windgeschwindigkeit",
                color: [194, 25, 152],
            },
            {
                call: data.getRain,
                args: ["day"],
                label: "Regenmenge",
                color: [29, 73, 173],
            },
            {
                call: data.getHumidity,
                args: ["day"],
                label: "Luftfeuchtigkeit",
                color: [103, 181, 25],
            },
            {
                call: data.getPressure,
                args: ["day"],
                label: "Luftdruck",
                color: [217, 172, 37],
            },
        ],
        type: "line",
        hoursBetween: 24,
    },
    {
        id: "week",
        lastChartObj: null,
        callables: [
            {
                call: data.getTemperature,
                args: ["week"],
                label: "Temperatur",
                color: [50, 168, 162],
            },
            {
                call: data.getWindSpeed,
                args: ["week"],
                label: "Windgeschwindigkeit",
                color: [194, 25, 152],
            },
            {
                call: data.getRain,
                args: ["week"],
                label: "Regenmenge",
                color: [29, 73, 173],
            },
            {
                call: data.getHumidity,
                args: ["week"],
                label: "Luftfeuchtigkeit",
                color: [103, 181, 25],
            },
            {
                call: data.getPressure,
                args: ["week"],
                label: "Luftdruck",
                color: [217, 172, 37],
            },
        ],
        type: "line",
        hoursBetween: 24,
    },
    {
        id: "month",
        lastChartObj: null,
        callables: [
            {
                call: data.getTemperature,
                args: ["month"],
                label: "Temperatur",
                color: [50, 168, 162],
            },
            {
                call: data.getWindSpeed,
                args: ["month"],
                label: "Windgeschwindigkeit",
                color: [194, 25, 152],
            },
            {
                call: data.getRain,
                args: ["month"],
                label: "Regenmenge",
                color: [29, 73, 173],
            },
            {
                call: data.getHumidity,
                args: ["month"],
                label: "Luftfeuchtigkeit",
                color: [103, 181, 25],
            },
            {
                call: data.getPressure,
                args: ["month"],
                label: "Luftdruck",
                color: [217, 172, 37],
            },
        ],
        type: "line",
        hoursBetween: 24,
    },
];

function updateVisibilities() {
    if (updatingData) return;

    var changed = false;

    for (var _i = 0; _i < chartData.length; _i++) {
        var chart = chartData[_i];
        var enabled = [];
        for (var i = 0; i < chart.callables.length; i++) {
            if (chart.lastChartObj != null) {
                var meta = chart.lastChartObj.getDatasetMeta(i);
                enabled.push(!meta.hidden);
                if (enabled[i] != chartCategoriesEnabled[i]) {
                    changed = true;
                }
            }
        }

        if (changed) {
            window.chartCategoriesEnabled = enabled;
            break;
        }
    }

    if (changed) {
        console.info("Detected change in category selection");
        localStorage.setItem(
            "chart_enabled",
            JSON.stringify({ data: chartCategoriesEnabled })
        );

        chartData.forEach(function (chart) {
            for (var i = 0; i < chart.callables.length; i++) {
                if (chart.lastChartObj != null) {
                    chart.lastChartObj.setDatasetVisibility(
                        i,
                        chartCategoriesEnabled[i]
                    );
                    chart.lastChartObj.update("active");
                } else {
                    console.warn(
                        "Chart for id " + chart.id + " has no last chart object"
                    );
                }
            }
        });
        console.info("Updated displayed categories");
    }
}

async function updateData() {
    updatingData = true;
    updateVisibilities();
    console.info("Updating data");
    console.time("update_data");

    chartData.forEach(async function (chart) {
        // ==========================
        // ==== DELETE OLD CHART ====
        // ==========================
        if (chart.lastChartObj != null) {
            chart.lastChartObj.destroy();
        }
        // =======================
        // ==== GENERATE DATA ====
        // =======================
        var canvas = document.getElementById(chart.id);
        var context = canvas.getContext("2d");
        var datasets = [];
        var labels = [];

        for (var index = 0; index < chart.callables.length; index++) {
            var callable = chart.callables[index];
            var [r, g, b] = callable.color;

            var callable_result = await callable.call(...callable.args);
            labels = callable_result.labels;

            datasets.push({
                label: callable.label,
                data: callable_result.entries,
                backgroundColor: `rgba(${r}, ${g}, ${b}, 0.4)`,
                borderColor: `rgba(${r}, ${g}, ${b}, 1)`,
                borderWidth: 1,
            });
        }

        /* -------------------------------------------------------------------------- */
        /*                                Create Charts                               */
        /* -------------------------------------------------------------------------- */
        chart.lastChartObj = new Chart(context, {
            type: chart.type,
            data: {
                // Labels are the index of the data +1
                labels: labels,
                datasets: datasets,
            },
            options: {
                animation: {
                    duration: 700,
                },
                aspectRatio: mobile ? 1 : 2,
                scales: {
                    yAxes: [
                        {
                            ticks: {
                                beginAtZero: true,
                            },
                        },
                    ],
                },
            },
        });

        /* -------------------------------------------------------------------------- */
        /*                         Restore selected categories                        */
        /* -------------------------------------------------------------------------- */
        if (chartCategoriesEnabled != null) {
            console.info(
                "Restoring selected categories",
                chartCategoriesEnabled
            );
            for (var index = 0; index < chart.callables.length; index++) {
                var enabled = chartCategoriesEnabled[index];
                chart.lastChartObj.setDatasetVisibility(index, enabled);
            }
            chart.lastChartObj.update();
        }
    });
    /* -------------------------------------------------------------------------- */
    /*                                  Live data                                 */
    /* -------------------------------------------------------------------------- */

    /* ----------------------------- Wind direction ----------------------------- */
    var windDirection = await data.getWindDirection("current");
    var percentage = Math.round((windDirection / 360) * 100);
    document
        .getElementById("winddir-main")
        .style.setProperty("--value", percentage);
    document.querySelector("#winddir-text").innerText = windDirection;

    /* ------------------------------- Temperature ------------------------------ */
    document.getElementById("live_temp").innerText = await data.getTemperature(
        "current"
    );

    /* ---------------------------------- Rain ---------------------------------- */
    document.getElementById("live_rain").innerText = await data.getRain(
        "current"
    );

    /* -------------------------------- Pressure -------------------------------- */
    document.getElementById("live_pressure").innerText = await data.getPressure(
        "current"
    );

    /* ---------------------------------- Wind ---------------------------------- */
    document.getElementById("live_windspeed").innerText =
        await data.getWindSpeed("current");

    console.timeEnd("update_data");
    console.info("Finished updating data");

    updatingData = false;
}
