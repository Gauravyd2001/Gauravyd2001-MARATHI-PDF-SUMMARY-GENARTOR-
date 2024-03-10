document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const messageContainer = document.getElementById('message-container');

    uploadForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        fetch('/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            if (data.message)  {
                // Display error message
                messageContainer.innerHTML = '<div class="alert error">+ data.message +</div>';
            } else {
                // If no error, proceed as before
                messageContainer.innerHTML = '';
                document.body.innerHTML = data;
                // Create home button
                const homeButton = document.createElement('button');
                homeButton.innerText = 'Home';
                homeButton.addEventListener('click', function() {
                    window.location.href = '/'; // Redirect to index.html
                });
                document.body.appendChild(homeButton);
            }
        })
        .catch(error => console.error('Error:', error));
    });
});
