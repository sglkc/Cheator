document.addEventListener('DOMContentLoaded', () => {
    const videoCanvas = document.getElementById('videoCanvas');
    const processedImage = document.getElementById('processedImage');
    const toggleButton = document.getElementById('toggleButton');
    const toggleIcon = document.getElementById('toggleIcon');
    const acceptButton = document.getElementById('acceptButton');
    const socket = new WebSocket('ws://' + window.location.host + '/ws/video_feed/');

    const canvasContext = videoCanvas.getContext('2d');
    let stream = null;
    let cameraActive = false;
    let proses = false;
    const studentName = document.getElementById('studentName').textContent; // Misalkan ada elemen dengan id studentName
    const className = document.getElementById('className').textContent; // Misalkan ada elemen dengan id className

    function startCamera() {
        navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } })
            .then((mediaStream) => {
                stream = mediaStream;
                videoCanvas.width = 640;
                videoCanvas.height = 480;

                const videoTrack = stream.getVideoTracks()[0];
                const video = document.createElement('video');
                video.srcObject = stream;
                video.play();

                video.addEventListener('loadedmetadata', () => {
                    function drawFrame() {
                        if (!cameraActive || proses) return;

                        canvasContext.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height);

                        videoCanvas.toBlob((blob) => {
                            const reader = new FileReader();
                            reader.onloadend = () => {
                                socket.send(reader.result);
                                proses = true;
                            };
                            reader.readAsArrayBuffer(blob);
                        }, 'image/jpeg', 0.3);
                    }
                    socket.send("online");
                    socket.send(studentName);
                    socket.send(className);

                    setInterval(drawFrame, 50);


                    socket.onmessage = (event) => {
                        proses = false;
                        const data = JSON.parse(event.data);
                        processedImage.src = data.image;
                        processedImage.style.display = 'block';

                        console.log("Status Kecurangan:", data.status);
                    };

                    cameraActive = true;
                    toggleButton.classList.add('active');
                    toggleIcon.textContent = 'videocam';
                });
            })
            .catch((err) => {
                console.error("Error accessing camera: ", err);
            });
    }

    function stopCamera() {
        if (stream) {
            let tracks = stream.getTracks();
            tracks.forEach(track => track.stop());
            stream = null;
            cameraActive = false;
            videoCanvas.style.display = 'none';
            processedImage.style.display = 'none';
            toggleButton.classList.remove('active');
            toggleIcon.textContent = 'videocam_off';
            setTimeout(() => {
                location.reload();
            }, 200);
        }
    }

    consentModal.style.display = 'block';

    acceptButton.addEventListener('click', () => {
        consentModal.style.display = 'none';
    });

    toggleButton.addEventListener('click', () => {
        if (cameraActive) {
            stopCamera();
        } else {
            startCamera();
        }
    });
});
