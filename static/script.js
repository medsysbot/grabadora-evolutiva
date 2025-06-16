let mediaRecorder;
let audioChunks = [];

function iniciarGrabacion() {
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      try {
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      } catch (e) {
        alert("Este navegador no soporta el tipo de audio requerido.");
        return;
      }

      mediaRecorder.start();
      audioChunks = [];

      mediaRecorder.ondataavailable = e => {
        if (e.data.size > 0) audioChunks.push(e.data);
      };

      mediaRecorder.onstop = () => {
        if (audioChunks.length === 0) {
          alert("No se grabó ningún audio.");
          return;
        }
        const blob = new Blob(audioChunks, { type: 'audio/webm' });
        const audioURL = URL.createObjectURL(blob);
        const player = document.getElementById("player");
        player.src = audioURL;
      };
    })
    .catch(err => {
      alert("Error: No se puede acceder al micrófono.");
    });
}

function detenerGrabacion() {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  } else {
    alert("No hay grabación en curso.");
  }
}

function reproducirGrabacion() {
  const player = document.getElementById("player");
  if (player.src) {
    player.play();
  } else {
    alert("No hay audio para reproducir.");
  }
}

function diagnosticar() {
  fetch("/diagnostico").then(r => r.text()).then(alert);
}

function reparar() {
  fetch("/reparar").then(r => r.text()).then(alert);
}
