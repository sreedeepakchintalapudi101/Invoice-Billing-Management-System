// register.js
document.getElementById('register-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;
    const userType = document.getElementById('user-type').value;

    // Password validation
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[\W_]).{8,}$/;
    if (!passwordRegex.test(password)) {
        alert("Password is too weak! It must contain at least one uppercase letter, one lowercase letter, and one special character.");
        return;
    }

    if (password !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    // Send the registration data to the backend
    const userData = {
        email: email,
        username: username,
        password: password,
        confirm_password: confirmPassword,
        user_type: userType
    };

    fetch('http://localhost:8081/register_user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.flag) {
            alert(data.message);
            window.location.href = 'login.html';  // Redirect to login page after successful registration
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Something went wrong!');
    });
});
