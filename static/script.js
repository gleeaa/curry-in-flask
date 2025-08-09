// Tab switching function
function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`.tab[onclick="switchTab('${tabName}')"]`).classList.add('active');
    document.getElementById(`${tabName}Tab`).classList.add('active');
}

// Test connection
function testConnection() {
    document.getElementById('result').textContent = "System connected!";
    console.log("Connection test successful");
}

// Main application
document.addEventListener('DOMContentLoaded', async () => {
    const video = document.getElementById('video');
    const canvas = document.getElementById('maskCanvas');
    const ctx = canvas.getContext('2d');
    const resultDiv = document.getElementById('result');
    const captureBtn = document.getElementById('capture');
    
    try {
        // Initialize camera
        const stream = await navigator.mediaDevices.getUserMedia({ 
            video: { width: 640, height: 480 } 
        });
        video.srcObject = stream;
        
        // Set canvas size to match video
        video.onloadedmetadata = () => {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            video.play();
        };
        
        // Analysis function
        captureBtn.addEventListener('click', () => {
            // Simulate analysis (replace with actual API call)
            const thickness = (Math.random() * 100).toFixed(2);
            resultDiv.textContent = `Thickness: ${thickness}%`;
            
            // Generate mock mask (yellow color detection)
            ctx.drawImage(video, 0, 0);
            const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            const data = imageData.data;
            
            for (let i = 0; i < data.length; i += 4) {
                // Simple yellow detection (for demo)
                if (data[i] > 150 && data[i+1] > 150 && data[i+2] < 100) {
                    // Keep yellow pixels
                } else {
                    // Make other pixels darker
                    data[i] *= 0.3;     // R
                    data[i+1] *= 0.3;   // G
                    data[i+2] *= 0.3;   // B
                }
            }
            
            ctx.putImageData(imageData, 0, 0);
            switchTab('mask');
        });
        
    } catch (err) {
        resultDiv.innerHTML = `ERROR: ${err.message}<br>
        Make sure you've allowed camera access`;
        console.error("Camera error:", err);
    }
});
