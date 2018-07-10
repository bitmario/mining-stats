var reloading;
var refresh_time = 30000;

function checkReloading() {
    if (window.location.hash=="#autoreload") {
        reloading = setTimeout("window.location.reload();", refresh_time);
        document.getElementById("reloadCB").checked=true;
    }
}

function toggleAutoRefresh(cb) {
    if (cb.checked) {
        window.location.replace("#autoreload");
        reloading=setTimeout("window.location.reload();", refresh_time);
    } else {
        window.location.replace("#");
        clearTimeout(reloading);
    }
}

window.onload=checkReloading;