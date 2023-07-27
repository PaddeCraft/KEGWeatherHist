import * as data from "./data.js";

document.addEventListener("DOMContentLoaded", function () {
    updateData();
    setInterval(updateData, 60 * 1000);
    setInterval(saveToLocalStorage, 500);
});

var mobile = false;
if (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    )
) {
    mobile = true;
}

var chartData = [
    {
        id: "day",
        lastChartObj: null,
        lastChartCategoriesEnabled: null,
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
        defaultVisibility: [true, false, false, false, false],
        dateLabel: {
            hour: "2-digit",
            minute: "2-digit",
        },
    },
    {
        id: "week",
        lastChartObj: null,
        lastChartCategoriesEnabled: null,
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
        defaultVisibility: [true, false, false, false, false],
        dateLabel: {
            weekday: "long",
            year: "numeric",
            month: "short",
            day: "numeric",
        },
    },
    {
        id: "month",
        lastChartObj: null,
        lastChartCategoriesEnabled: null,
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
        defaultVisibility: [true, false, false, false, false],
        dateLabel: {
            weekday: "long",
            year: "numeric",
            month: "short",
            day: "numeric",
        },
    },
];

function saveToLocalStorage() {
    chartData.forEach(function (chart) {
        chart.lastChartCategoriesEnabled = [];
        for (var i = 0; i < chart.callables.length; i++) {
            if (chart.lastChartObj != null) {
                var meta = chart.lastChartObj.getDatasetMeta(i);
                chart.lastChartCategoriesEnabled.push(!meta.hidden);
            }
        }
        if (chart.lastChartCategoriesEnabled.length > 0) {
            localStorage.setItem(
                "chart_" + chart.id,
                JSON.stringify({ data: chart.lastChartCategoriesEnabled })
            );
        }
    });
}

async function updateData() {
    saveToLocalStorage();
    chartData.forEach(async function (chart) {
        // ==========================
        // ==== DELETE OLD CHART ====
        // ==========================
        if (chart.lastChartObj != null) {
            chart.lastChartObj.destroy();
        } else {
            if (localStorage.getItem("chart_" + chart.id) == null) {
                chart.lastChartCategoriesEnabled = chart.defaultVisibility;
            } else {
                chart.lastChartCategoriesEnabled = JSON.parse(
                    localStorage.getItem("chart_" + chart.id)
                ).data;
            }
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
            datasets.push({
                label: callable.label,
                data: await callable.call(...callable.args),
                backgroundColor: `rgba(${r}, ${g}, ${b}, 0.4)`,
                borderColor: `rgba(${r}, ${g}, ${b}, 1)`,
                borderWidth: 1,
            });
        }

        var now = new Date();
        for (var index = datasets[0].data.length; index > 0; index--) {
            labels.push(
                new Date(
                    now.getTime() - chart.hoursBetween * 3600000 * index
                ).toLocaleDateString("de-DE", chart.dateLabel)
            );
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
        if (chart.lastChartCategoriesEnabled != null) {
            for (var index = 0; index < chart.callables.length; index++) {
                var enabled = chart.lastChartCategoriesEnabled[index];
                chart.lastChartObj.setDatasetVisibility(index, enabled);
            }
            chart.lastChartObj.update();
        }
    });
    /* -------------------------------------------------------------------------- */
    /*                                  Live data                                 */
    /* -------------------------------------------------------------------------- */

    /* ----------------------------- Wind direction ----------------------------- */
    var windDirection = (await data.getWindDirection("current"))[0];
    var percentage = Math.round((windDirection / 360) * 100);
    document
        .getElementById("winddir-main")
        .style.setProperty("--value", percentage);
    document.querySelector("#winddir-text").innerText = windDirection;

    /* ------------------------------- Temperature ------------------------------ */
    document.getElementById("live_temp").innerText = (
        await data.getTemperature("current")
    )[0];

    /* ---------------------------------- Rain ---------------------------------- */
    document.getElementById("live_rain").innerText = (
        await data.getRain("current")
    )[0];

    /* -------------------------------- Pressure -------------------------------- */
    document.getElementById("live_pressure").innerText = (
        await data.getPressure("current")
    )[0];

    /* ---------------------------------- Wind ---------------------------------- */
    document.getElementById("live_windspeed").innerText = (
        await data.getWindSpeed("current")
    )[0];
}
