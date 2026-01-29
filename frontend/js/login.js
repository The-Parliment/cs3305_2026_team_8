// login.js: Handles login form logic and session token

const handleLogin = (e) => {
    e.preventDefault();
    const loginForm = e.target;
    const messageDiv = document.getElementById('message');
    fetch('/auth/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: loginForm.username.value,
            password: loginForm.password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success && data.token) {
            localStorage.setItem('jwt_token', data.token);
            messageDiv.innerText = data.message + '\nRedirecting to profile...';
            setTimeout(() => {
                window.location.href = 'profile.html';
            }, 1200);
        } else {
            messageDiv.innerText = data.message || 'Login failed.';
        }
    })
    .catch(err => messageDiv.innerText = 'Login error: ' + err);
};

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
});
