document.addEventListener('DOMContentLoaded', function () {
    const loginPopup = document.getElementById('login-popup');
    const signupPopup = document.getElementById('signup-popup');
    const loginPopupContent = document.getElementById('login-popup-content');
    const signupPopupContent = document.getElementById('signup-popup-content');

    
    loginPopup.addEventListener('click', function () {
        if (loginPopupContent.style.display === 'block') {
            loginPopupContent.style.display = 'none';
        } else {
            loginPopupContent.style.display = 'block';
        }
    });

    
    signupPopup.addEventListener('click', function () {
        if (signupPopupContent.style.display === 'block') {
            signupPopupContent.style.display = 'none';
        } else {
            signupPopupContent.style.display = 'block';
        }
    });
});
