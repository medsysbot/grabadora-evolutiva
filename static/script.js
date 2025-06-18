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

function consultaManualMejora() {
  fetch("/consultar_mejora_manual", { method: "POST" })
    .then(r => r.json())
    .then(data => {
      document.getElementById("respuesta-mejora").innerText =
        "Sugerencia IA: " + data.respuesta;
    })
    .catch(() => {
      document.getElementById("respuesta-mejora").innerText =
        "Error al consultar la IA.";
    });
}

function cargarSugerencias() {
  fetch("/sugerencias_pendientes")
    .then(r => r.json())
    .then(data => {
      const div = document.getElementById("bandeja-sugerencias");
      div.innerHTML = "";
      data.forEach(s => {
        div.innerHTML += `
          <div class="card mb-2 p-2">
            <div>${s.texto}</div>
            <button class="btn btn-success btn-sm mt-2" onclick="aplicarSugerencia('${s.id}')">Aplicar</button>
            <button class="btn btn-danger btn-sm mt-2 ms-2" onclick="descartarSugerencia('${s.id}')">Descartar</button>
          </div>
        `;
      });
    });
}

function aplicarSugerencia(id) {
  fetch("/aplicar_sugerencia", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({id})
  })
    .then(r => r.json())
    .then(data => {
      cargarSugerencias();
      if (data.codigo) {
        document.getElementById("codigo-generado").textContent = data.codigo;
      }
    });
}

function descartarSugerencia(id) {
  fetch("/descartar_sugerencia", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({id})
  }).then(() => cargarSugerencias());
}

function verLog(nombre) {
  fetch(`/ver_log?archivo=${encodeURIComponent(nombre)}`)
    .then(res => {
      if (nombre.endsWith('.json')) {
        return res.json();
      }
      return res.text();
    })
    .then(data => {
      const cont = document.getElementById('resultado-log');
      if (!cont) return;
      if (Array.isArray(data)) {
        if (data.length === 0) {
          cont.innerHTML = '<p class="text-center">Lista vacía.</p>';
          return;
        }
        let html = '<ul class="list-group">';
        data.forEach(item => {
          if (typeof item === 'object') {
            const fecha = item.fecha ? item.fecha + ' - ' : '';
            const estado = item.estado ? ' [' + item.estado + ']' : '';
            const texto = item.texto || JSON.stringify(item);
            html += `<li class="list-group-item bg-dark text-light">${fecha}${texto}${estado}</li>`;
          } else {
            html += `<li class="list-group-item bg-dark text-light">${item}</li>`;
          }
        });
        html += '</ul>';
        cont.innerHTML = html;
      } else {
        cont.innerHTML = `<pre class="bg-dark text-info p-2">${data}</pre>`;
      }
    });
}
