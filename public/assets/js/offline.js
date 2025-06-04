const videoCanvas = document.getElementById('videoCanvas');
const processedImage = document.getElementById('processedImage');
const toggleButton = document.getElementById('toggleButton');
const toggleIcon = document.getElementById('toggleIcon');
const downloadButton = document.getElementById('downloadButton');

const canvasContext = videoCanvas.getContext('2d');
let stream = null;
let cameraActive = false;
let video = null;

// Cheating detection variables
let startTime = null;
let tengokKiriDetected = false;
const cheatingDuration = 0.75;
let cheatingStatus = "no cheating";

// Throttling for upload function
let lastUploadTime = 0;
const uploadThrottleDelay = 3000; // 3 seconds between uploads
let consecutiveCheatingDetections = 0;

// Frame rate control
const targetFPS = 30;
const frameInterval = 1000 / targetFPS; // ~33.33ms between frames
let lastFrameTime = 0;

// MediaPipe Face Mesh and Pose Detection
let faceMesh = null;
let pose = null;
let detectionResults = null;
let modelsLoaded = false;

// API function to upload cheating event
async function uploadCheatingEvent(studentName, imageFile) {
  try {
    // Create FormData to handle file upload
    const formData = new FormData();
    formData.append('name', studentName);
    formData.append('image', imageFile);

    // Get CSRF token if available (for Laravel CSRF protection)
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    const headers = {
      'Accept': 'application/json'
    };

    if (csrfToken) {
      headers['X-CSRF-TOKEN'] = csrfToken.getAttribute('content');
    }

    // Make API call
    const response = await fetch('/api/cheating-events', {
      method: 'POST',
      headers: headers,
      body: formData
    });

    const result = await response.json();

    if (response.ok && result.success) {
      console.log('Cheating event uploaded successfully:', result.data);
      return {
        success: true,
        data: result.data,
        message: result.message
      };
    } else {
      console.error('Upload failed:', result);
      return {
        success: false,
        error: result.message || 'Upload failed',
        errors: result.errors || {}
      };
    }
  } catch (error) {
    console.error('Network error uploading cheating event:', error);
    return {
      success: false,
      error: 'Network error: ' + error.message
    };
  }
}

// Helper function to convert canvas to blob for upload
function canvasToBlob(canvas, quality = 0.8) {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(blob);
    }, 'image/jpeg', quality);
  });
}

// Function to capture current frame and upload cheating event
async function captureAndUploadCheatingEvent(studentName) {
  if (!cameraActive || !videoCanvas) {
    console.error('Camera is not active or canvas not available');
    return {
      success: false,
      error: 'Camera is not active'
    };
  }

  try {
    // Convert current canvas frame to blob
    const imageBlob = await canvasToBlob(videoCanvas);

    // Create a File object from the blob
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `cheating_evidence_${timestamp}.jpg`;
    const imageFile = new File([imageBlob], fileName, { type: 'image/jpeg' });

    // Upload the cheating event
    const result = await uploadCheatingEvent(studentName, imageFile);

    if (result.success) {
      console.log('Cheating event captured and uploaded:', result.data);
      // You can add UI feedback here later
    } else {
      console.error('Failed to upload cheating event:', result.error);
      // You can add error handling UI here later
    }

    return result;
  } catch (error) {
    console.error('Error capturing and uploading cheating event:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Loading modal functions
function showLoadingModal() {
  const modal = document.getElementById('loadingModal');
  modal.style.display = 'flex';
}

function hideLoadingModal() {
  const modal = document.getElementById('loadingModal');
  modal.style.display = 'none';
}

// Initialize MediaPipe models and force download
async function downloadAndInitializeModels() {
  if (modelsLoaded) {
    return; // Models already loaded
  }

  do {
    localStorage.setItem("nama", prompt("Masukkan nama:"));
  } while (!localStorage.getItem("nama"))

  showLoadingModal();
  downloadButton.disabled = true;
  downloadButton.style.opacity = '0.5';

  try {
    // Initialize Face Mesh
    faceMesh = new FaceMesh({
      locateFile: (file) => {
        return `assets/mediapipe/${file}`;
      }
    });

    faceMesh.setOptions({
      maxNumFaces: 1,
      refineLandmarks: true,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    faceMesh.onResults((results) => {
      if (results.multiFaceLandmarks && results.multiFaceLandmarks.length > 0) {
        if (detectionResults) {
          detectionResults.faceLandmarks = results.multiFaceLandmarks[0];
        } else {
          detectionResults = {
            faceLandmarks: results.multiFaceLandmarks[0],
            image: results.image
          };
        }
      }
    });

    // Initialize Pose
    pose = new Pose({
      locateFile: (file) => {
        return `assets/mediapipe/${file}`;
      }
    });

    pose.setOptions({
      modelComplexity: 1,
      smoothLandmarks: true,
      enableSegmentation: false,
      smoothSegmentation: false,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    pose.onResults((results) => {
      if (results.poseLandmarks) {
        if (detectionResults) {
          detectionResults.poseLandmarks = results.poseLandmarks;
        } else {
          detectionResults = {
            poseLandmarks: results.poseLandmarks,
            image: results.image
          };
        }
      }
    });

    // Force model download by calling initialize()
    console.log("Downloading Face Mesh model...");
    await faceMesh.initialize();
    console.log("Downloading Pose model...");
    await pose.initialize();

    console.log("MediaPipe models downloaded and initialized successfully");
    modelsLoaded = true;

    // Enable camera button and hide download button
    toggleButton.disabled = false;
    toggleButton.style.opacity = '1';
    downloadButton.style.display = 'none';

    hideLoadingModal();
  } catch (error) {
    console.error("Error downloading MediaPipe models:", error);
    downloadButton.disabled = false;
    downloadButton.style.opacity = '1';
    hideLoadingModal();
    alert("Failed to download face detection models. Please check your internet connection and try again.");
  }
}

// Process detection results and extract landmarks
function extractLandmarks() {
  if (!detectionResults) {
    return null;
  }

  const width = videoCanvas.width;
  const height = videoCanvas.height;
  const landmarks = {};

  // Extract face landmarks if available
  if (detectionResults.faceLandmarks) {
    const face = detectionResults.faceLandmarks;

    // Key face landmarks (MediaPipe face mesh indices)
    landmarks.leftEye = {
      x: face[33].x * width,
      y: face[33].y * height
    };
    landmarks.rightEye = {
      x: face[263].x * width,
      y: face[263].y * height
    };
    landmarks.noseTip = {
      x: face[1].x * width,
      y: face[1].y * height
    };
    landmarks.leftEar = {
      x: face[234].x * width,
      y: face[234].y * height
    };
    landmarks.rightEar = {
      x: face[454].x * width,
      y: face[454].y * height
    };
    landmarks.mouthLeft = {
      x: face[61].x * width,
      y: face[61].y * height
    };
    landmarks.mouthRight = {
      x: face[291].x * width,
      y: face[291].y * height
    };
  }

  // Extract pose landmarks if available
  if (detectionResults.poseLandmarks) {
    const pose = detectionResults.poseLandmarks;

    landmarks.leftShoulder = {
      x: pose[11].x * width,
      y: pose[11].y * height
    };
    landmarks.rightShoulder = {
      x: pose[12].x * width,
      y: pose[12].y * height
    };
  }

  return landmarks;
}

// Calculate angle between two shoulder points
function calculateAngle(shoulderLeft, shoulderRight) {
  const deltaX = shoulderRight.x - shoulderLeft.x;
  const deltaY = shoulderRight.y - shoulderLeft.y;
  const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
  return angle;
}

// Simplified detection function using MediaPipe results
function detectFaceAndShoulder() {
  // Use real MediaPipe detection results
  const landmarks = extractLandmarks();

  if (!landmarks) {
    // Return default positions if no detection
    return {
      leftEye: { x: 100, y: 100 },
      rightEye: { x: 150, y: 100 },
      noseTip: { x: 125, y: 120 },
      leftEar: { x: 80, y: 100 },
      rightEar: { x: 170, y: 100 },
      mouthLeft: { x: 110, y: 140 },
      mouthRight: { x: 140, y: 140 },
      leftShoulder: { x: 50, y: 200 },
      rightShoulder: { x: 200, y: 200 }
    };
  }

  return landmarks;
}

// Cheating detection algorithm (based on cheat.py)
function detectCheating(landmarks) {
  if (!landmarks || !landmarks.leftEye || !landmarks.rightEye || !landmarks.noseTip) {
    return { status: "no detection", color: "blue" };
  }

  const threshold = 20; // Distance threshold in pixels
  const thresholdVertical = 45;

  // Check if nose is too far from left eye (looking left)
  const noseLeftEyeDistance = landmarks.noseTip.x - landmarks.leftEye.x;

  // Check if nose is too far from right eye (looking right) - corrected logic
  const noseRightEyeDistance = landmarks.noseTip.x - landmarks.rightEye.x + 30;

  // Check if nose is too low (looking down)
  const noseEyeVerticalDistance = landmarks.noseTip.y - Math.min(landmarks.leftEye.y, landmarks.rightEye.y);

  let cheatingDetected = false;
  let direction = "";

  if (noseLeftEyeDistance < threshold) {
    cheatingDetected = true;
    direction = "looking left";
  } else if (noseRightEyeDistance > threshold) {
    cheatingDetected = true;
    direction = "looking right";
  } else if (noseEyeVerticalDistance > thresholdVertical) {
    cheatingDetected = true;
    direction = "looking down";
  }

  // Check shoulder angle if shoulders are detected
  if (landmarks.leftShoulder && landmarks.rightShoulder) {
    const angle = calculateAngle(landmarks.leftShoulder, landmarks.rightShoulder);
    if (Math.abs(angle) < 176) {
      cheatingDetected = true;
      direction += " (tilted posture)";
    }
  }

  const currentTime = Date.now();

  if (cheatingDetected) {
    if (!tengokKiriDetected) {
      startTime = currentTime;
      tengokKiriDetected = true;
    }

    consecutiveCheatingDetections++;

    // Throttled upload - only upload every 3 seconds, but immediately on first detection
    if (consecutiveCheatingDetections === 1 || currentTime - lastUploadTime >= uploadThrottleDelay) {
      captureAndUploadCheatingEvent(localStorage.getItem("nama"));
      lastUploadTime = currentTime;
    }

    const elapsedTime = (currentTime - startTime) / 1000;

    if (elapsedTime >= cheatingDuration) {
      cheatingStatus = `cheating detected: ${direction}`;
      return { status: cheatingStatus, color: "red", duration: elapsedTime };
    } else {
      cheatingStatus = `suspicious activity: ${direction} (${elapsedTime.toFixed(1)}s)`;
      return { status: cheatingStatus, color: "yellow", duration: elapsedTime };
    }
  } else {
    // Reset detection
    tengokKiriDetected = false;
    startTime = null;
    consecutiveCheatingDetections = 0;
    cheatingStatus = "stand by";
    return { status: cheatingStatus, color: "blue", duration: 0 };
  }
}

// Process frame with real MediaPipe detection
async function processFrame() {
  if (!cameraActive || !video) return;

  const currentTime = performance.now();

  // Frame rate limiting - only process if enough time has passed
  if (currentTime - lastFrameTime < frameInterval) {
    if (cameraActive) {
      requestAnimationFrame(processFrame);
    }
    return;
  }

  lastFrameTime = currentTime;

  canvasContext.clearRect(0, 0, videoCanvas.width, videoCanvas.height);
  canvasContext.drawImage(video, 0, 0, videoCanvas.width, videoCanvas.height);

  // Send frame to MediaPipe for processing
  if (faceMesh && pose) {
    // Create a canvas to get the current frame for MediaPipe
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);

    // Send to MediaPipe models
    await faceMesh.send({ image: canvas });
    await pose.send({ image: canvas });
  }

  // Get detection results and display landmarks
  const detection = detectFaceAndShoulder();

  // Run cheating detection
  const cheatingResult = detectCheating(detection);

  // Draw face landmarks
  canvasContext.fillStyle = 'lime';

  // Left Eye
  canvasContext.beginPath();
  canvasContext.arc(detection.leftEye.x, detection.leftEye.y, 6, 0, 2 * Math.PI);
  canvasContext.fill();

  // Right Eye
  canvasContext.beginPath();
  canvasContext.arc(detection.rightEye.x, detection.rightEye.y, 6, 0, 2 * Math.PI);
  canvasContext.fill();

  // Nose tip
  canvasContext.fillStyle = 'cyan';
  canvasContext.beginPath();
  canvasContext.arc(detection.noseTip.x, detection.noseTip.y, 8, 0, 2 * Math.PI);
  canvasContext.fill();

  // Left Ear
  canvasContext.fillStyle = 'orange';
  canvasContext.beginPath();
  canvasContext.arc(detection.leftEar.x, detection.leftEar.y, 5, 0, 2 * Math.PI);
  canvasContext.fill();

  // Right Ear
  canvasContext.beginPath();
  canvasContext.arc(detection.rightEar.x, detection.rightEar.y, 5, 0, 2 * Math.PI);
  canvasContext.fill();

  // Left Mouth corner
  canvasContext.fillStyle = 'magenta';
  canvasContext.beginPath();
  canvasContext.arc(detection.mouthLeft.x, detection.mouthLeft.y, 4, 0, 2 * Math.PI);
  canvasContext.fill();

  // Right Mouth corner
  canvasContext.beginPath();
  canvasContext.arc(detection.mouthRight.x, detection.mouthRight.y, 4, 0, 2 * Math.PI);
  canvasContext.fill();

  // Left Shoulder
  canvasContext.fillStyle = 'red';
  canvasContext.beginPath();
  canvasContext.arc(detection.leftShoulder.x, detection.leftShoulder.y, 8, 0, 2 * Math.PI);
  canvasContext.fill();

  // Right Shoulder
  canvasContext.beginPath();
  canvasContext.arc(detection.rightShoulder.x, detection.rightShoulder.y, 8, 0, 2 * Math.PI);
  canvasContext.fill();

  // Draw shoulder line
  canvasContext.strokeStyle = 'red';
  canvasContext.lineWidth = 3;
  canvasContext.beginPath();
  canvasContext.moveTo(detection.leftShoulder.x, detection.leftShoulder.y);
  canvasContext.lineTo(detection.rightShoulder.x, detection.rightShoulder.y);
  canvasContext.stroke();

  // Draw cheating detection status box
  const boxColor = cheatingResult.color === 'red' ? 'rgba(255, 0, 0, 0.7)' :
    cheatingResult.color === 'yellow' ? 'rgba(255, 255, 0, 0.7)' :
      'rgba(0, 0, 255, 0.7)';

  canvasContext.fillStyle = boxColor;
  canvasContext.fillRect(10, 10, 300, 80);

  canvasContext.fillStyle = 'white';
  canvasContext.font = "16px Arial";
  canvasContext.fillText("Status: " + cheatingResult.status, 20, 35);
  canvasContext.fillText("Duration: " + cheatingResult.duration.toFixed(1) + "s", 20, 55);
  canvasContext.fillText("Threshold: " + cheatingDuration + "s", 20, 75);

  // Draw labels for landmarks
  canvasContext.fillStyle = 'white';
  canvasContext.font = "14px Arial";
  canvasContext.strokeStyle = 'black';
  canvasContext.lineWidth = 3;

  // Eye labels
  canvasContext.strokeText("LEFT EYE", detection.leftEye.x - 15, detection.leftEye.y - 15);
  canvasContext.fillText("LEFT EYE", detection.leftEye.x - 15, detection.leftEye.y - 15);

  canvasContext.strokeText("RIGHT EYE", detection.rightEye.x - 15, detection.rightEye.y - 15);
  canvasContext.fillText("RIGHT EYE", detection.rightEye.x - 15, detection.rightEye.y - 15);

  // Nose label
  canvasContext.strokeText("NOSE", detection.noseTip.x - 10, detection.noseTip.y - 15);
  canvasContext.fillText("NOSE", detection.noseTip.x - 10, detection.noseTip.y - 15);

  // Ear labels
  canvasContext.strokeText("L EAR", detection.leftEar.x - 15, detection.leftEar.y - 15);
  canvasContext.fillText("L EAR", detection.leftEar.x - 15, detection.leftEar.y - 15);

  canvasContext.strokeText("R EAR", detection.rightEar.x - 15, detection.rightEar.y - 15);
  canvasContext.fillText("R EAR", detection.rightEar.x - 15, detection.rightEar.y - 15);

  // Mouth labels
  canvasContext.strokeText("L MOUTH", detection.mouthLeft.x - 20, detection.mouthLeft.y - 15);
  canvasContext.fillText("L MOUTH", detection.mouthLeft.x - 20, detection.mouthLeft.y - 15);

  canvasContext.strokeText("R MOUTH", detection.mouthRight.x - 20, detection.mouthRight.y - 15);
  canvasContext.fillText("R MOUTH", detection.mouthRight.x - 20, detection.mouthRight.y - 15);

  // Shoulder labels
  canvasContext.strokeText("LEFT SHOULDER", detection.leftShoulder.x - 25, detection.leftShoulder.y - 15);
  canvasContext.fillText("LEFT SHOULDER", detection.leftShoulder.x - 25, detection.leftShoulder.y - 15);

  canvasContext.strokeText("RIGHT SHOULDER", detection.rightShoulder.x - 25, detection.rightShoulder.y - 15);
  canvasContext.fillText("RIGHT SHOULDER", detection.rightShoulder.x - 25, detection.rightShoulder.y - 15);

  // Copy canvas to processed image
  processedImage.src = videoCanvas.toDataURL();
  processedImage.style.display = 'block';

  // Continue processing
  if (cameraActive) {
    requestAnimationFrame(processFrame);
  }
}

function startCamera() {
  if (!modelsLoaded) {
    alert("Please download the face detection models first by clicking the download button.");
    return;
  }

  navigator.mediaDevices.getUserMedia({
    video: {
      width: 640,
      height: 480,
      frameRate: { ideal: 30, max: 30 }
    }
  })
    .then(async (mediaStream) => {
      stream = mediaStream;
      videoCanvas.width = 640;
      videoCanvas.height = 480;

      video = document.createElement('video');
      video.srcObject = stream;
      video.play();

      video.addEventListener('loadedmetadata', () => {
        cameraActive = true;
        toggleButton.classList.add('active');
        toggleIcon.textContent = 'videocam';

        // Start processing frames
        processFrame();
      });
    })
    .catch((err) => {
      console.error("Error accessing camera: ", err);
      alert("Error accessing camera. Please check permissions and try again.");
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
  }
}

// Download button event listener
downloadButton.addEventListener('click', () => {
  downloadAndInitializeModels();
});

// Toggle camera button event listener
toggleButton.addEventListener('click', () => {
  if (cameraActive) {
    stopCamera();
  } else {
    startCamera();
  }
});

function openModal(name, jumlah, imageUrls, timestamps) {
  document.getElementById('modalName').innerText = 'Mode: ' + name;
  document.getElementById('modalClass').innerText = 'Tangkapan Hari Ini: ' + jumlah;

  // Split images and timestamps
  var imageArray = imageUrls.split(',');
  var timestampArray = timestamps.split(',');

  var tableBody = document.getElementById('modalImageTableBody');
  tableBody.innerHTML = ''; // Clear any existing table rows

  // Create a single row for images
  var rowImages = document.createElement('tr');
  var cellImagesLabel = document.createElement('td');
  cellImagesLabel.colSpan = 2; // Merge cells for image label
  rowImages.appendChild(cellImagesLabel);

  // Create a single row for timestamps
  var rowTimestamps = document.createElement('tr');
  var cellTimestampsLabel = document.createElement('td');
  cellTimestampsLabel.colSpan = 2; // Merge cells for timestamp label
  rowTimestamps.appendChild(cellTimestampsLabel);

  // Loop over the images and timestamps to populate the rows
  imageArray.forEach(function (imageUrl, index) {
    if (imageUrl.trim() !== '') {
      // Create image cell
      var cellImage = document.createElement('td');
      var img = document.createElement('img');
      img.src = imageUrl.trim();
      img.className = 'studentmodel-table-image'; // Ensure the class matches your CSS
      img.alt = 'Bukti Kecurangan';
      cellImage.appendChild(img);
      rowImages.appendChild(cellImage);

      // Create timestamp cell
      var cellTimestamp = document.createElement('td');
      cellTimestamp.innerText = timestampArray[index] ? timestampArray[index].trim() : 'N/A';
      rowTimestamps.appendChild(cellTimestamp);
    }
  });

  // Append the rows to the table body
  tableBody.appendChild(rowImages);
  tableBody.appendChild(rowTimestamps);

  var modal = document.getElementById('studentModal');
  modal.style.display = 'block'; // Show the modal

  // Close modal when clicking outside of the modal content
  modal.addEventListener('click', function (event) {
    if (event.target === modal) { // Check if the click was outside the modal content
      closeModal(); // Call the closeModal function
    }
  });
}

function closeModal() {
  document.getElementById('studentModal').style.display = 'none'; // Hide the modal
}

// API function to upload cheating event
async function uploadCheatingEvent(studentName, imageFile) {
  try {
    // Create FormData to handle file upload
    const formData = new FormData();
    formData.append('name', studentName);
    formData.append('image', imageFile);

    // Get CSRF token if available (for Laravel CSRF protection)
    const csrfToken = document.querySelector('meta[name="csrf-token"]');
    const headers = {
      'Accept': 'application/json'
    };

    if (csrfToken) {
      headers['X-CSRF-TOKEN'] = csrfToken.getAttribute('content');
    }

    // Make API call
    const response = await fetch('/api/cheating-events', {
      method: 'POST',
      headers: headers,
      body: formData
    });

    const result = await response.json();

    if (response.ok && result.success) {
      console.log('Cheating event uploaded successfully:', result.data);
      return {
        success: true,
        data: result.data,
        message: result.message
      };
    } else {
      console.error('Upload failed:', result);
      return {
        success: false,
        error: result.message || 'Upload failed',
        errors: result.errors || {}
      };
    }
  } catch (error) {
    console.error('Network error uploading cheating event:', error);
    return {
      success: false,
      error: 'Network error: ' + error.message
    };
  }
}

// Helper function to convert canvas to blob for upload
function canvasToBlob(canvas, quality = 0.8) {
  return new Promise((resolve) => {
    canvas.toBlob((blob) => {
      resolve(blob);
    }, 'image/jpeg', quality);
  });
}

// Function to capture current frame and upload cheating event
async function captureAndUploadCheatingEvent(studentName) {
  if (!cameraActive || !videoCanvas) {
    console.error('Camera is not active or canvas not available');
    return {
      success: false,
      error: 'Camera is not active'
    };
  }

  try {
    // Convert current canvas frame to blob
    const imageBlob = await canvasToBlob(videoCanvas);

    // Create a File object from the blob
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const fileName = `cheating_evidence_${timestamp}.jpg`;
    const imageFile = new File([imageBlob], fileName, { type: 'image/jpeg' });

    // Upload the cheating event
    const result = await uploadCheatingEvent(studentName, imageFile);

    if (result.success) {
      console.log("Cheating event captured and uploaded:", result.data);
      // You can add UI feedback here later
    } else {
      console.error("Failed to upload cheating event:", result.error);
      // You can add error handling UI here later
    }

    return result;
  } catch (error) {
    console.error("Error capturing and uploading cheating event:", error);
    return {
      success: false,
      error: error.message
    };
  }
}
