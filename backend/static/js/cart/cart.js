function startTimer(expirationTime, elementId) {
    const countDownDate = new Date(expirationTime).getTime();

    const timer = setInterval(function () {
        const now = new Date().getTime();
        const distance = countDownDate - now;

        if (distance > 0) {
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            const timerElement = document.getElementById(elementId);
            if (timerElement) {
                timerElement.innerHTML = `Time left: ${minutes}m ${seconds}s`;
            }
        } else {
            clearInterval(timer);
            const timerElement = document.getElementById(elementId);
            if (timerElement) {
                timerElement.innerHTML = "<span class='expired'>Expired</span>";
            }
            location.reload();
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", function () {
    cartItemsData.forEach(item => {
        startTimer(item.expiration_time, `timer-${item.id}`);
    });
});
