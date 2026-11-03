/**
 * Smart Campus Lost & Found Matcher - Interactive Frontend Script
 */

document.addEventListener("DOMContentLoaded", () => {
    initDismissableAlerts();
    initQuickStatusToggles();
});

function initDismissableAlerts() {
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(alert => {
        // Auto dismiss after 6 seconds
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s ease, transform 0.5s ease";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 500);
        }, 6000);
    });
}

function initQuickStatusToggles() {
    // Progressive enhancement: Allow inline status updates via fetch without hard reloads
    const statusForms = document.querySelectorAll(".inline-form");
    statusForms.forEach(form => {
        form.addEventListener("submit", async (e) => {
            // Optional progressive enhancement
        });
    });
}
