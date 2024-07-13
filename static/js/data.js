Array.from(document.getElementsByClassName("js_enabled")).forEach((el) => {
    el.style.display = "block";
});

let currentDataBuffer = null;

export async function getCurrent() {
    if (currentDataBuffer == null) {
        currentDataBuffer = await (await fetch("../api/all.json")).json();
    }
    return currentDataBuffer;
}
export async function resetCurrent() {
    currentDataBuffer = null;
}
export async function getTemperature(span) {
    return await (await fetch("../api/temperature/" + span + ".json")).json();
}
export async function getHumidity(span) {
    return await (await fetch("../api/humidity/" + span + ".json")).json();
}
export async function getPressure(span) {
    return await (await fetch("../api/pressure/" + span + ".json")).json();
}
export async function getRain(span) {
    return await (await fetch("../api/rain/" + span + ".json")).json();
}
export async function getWindSpeed(span) {
    return await (await fetch("../api/wind_speed/" + span + ".json")).json();
}
export async function getWindDirection(span) {
    return await (await fetch("../api/wind_direction/" + span + ".json")).json();
}
