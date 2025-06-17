let mediaRecorder;
let audioChunks = [];

function obtenerMimeType() {
  const formatos = ['audio/webm', 'audio/mp4', 'audio/wav'];
  for (const tipo of formatos) {
    if (MediaRecorder.isTypeSupported(tipo)) {
      return tipo;
    }
  }
  return null;
}

function registrarEvento(mensaje) {
  fetch("/registrar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mensaje })
  }).catch(() => {
    console.warn("No se pudo registrar el evento");
  });
}

function iniciarGrabacion() {
  registrarEvento("Se inició grabación");
  navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
      const tipo = obtenerMimeType();
      if (!tipo) {
        alert("Este navegador no soporta grabación de audio compatible.");
        return;
      }
      try {
        mediaRecorder = new MediaRecorder(stream, { mimeType: tipo });
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
        const blob = new Blob(audioChunks, { type: tipo });
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
  registrarEvento("Se detuvo la grabación");
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
  } else {
    alert("No hay grabación en curso.");
  }
}

function reproducirGrabacion() {
  registrarEvento("Se reprodujo el audio");
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
