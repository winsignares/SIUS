// Manejo de la navegación entre vistas
const loginView = document.getElementById('loginView');
const resetPasswordView = document.getElementById('resetPasswordView');
const forgotPasswordLink = document.getElementById('forgotPasswordLink');
const backToLoginLink = document.getElementById('backToLoginLink');

// Función para cambiar entre vistas con animación
function switchView(hideView, showView) {
    hideView.classList.add('fade-out');
    hideView.addEventListener('animationend', () => {
        hideView.classList.add('d-none');
        hideView.classList.remove('fade-out');
        showView.classList.remove('d-none');
        showView.classList.add('fade-in');
        showView.addEventListener('animationend', () => {
            showView.classList.remove('fade-in');
        }, { once: true });
    }, { once: true });
}

forgotPasswordLink.addEventListener('click', (e) => {
    e.preventDefault();
    switchView(loginView, resetPasswordView);
});

backToLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    switchView(resetPasswordView, loginView);
});