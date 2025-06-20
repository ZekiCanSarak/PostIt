function submitForm(event, formId, errorMessageId, successCallback) {
    event.preventDefault(); 

    
    var formData = new FormData(document.getElementById(formId));

    
    fetch(event.target.action, {
        method: 'POST',
        body: formData,
        redirect: 'follow'
    })
    .then(response => {
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        return response.json();
    }) 
    .then(data => {
        if (data && !data.success) {
            document.getElementById(errorMessageId).textContent = data.message;
            document.getElementById(errorMessageId).style.display = 'block';
        }
    })
    .catch(error => console.error('Error:', error));
}


function handleSignupSuccess(data) {
   
    closePopup('signup-popup');
    
    location.reload();
}


document.addEventListener("DOMContentLoaded", function() {
    var loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(event) {
            submitForm(event, 'login-form', 'login-error-message', function() {
                window.location.href = '/';
            });
        });
    }

    var signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', function(event) {
            submitForm(event, 'signup-form', 'signup-error-message', function() {
                window.location.href = '/';
            });
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    var loginLink = document.getElementById('login-link');
    if (loginLink) {
        loginLink.addEventListener('click', function(event) {
            
        });
    }
});

function closePopup(popupId) {
    document.getElementById(popupId).style.display = 'none';
}

if (document.getElementById('signup-form')) {
    document.getElementById('signup-form').addEventListener('submit', function(event) {
        event.preventDefault();  
    
        var formData = new FormData(this);  
    
        fetch('/signup', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())  
        .then(data => {
            if (data.success) {
                window.location.href = '/';  
            } else {
                var errorMessageDiv = document.getElementById('signup-error-message');
                errorMessageDiv.textContent = data.message;  
                errorMessageDiv.style.display = 'block';  
            }
        })
        .catch(error => console.error('Error:', error));
    });
}


function replyToReply(replyId) {
    var formId = 'reply-form-' + replyId;
    var replyForm = document.getElementById(formId);

    
    if (replyForm.style.display === 'block') {
        replyForm.style.display = 'none';
    } else {
        replyForm.style.display = 'block';
    }
}