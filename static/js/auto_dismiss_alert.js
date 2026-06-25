document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(
        ".message, .alert, .profile-alert, .notification, .django-message, [data-auto-dismiss='true']"
    );

    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-8px)";

            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 10000);
    });
});