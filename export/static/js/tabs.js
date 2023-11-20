var tabElements = document.getElementsByClassName("tabsjs");
var tabElementCount = 1;
var classToggle = null;

Array.prototype.forEach.call(tabElements, function (e) {
    classToggle = e.dataset.classtoggle;
    if (classToggle == undefined) {
        classToggle = "";
    }
    var tabSelectors = e.getElementsByClassName("tabsjs-sel");
    var tabs = e.getElementsByClassName("tabsjs-tab");
    var tabDict = {};
    Array.prototype.forEach.call(tabs, function (tab) {
        tabDict[tab.dataset.tab] = tab;
        if (tab.dataset.tab != "0") {
            tab.style.display = "none";
        }
    });
    Array.prototype.forEach.call(tabSelectors, function (ts) {
        ts.dataset.cnt = tabElementCount;
        ts.classList.add("tabsjs-data-group-" + tabElementCount);
        ts.onclick = function () {
            selectTab(this.dataset.tab, tabDict);
        };
    });
    tabElementCount += 1;
});

function selectTab(nr, tabs) {
    history.replaceState(null, "", "./#" + nr);
    setTabSelectHighlight(parseInt(nr));

    for (var [, value] of Object.entries(tabs)) {
        value.style.display = "none";
    }
    tabs[nr].style.display = "block";
}

function setTabSelectHighlight(nr) {
    const el = document.querySelector(`.tabsjs-sel[data-tab="${nr}"]`);
    const thisGroupClass = "tabsjs-data-group-" + el.dataset.cnt;
    if (classToggle != "") {
        var thisGroup = document.getElementsByClassName(thisGroupClass);
        Array.prototype.forEach.call(thisGroup, function (e) {
            e.classList.remove(classToggle);
        });
        el.classList.add(classToggle);
    }
}

if (window.location.hash != "") {
    const tabs = [...document.querySelectorAll(".tabsjs-tab")];
    const tNr = window.location.hash.slice(1);
    if (!(isNaN(tNr) || tNr > tabs.length || tNr < 1)) selectTab(tNr, tabs);
}
