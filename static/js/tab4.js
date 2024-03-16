import * as data from "./data.js";

var mobile =
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
    );

var updatingData = false;

document.addEventListener("DOMContentLoaded", function () {
    updateData();
    setInterval(updateData, 60 * 1000);
    //setInterval(updateVisibilities, 500);
    console.info("Initialized interval loops");
});

window.updateData = updateData;

var chartData = [
    {
        id: "month-temp",
        lastChartObj: null,
        callables: [
            {
                call: data.getTemperature,
                args: ["month"],
                label: "Temperatur",
                color: [50, 168, 162],
            }
        ],
        type: "line",
        hoursBetween: 24,
    },

    {
        id: "month-rain",
        lastChartObj: null,
        callables: [
            {
                call: data.getRain,
                args: ["month"],
                label: "Regenmenge",
                color: [29, 73, 173],
            }
        ],
        type: "line",
        hoursBetween: 24,
    },

    {
        id: "month-hum",
        lastChartObj: null,
        callables: [
            {
                call: data.getHumidity,
                args: ["month"],
                label: "Luftfeuchtigkeit",
                color: [103, 181, 25],
            }
        ],
        type: "line",
        hoursBetween: 24,
    },

    {
        id: "month-pre",
        lastChartObj: null,
        callables: [
            {
                call: data.getPressure,
                args: ["month"],
                label: "Luftdruck",
                color: [217, 172, 37],
            }
        ],
        type: "line",
        hoursBetween: 24,
    }
];


async function updateData() {
    updatingData = true;
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
    });
    updatingData = false;
}

const e = document.getElementById("info_last_updated");
const CRITICAL_LAST_UPDATE_THRESHOLD = 60 * 60; // 1 hour
if (
    (window.data_update_time + CRITICAL_LAST_UPDATE_THRESHOLD) * 1000 <
    Date.now()
) {
    const date = new Date(window.data_update_time * 1000);
    e.innerText = `Die Daten wurden zuletzt am ${date.toLocaleDateString()} um ${date.toLocaleTimeString()} aktualisiert. Hier angezeigte Daten können veraltet sein.`;
}
