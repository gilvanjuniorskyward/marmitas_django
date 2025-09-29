// Simple scanner using the BarcodeDetector API (Chrome/Android recommended)
let running = false;
const statusEl = document.getElementById('status');
const videoEl = document.getElementById('camera');
const toggleBtn = document.getElementById('toggle');
const manualInput = document.getElementById('manual');
const enviarBtn = document.getElementById('enviar');

async function startCamera() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    videoEl.srcObject = stream;
    await videoEl.play();
    statusEl.textContent = 'Câmera iniciada. Lendo…';
    return true;
  } catch (e) {
    statusEl.textContent = 'Erro ao acessar a câmera: ' + e.message;
    return false;
  }
}

async function stopCamera() {
  const stream = videoEl.srcObject;
  if (stream) {
    stream.getTracks().forEach(t => t.stop());
    videoEl.srcObject = null;
  }
  statusEl.textContent = 'Câmera parada.';
}

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

async function scanLoop() {
  if (!('BarcodeDetector' in window)) {
    statusEl.textContent = 'Leitor não suportado neste navegador. Use o campo manual.';
    return;
  }
  const formats = ['qr_code','code_128','code_39','ean_13','ean_8','upc_a','upc_e'];
  let detector;
  try {
    detector = new BarcodeDetector({ formats });
  } catch (e) {
    statusEl.textContent = 'Leitor indisponível. Use o campo manual.';
    return;
  }
  while (running) {
    try {
      const barcodes = await detector.detect(videoEl);
      if (barcodes && barcodes.length > 0) {
        const code = barcodes[0].rawValue;
        running = false;
        await sendCode(code);
        await stopCamera();
        toggleBtn.textContent = 'Iniciar Leitura';
        break;
      }
    } catch (e) {
      // ignore frame errors
    }
    await new Promise(r => setTimeout(r, 150));
  }
}

toggleBtn.addEventListener('click', async () => {
  if (running) {
    running = false;
    await stopCamera();
    toggleBtn.textContent = 'Iniciar Leitura';
  } else {
    const ok = await startCamera();
    if (ok) {
      running = true;
      toggleBtn.textContent = 'Parar Leitura';
      scanLoop();
    }
  }
});

enviarBtn.addEventListener('click', async () => {
  const code = manualInput.value.trim();
  if (code) {
    await sendCode(code);
  }
});