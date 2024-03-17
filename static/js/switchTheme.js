const switchThemeObj = document.getElementById("switchTheme");
const switchThemeInnerObj = document.getElementById("switchThemeInner");
switchThemeObj.onclick = function (event) {
    if (event.originalTarget.style.float == "right") {
        switchThemeInnerObj.style.float = "left";
        document.body.setAttribute("data-theme", "dark");
        switchThemeInnerObj.innerHTML = "&#x1F319;"; // Moon
    } else {
        switchThemeInnerObj.style.float = "right";
        document.body.setAttribute("data-theme", "light");
        switchThemeInnerObj.innerHTML = "&#x1F31E;"; //Sun
    }
};
if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    // dark mode
    switchThemeInnerObj.innerHTML = "&#x1F319;";
    switchThemeInnerObj.style.float = "left";
}