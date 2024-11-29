// Manejo de la navegación entre vistas
const loginView = document.getElementById('loginView');
const resetPasswordView = document.getElementById('resetPasswordView');
const forgotPasswordLink = document.getElementById('forgotPasswordLink');
const backToLogin = document.getElementById('backToLogin');

forgotPasswordLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginView.classList.add('d-none');
    resetPasswordView.classList.remove('d-none');
});

backToLogin.addEventListener('click', () => {
    resetPasswordView.classList.add('d-none');
    loginView.classList.remove('d-none');
});