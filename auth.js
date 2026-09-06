// Спільна логіка автентифікації для всіх сторінок сайту.
// Перевіряє, чи є збережений токен, і відповідно оновлює header:
// показує ім'я + "Вийти", якщо людина увійшла, або "Увійти"/"Реєстрація", якщо ні.

function getStoredUser() {
    const raw = localStorage.getItem('mist_user');
    if (!raw) return null;
    try {
        return JSON.parse(raw);
    } catch (e) {
        return null;
    }
}

function logout() {
    localStorage.removeItem('mist_token');
    localStorage.removeItem('mist_user');
    window.location.href = 'index.html';
}

function renderAuthHeader() {
    const authContainer = document.querySelector('.nav-auth');
    if (!authContainer) return;

    const user = getStoredUser();
    const token = localStorage.getItem('mist_token');

    if (user && token) {
        authContainer.innerHTML = `
            <span style="color: #cbd5e1; font-size: 0.9rem;">Привіт, ${user.name}</span>
            <a href="#" class="btn-outline" onclick="logout(); return false;">Вийти</a>
        `;
    } else {
        authContainer.innerHTML = `
            <a href="login.html" class="btn-outline">Увійти</a>
            <a href="register.html" class="btn">Реєстрація</a>
        `;
    }
}

document.addEventListener('DOMContentLoaded', renderAuthHeader);