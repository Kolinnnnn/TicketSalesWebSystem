function periodicallyClearExpiredItems() {
    setInterval(() => {
        fetch(clearExpiredItemsUrl, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'expired items cleared') {
                console.log("Expired items cleared from cart");
            }
        })
        .catch(error => console.error("Error clearing expired items:", error));
    }, 5 * 60 * 1000);
}

document.addEventListener("DOMContentLoaded", periodicallyClearExpiredItems);

document.addEventListener("DOMContentLoaded", function() {
    const alerts = document.querySelectorAll(".fixed-alerts-container .alert");
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add("fade-out");
        }, 5000);

        alert.addEventListener("transitionend", function() {
            if (alert.classList.contains("fade-out")) {
                alert.remove();
            }
        });
    });
});