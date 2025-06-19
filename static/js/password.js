document.addEventListener('DOMContentLoaded', function() {
    function validatePasswords() {
        var password = document.getElementById("password").value.trim();
        var confirmPassword = document.getElementById("password_confirm").value.trim();

        if (password !== confirmPassword) {
            alert("Passwords do not match.");
            return false;
        }

        return true;
    }
});
