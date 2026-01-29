// register.js: Handles registration form logic

const handleRegister = (e) => {
    e.preventDefault();
    const registerForm = e.target;
    const messageDiv = document.getElementById('message');
    fetch('/auth/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            username: registerForm.username.value,
            first_name: registerForm.first_name.value,
            last_name: registerForm.last_name.value,
            email: registerForm.email.value,
            phone: registerForm.phone.value,
            password: registerForm.password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.username) {
            messageDiv.innerText = 'Registration successful! Redirecting to login...';
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1200);
        } else {
            messageDiv.innerText = data.message || 'Registration failed.';
        }
    })
    .catch(err => messageDiv.innerText = 'Register error: ' + err);
};

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('register-form');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
});
