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

async function updateData() {
    updatingData = true;
    data.resetCurrent();
    console.info("Updating data");
    console.time("update_data");

    /* -------------------------------------------------------------------------- */
    /*                                  Live data                                 */
    /* -------------------------------------------------------------------------- */

    /* ----------------------------- Wind direction ----------------------------- */
    var windDirection = (await data.getCurrent()).wind.direction;
    var percentage = Math.round((windDirection / 360) * 100);
    document
        .getElementById("winddir-main")
        .style.setProperty("--value", percentage);
    document.querySelector("#winddir-text").innerText = windDirection;

    /* ------------------------------- Temperature ------------------------------ */
    document.getElementById("live_temp").innerText = (await data.getCurrent()).temperature;

    /* ---------------------------------- Rain ---------------------------------- */
    document.getElementById("live_rain").innerText = (await data.getCurrent()).rain;

    /* -------------------------------- Pressure -------------------------------- */
    document.getElementById("live_pressure").innerText = (await data.getCurrent()).pressure;

    /* ---------------------------------- Wind ---------------------------------- */
    document.getElementById("live_windspeed").innerText = (await data.getCurrent()).wind.speed;

    console.timeEnd("update_data");
    console.info("Finished updating data");

    updatingData = false;
    const uploadTimestamp = (await data.getCurrent()).timestamp;
    const e = document.getElementById("info_last_updated");
    const CRITICAL_LAST_UPDATE_THRESHOLD = 60 * 60; // 1 hour
    if (
        (uploadTimestamp + CRITICAL_LAST_UPDATE_THRESHOLD) * 1000 <
        Date.now()
    ) {
        const date = new Date(uploadTimestamp * 1000);
        e.innerText = `Die Daten wurden zuletzt am ${date.toLocaleDateString()} um ${date.toLocaleTimeString()} aktualisiert. Hier angezeigte Daten können veraltet sein.`;
    }
    

}
