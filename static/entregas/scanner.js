let running = false;
const statusEl = document.getElementById('status');
const toggleBtn = document.getElementById('toggle');
const manualInput = document.getElementById('manual');
const enviarBtn = document.getElementById('enviar');
const readerEl = document.getElementById('reader');

let html5QrCode = null;

async function sendCode(code) {
  try {
    const url = `/registrar/?code=${encodeURIComponent(code)}`;
    const res = await fetch(url, { method: 'GET', credentials: 'same-origin' });
    const data = await res.json();
    if (data.ok) {
      statusEl.textContent = '✅ ' + data.mensagem;
    } else {
      statusEl.textContent = '⚠️ ' + (data.mensagem || 'Falha ao registrar.');
    }
  } catch (e) {
    statusEl.textContent = 'Erro: ' + e.message;
  }
}

async function startScanner() {
  // Mostra a div do leitor
  readerEl.style.display = 'block';
  
  html5QrCode = new Html5Qrcode("reader");

  try {
    await html5QrCode.start(
      { facingMode: "environment" }, // câmera traseira
      { fps: 10, qrbox: 250 },
      async (decodedText) => {
        running = false;
        await sendCode(decodedText);
        stopScanner();
      }
    );
    statusEl.textContent = "Câmera iniciada. Lendo…";
  } catch (e) {
    statusEl.textContent = "Erro ao acessar a câmera: " + e.message;
  }
}

function stopScanner() {
  if (html5QrCode) {
    html5QrCode.stop().then(() => {
      readerEl.style.display = 'none';
      statusEl.textContent = 'Câmera parada.';
    });
  }
}

toggleBtn.addEventListener('click', async () => {
  if (running) {
    running = false;
    stopScanner();
    toggleBtn.textContent = 'Iniciar Leitura';
  } else {
    running = true;
    toggleBtn.textContent = 'Parar Leitura';
    startScanner();
  }
});

enviarBtn.addEventListener('click', async () => {
  const code = manualInput.value.trim();
  if (code) {
    await sendCode(code);
  }
});
