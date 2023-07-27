var tabElements = document.getElementsByClassName("tabsjs");
var tabElementCount = 1;

Array.prototype.forEach.call(tabElements, function (e) {
    var classToggle = e.dataset.classtoggle;
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
            var thisGroupClass = "tabsjs-data-group-" + this.dataset.cnt;
            selectTab(this.dataset.tab, tabDict);
            if (classToggle != "") {
                var thisGroup = document.getElementsByClassName(thisGroupClass);
                Array.prototype.forEach.call(thisGroup, function (e) {
                    e.classList.remove(classToggle);
                });
                this.classList.add(classToggle);
            }
        };
    });
    tabElementCount += 1;
});

function selectTab(nr, tabs) {
    for (var [, value] of Object.entries(tabs)) {
        value.style.display = "none";
    }
    tabs[nr].style.display = "block";
}
