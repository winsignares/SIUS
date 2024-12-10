// ----------------------------- Dashboard Base -----------------------------
document.addEventListener('DOMContentLoaded', () => {
    const sidePanel = document.getElementById('sidePanel');
    const mainContainer = document.querySelector('.main-container');
    const toggleButton = document.getElementById('toggleSidePanel');

    toggleButton.addEventListener('click', () => {
        sidePanel.classList.toggle('collapsed');
        mainContainer.classList.toggle('collapsed');
    });
});