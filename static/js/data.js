async function getWind(span) {
    return await (await fetch("/api/wind/" + span)).json();
}

// Exposed functions

export async function getTemperature(span) {
    return await (await fetch("/api/temperature/" + span)).json();
}
export async function getHumidity(span) {
    return await (await fetch("/api/humidity/" + span)).json();
}
export async function getPressure(span) {
    return await (await fetch("/api/pressure/" + span)).json();
}
export async function getRain(span) {
    return await (await fetch("/api/rain/" + span)).json();
}
export async function getWindSpeed(span) {
    return (await getWind(span)).map((x) => x.speed);
}
export async function getWindDirection(span) {
    return (await getWind(span)).map((x) => x.direction);
}
