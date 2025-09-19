async function checkDetection() {
   try {
       const res = await fetch("/status");
       const data = await res.json();
       const alertBox = document.getElementById("alertBox");
       const alertText = document.getElementById("alertText");
       const alertTime = document.getElementById("alertTime");
       const detectedTime = document.getElementById("detectedTime");
       const humanCount = document.getElementById("humanCount");

       const now = new Date();
       alertTime.textContent = `Last checked: ${now.toLocaleTimeString()}`;

       if (data.detected) {
           alertText.textContent = "🚨 Human Detected!";
           alertBox.classList.remove("safe");
           alertBox.classList.add("detected");
       } else {
           alertText.textContent = "✅ No Human Detected";
           alertBox.classList.remove("detected");
           alertBox.classList.add("safe");
       }

       if (data.last_detected_time) {
           detectedTime.textContent = `Human detected at: ${data.last_detected_time}`;
       } else {
           detectedTime.textContent = '';
       }

       if (data.human_count !== undefined) {
           humanCount.textContent = `Number of humans: ${data.human_count}`;
       } else {
           humanCount.textContent = '';
       }

   } catch (err) {
       console.error("Error checking detection:", err);
   }
}

setInterval(checkDetection, 1000);
