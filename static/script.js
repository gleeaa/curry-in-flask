document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('video');
    const captureBtn = document.getElementById('capture');
    const resultDiv = document.getElementById('result');
    
    // Access webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(stream => video.srcObject = stream)
            .catch(err => resultDiv.textContent = `Error: ${err.message}`);
    }

    // Capture and analyze
    captureBtn.addEventListener('click', () => {
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0);
        
        // Simulate analysis (replace with actual API call)
        const thickness = Math.random() * 100;
        resultDiv.textContent = `Thickness: ${thickness.toFixed(2)}%`;
        
        // In real implementation, you would:
        // 1. Send canvas image to your backend API
        // 2. Receive and display real analysis
    });
});
