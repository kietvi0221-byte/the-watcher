const messageElement =
    document.getElementById("message");

const deviceElement =
    document.getElementById("deviceName");

const connectionElement =
    document.getElementById("connection");

const lastEventElement =
    document.getElementById("lastEvent");


// ============================================================
// DEVICE
// ============================================================

function loadDevice() {

    let deviceName =
        localStorage.getItem(
            "watcher_device_name"
        );

    if (!deviceName) {

        deviceName =
            "PHONE-" +
            Math.floor(
                Math.random() * 9000 + 1000
            );

        localStorage.setItem(
            "watcher_device_name",
            deviceName
        );
    }

    deviceElement.textContent =
        deviceName;
}


// ============================================================
// MESSAGE
// ============================================================

function showMessage(text) {

    messageElement.style.opacity = "0";

    setTimeout(() => {

        messageElement.textContent =
            text;

        messageElement.style.opacity =
            "1";

    }, 250);

    lastEventElement.textContent =
        text;
}


// ============================================================
// CONNECTION
// ============================================================

function setConnected() {

    connectionElement.textContent =
        "● Connected";

    connectionElement.style.color =
        "#777777";
}

function setDisconnected() {

    connectionElement.textContent =
        "○ Disconnected";

    connectionElement.style.color =
        "#444444";
}


// ============================================================
// SERVER CONNECTION
// ============================================================

function connectWatcher() {

    /*
        V1 dùng polling đơn giản.

        Sau này server có thể chuyển sang
        WebSocket để nhận sự kiện realtime.
    */

    fetch("/api/mobile/status")
        .then(response => {

            if (!response.ok) {
                throw new Error(
                    "Server error"
                );
            }

            return response.json();
        })
        .then(data => {

            setConnected();

            if (data.message) {

                showMessage(
                    data.message
                );
            }

        })
        .catch(() => {

            setDisconnected();

        });
}


// ============================================================
// START
// ============================================================

loadDevice();

connectWatcher();

setInterval(
    connectWatcher,
    5000
);