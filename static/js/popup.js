document.addEventListener('DOMContentLoaded', function() {
    // Login popup
    const loginButton = document.getElementById('login-popup');
    const loginPopup = document.getElementById('login-popup-content');

    // Signup popup
    const signupButton = document.getElementById('signup-popup');
    const signupPopup = document.getElementById('signup-popup-content');

    if (loginButton && loginPopup) {
        loginButton.addEventListener('click', function(e) {
            e.preventDefault();
            loginPopup.style.display = 'flex';
        });
    }

    if (signupButton && signupPopup) {
        signupButton.addEventListener('click', function(e) {
            e.preventDefault();
            signupPopup.style.display = 'flex';
        });
    }

    // Close popup when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target.classList.contains('popup-overlay')) {
            e.target.style.display = 'none';
        }
    });
});

// Function to close popup programmatically
function closePopup(popupId) {
    const popup = document.getElementById(popupId);
    if (popup) {
        popup.style.display = 'none';
    }
}
