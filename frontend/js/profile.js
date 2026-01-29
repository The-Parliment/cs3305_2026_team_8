// profile.js: Handles fetching user details using JWT token

const handleGetDetails = () => {
    const messageDiv = document.getElementById('message');
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        messageDiv.innerText = 'No token found. Please login first.';
        return;
    }
    fetch('/auth/me', {
        method: 'GET',
        headers: { 'token': token }
    })
    .then(res => res.json())
    .then(data => {
        if (data.username) {
            messageDiv.innerText = `User Details:\nUsername: ${data.username}\nFirst Name: ${data.first_name}\nLast Name: ${data.last_name}\nEmail: ${data.email}\nPhone: ${data.phone}`;
        } else {
            messageDiv.innerText = 'Failed to fetch user details.';
        }
    })
    .catch(err => messageDiv.innerText = 'Fetch details error: ' + err);
};

document.addEventListener('DOMContentLoaded', () => {
    const getDetailsBtn = document.getElementById('get-details-btn');
    if (getDetailsBtn) {
        getDetailsBtn.addEventListener('click', handleGetDetails);
    }
});
