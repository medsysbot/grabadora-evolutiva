let mediaRecorder;
let audioChunks = [];

function iniciarGrabacion() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      mediaRecorder = new MediaRecorder(stream);
      mediaRecorder.start();
      audioChunks = [];
      mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
    })
    .catch(err => {
      alert("Error: No se puede acceder al micrófono.");
    });
}

function detenerGrabacion() {
  if (mediaRecorder) {
    mediaRecorder.stop();
    mediaRecorder.onstop = () => {
      const blob = new Blob(audioChunks);
      const audioURL = URL.createObjectURL(blob);
      document.getElementById("player").src = audioURL;
    };
  }
}

function reproducirGrabacion() {
  const player = document.getElementById("player");
  player.play();
}

function diagnosticar() {
  fetch("/diagnostico").then(r => r.text()).then(alert);
}

function reparar() {
  fetch("/reparar").then(r => r.text()).then(alert);
}
