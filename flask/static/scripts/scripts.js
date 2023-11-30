window.addEventListener('DOMContentLoaded', (event) => {
    function uploadAndSummarize() {
        var form = document.getElementById('uploadForm');
        var formData = new FormData(form);
        var loading = document.getElementById('loading');

        loading.style.display = 'block'; // Show loading indicator

        fetch('/summarize', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('summaryOutput').innerText = data.summary;
            loading.style.display = 'none'; // Hide loading indicator
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('summaryOutput').innerText = 'Error summarizing text.';
            loading.style.display = 'none'; // Hide loading indicator
        });
    }

    // Attach the uploadAndSummarize function to the button's onclick event
    function uploadAndSummarize() {
        var form = document.getElementById('uploadForm');
        var formData = new FormData(form);
        var loading = document.getElementById('loading');
    
        loading.style.display = 'block'; // Show loading indicator
    
        fetch('/summarize', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            document.getElementById('extractedText').innerText = data.extractedText; // Display extracted text
            document.getElementById('summaryOutput').innerText = data.summary;
            loading.style.display = 'none'; // Hide loading indicator
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('extractedText').innerText = '';
            document.getElementById('summaryOutput').innerText = 'Error summarizing text.';
            loading.style.display = 'none'; // Hide loading indicator
        });
    }
    var uploadButton = document.getElementById('uploadButton');
    if (uploadButton) {
        uploadButton.onclick = uploadAndSummarize;
    }
});
