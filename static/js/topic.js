function toggleTopicDetails(topicId) {
    var details = document.getElementById('details-' + topicId);
    if (details.style.display === 'none' || !details.style.display) {
        details.style.display = 'block';  
    } else {
        details.style.display = 'none';  
    }
}

function showForm(topicId) {
    var form = document.getElementById('form-' + topicId);
    form.style.display = 'block';
}

function submitClaim(topicId) {
    var claimText = document.getElementById('claim-text-' + topicId).value;
    if (claimText.trim() === '') {
        alert('Please enter a claim text.');
        return;
    }
    fetch('/create-claim', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `topic=${topicId}&text=${encodeURIComponent(claimText)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Claim created successfully!');
            var claimsDiv = document.getElementById('claims-' + topicId);
            var newClaim = document.createElement('p');
            newClaim.textContent = claimText; 
            claimsDiv.appendChild(newClaim);
            document.getElementById('claim-text-' + topicId).value = ''; 
        } else {
            alert('Failed to create claim: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}

function loadClaims(topicId) {
    fetch(`/get-claims/${topicId}`)
    .then(response => response.json())
    .then(data => {
        const claimsDiv = document.getElementById('claims-' + topicId);
        claimsDiv.innerHTML = '';  
        data.forEach(claim => {
            const claimElement = document.createElement('div');
            claimElement.innerHTML = `<strong>${claim.userName}</strong>: ${claim.text} <small>${claim.creationTime}</small>`;
            claimsDiv.appendChild(claimElement);
        });
    });
}

function submitClaim(topicId) {
    var claimText = document.getElementById('claim-text-' + topicId).value.trim();
    if (claimText === '') {
        alert('Please enter a claim text.');
        return;
    }

    fetch('/create-claim', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `topic=${topicId}&text=${encodeURIComponent(claimText)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const claimsDiv = document.getElementById('claims-' + topicId);
            const newClaim = document.createElement('div');
            newClaim.classList.add('claim');
            newClaim.innerHTML = `<strong>${data.claimText}</strong> - <small>Just now</small>`;
            newClaim.onclick = () => displayReplyForm(data.claimId);  
            claimsDiv.insertBefore(newClaim, claimsDiv.firstChild);  
            document.getElementById('claim-text-' + topicId).value = ''; 
        } else {
            alert('Failed to create claim: ' + data.message);
        }
    })
    .catch(error => console.error('Error:', error));
}



function displayReplyForm(claimId) {
    var formId = 'reply-form-' + claimId;
    var replyForm = document.getElementById(formId);

    
    if (replyForm) {
        replyForm.style.display = replyForm.style.display === 'block' ? 'none' : 'block';
    } else {
        
        replyForm = document.createElement('div');
        replyForm.id = formId;
        replyForm.innerHTML = `
            <input type="text" placeholder="Enter your reply" id="reply-text-${claimId}">
            <button onclick="submitReply(${claimId})">Submit Reply</button>
        `;
        const claimElement = document.getElementById('claim-' + claimId);
        claimElement.appendChild(replyForm);
        replyForm.style.display = 'block';  
    }
}

function submitReply(claimId) {
    var replyText = document.getElementById('reply-text-' + claimId).value.trim();
    if (replyText === '') {
        alert('Please enter a reply text.');
        return;
    }

    fetch('/add-reply', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `claimId=${encodeURIComponent(claimId)}&text=${encodeURIComponent(replyText)}`
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok.');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Reply added successfully!');
            
        } else {
            alert('Failed to add reply: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting reply. See console for details.');
    });
}

function submitReplyToReply(replyId) {
    const replyTextElement = document.getElementById(`reply-text-${replyId}`);
    const replyText = replyTextElement.value.trim();
    if (replyText === '') {
        alert('Please enter a reply text.');
        return;
    }

    fetch('/reply-to-reply', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `replyToReplyID=${encodeURIComponent(replyId)}&text=${encodeURIComponent(replyText)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Reply added successfully!');
            const newReplyMarkup = `
                <div class="reply" id="reply-${data.newReplyID}">
                    <div class="reply-text-wrapper">
                        <strong>${data.username}</strong>: ${replyText} <small>Just now</small>
                    </div>
                </div>`;
            
        
            const nestedRepliesContainer = document.getElementById(`replies-${replyId}`);
            nestedRepliesContainer.insertAdjacentHTML('beforeend', newReplyMarkup);
            replyTextElement.value = ''; 
        } else {
            alert(`Failed to add reply: ${data.message}`);
        }
    })
    .catch(error => {
        console.error('Error submitting reply:', error);
        alert('Error submitting reply. Please check console for more details.');
    });
}




function toggleReplyForm(replyId) {
    const replyForm = document.getElementById(`reply-form-${replyId}`);
    replyForm.style.display = (replyForm.style.display === 'none' || !replyForm.style.display) ? 'block' : 'none';
}






function toggleReplyForm(claimId) {
    var formId = 'reply-form-' + claimId;
    var replyForm = document.getElementById(formId);

    if (replyForm.style.display === 'block') {
        replyForm.style.display = 'none';
    } else {
        replyForm.style.display = 'block';
    }
}


function stopPropagation(event) {
    event.stopPropagation();
}

function submitReply(claimId) {
    var replyTextElement = document.getElementById('reply-text-' + claimId);
    var replyText = replyTextElement.value.trim();
    if (replyText === '') {
        alert('Please enter a reply text.');
        return;
    }

    fetch('/add-reply', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `claimId=${encodeURIComponent(claimId)}&text=${encodeURIComponent(replyText)}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            
            replyTextElement.value = '';
           
            var repliesContainer = document.getElementById('replies-' + claimId);
            var newReply = document.createElement('div');
            newReply.classList.add('reply');
            newReply.innerHTML = `<strong>${data.username}</strong>: ${replyText} <small>Just now</small>`;
            repliesContainer.appendChild(newReply);

            alert('Reply added successfully!');
        } else {
            alert('Failed to add reply: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting reply. Please check console for more details.');
    });
}


function stopPropagation(event) {
    event.stopPropagation();
}

function loadReplies(claimId) {
    fetch(`/get-replies/${claimId}`)
        .then(response => response.json())
        .then(data => {
            const repliesContainer = document.getElementById(`replies-${claimId}`);
            repliesContainer.innerHTML = ''; 
            data.forEach(reply => {
                const replyElement = document.createElement('div');
                replyElement.className = 'reply';
                replyElement.innerHTML = `<strong>${reply.userName}</strong>: ${reply.text} <small>${reply.creationTime}</small>`;
                repliesContainer.appendChild(replyElement);
            });
        })
        .catch(error => console.error('Failed to load replies:', error));
}



document.addEventListener('DOMContentLoaded', function() {
    const claimIds = [...document.querySelectorAll('.claim')].map(claim => claim.id.replace('claim-', ''));
    claimIds.forEach(claimId => loadRepliesForClaim(claimId));
});

document.addEventListener('DOMContentLoaded', function () {
    
    document.querySelectorAll('[data-topic-date]').forEach(element => {
        element.textContent += element.getAttribute('data-topic-date');
    });
});

function submitClaimToClaim(claimId) {
    var relationTypeSelect = document.getElementById('claim-rel-type-' + claimId);
    var relatedClaimIdInput = document.getElementById('linked-claim-id-' + claimId);
    var relationType = relationTypeSelect.value;
    var relatedClaimId = relatedClaimIdInput.value;

    if (!relationType || !relatedClaimId) {
        alert('Please select a relation type and enter a related claim ID.');
        return;
    }

    fetch('/create-claim-to-claim', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `firstClaimId=${encodeURIComponent(claimId)}&secondClaimId=${encodeURIComponent(relatedClaimId)}&relationType=${encodeURIComponent(relationType)}`
    })
    .then(response => {
        if (!response.ok) throw new Error('Network response was not ok.');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            alert('Claim relationship added successfully!');
        } else {
            alert('Failed to add claim relationship: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error submitting claim relationship. Please check console for more details.');
    });
}



document.addEventListener('DOMContentLoaded', function() {
    fetch('/get-claim-rel-types')
        .then(response => response.json())
        .then(types => {
            document.querySelectorAll('[id^="claim-rel-type-"]').forEach(select => {
                types.forEach(type => {
                    let option = document.createElement('option');
                    option.value = type.claimRelTypeID;
                    option.textContent = type.claimRelType;
                    select.appendChild(option);
                });
            });
        });
});

document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelectorAll('.reply').forEach(reply => {
        const replyId = reply.getAttribute('id').split('-')[1]; 
        loadNestedReplies(replyId);
    });
});

function loadNestedReplies(parentReplyId) {
    fetch(`/get-nested-replies/${parentReplyId}`)
        .then(response => response.json())
        .then(nestedReplies => {
            const repliesContainer = document.getElementById(`replies-${parentReplyId}`);
            nestedReplies.forEach(reply => {
                const replyElement = document.createElement('div');
                replyElement.className = 'nested-reply';
                replyElement.innerHTML = `<strong>${reply.userName}</strong>: ${reply.text} <small>${reply.formattedCreationTime}</small>`;
                repliesContainer.appendChild(replyElement);
            });
        })
        .catch(error => console.error('Error loading nested replies:', error));
}
