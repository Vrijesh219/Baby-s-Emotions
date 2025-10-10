(() => {
  const API_URL = (window.API_URL || 'http://localhost:8080') + '/predict';

  const btnRecord = document.getElementById('btnRecord');
  const btnStop = document.getElementById('btnStop');
  const btnUpload = document.getElementById('btnUpload');
  const player = document.getElementById('player');
  const timerEl = document.getElementById('timer');
  const statusEl = document.getElementById('status');
  const resultEl = document.getElementById('result');

  // Recording state
  let mediaStream = null;
  let audioCtx = null;
  let sourceNode = null;
  let processor = null;
  let pcmChunks = [];
  let recordedSampleRate = 44100;
  let tickInterval = null;
  let startTs = 0;
  let blob = null;
  let wavesurfer = null;

  function setStatus(text, isError = false) {
    statusEl.textContent = text || '';
    statusEl.style.color = isError ? '#fca5a5' : '#9ca3af';
  }

  function fmt(ms) {
    const s = Math.floor(ms / 1000);
    const mm = String(Math.floor(s / 60)).padStart(2, '0');
    const ss = String(s % 60).padStart(2, '0');
    return `${mm}:${ss}`;
  }

  function startTimer() {
    startTs = Date.now();
    tickInterval = setInterval(() => {
      timerEl.textContent = fmt(Date.now() - startTs);
    }, 200);
  }

  function stopTimer() {
    clearInterval(tickInterval);
    tickInterval = null;
  }

  async function ensureWave() {
    if (wavesurfer) return wavesurfer;
    wavesurfer = window.WaveSurfer.create({
      container: '#wave',
      waveColor: '#60a5fa',
      progressColor: '#2563eb',
      cursorColor: '#e5e7eb',
      height: 120,
      normalize: true,
    });
    return wavesurfer;
  }

  async function drawWaveFromBlob(b) {
    const ws = await ensureWave();
    ws.empty();
    const buf = await b.arrayBuffer();
    await ws.loadBlob(new Blob([buf]));
  }

  function floatTo16BitPCM(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    let offset = 0;
    for (let i = 0; i < float32Array.length; i++) {
      let s = Math.max(-1, Math.min(1, float32Array[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      offset += 2;
    }
    return buffer;
  }

  function encodeWAV(samples, sampleRate) {
    const bytesPerSample = 2; // 16-bit PCM
    const blockAlign = bytesPerSample * 1; // mono
    const byteRate = sampleRate * blockAlign;
    const dataBuffer = floatTo16BitPCM(samples);
    const dataLength = dataBuffer.byteLength;
    const buffer = new ArrayBuffer(44 + dataLength);
    const view = new DataView(buffer);

    // RIFF header
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataLength, true);
    writeString(view, 8, 'WAVE');
    // fmt chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true); // Subchunk1Size (16 for PCM)
    view.setUint16(20, 1, true);  // AudioFormat (1=PCM)
    view.setUint16(22, 1, true);  // NumChannels (mono)
    view.setUint32(24, sampleRate, true); // SampleRate
    view.setUint32(28, byteRate, true);   // ByteRate
    view.setUint16(32, blockAlign, true); // BlockAlign
    view.setUint16(34, 16, true);         // BitsPerSample
    // data chunk
    writeString(view, 36, 'data');
    view.setUint32(40, dataLength, true);
    new Uint8Array(buffer).set(new Uint8Array(dataBuffer), 44);
    return new Blob([buffer], { type: 'audio/wav' });
  }

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  async function startRecording() {
    try {
      setStatus('Requesting microphone...');
      mediaStream = await navigator.mediaDevices.getUserMedia({ audio: { channelCount: 1 } });

      audioCtx = new (window.AudioContext || window.webkitAudioContext)({
        latencyHint: 'interactive'
      });
      recordedSampleRate = audioCtx.sampleRate || 44100;

      sourceNode = audioCtx.createMediaStreamSource(mediaStream);
      // ScriptProcessor is deprecated but widely supported; bufferSize 4096, mono
      processor = audioCtx.createScriptProcessor(4096, 1, 1);
      pcmChunks = [];

      processor.onaudioprocess = (e) => {
        const input = e.inputBuffer.getChannelData(0);
        // Copy the buffer to avoid mutation
        pcmChunks.push(new Float32Array(input));
      };

      sourceNode.connect(processor);
      processor.connect(audioCtx.destination);

      setStatus('Recording...');
      startTimer();
      btnRecord.disabled = true;
      btnStop.disabled = false;
      btnUpload.disabled = true;
      resultEl.textContent = '';
    } catch (err) {
      console.error(err);
      setStatus('Microphone access denied or unsupported.', true);
    }
  }

  async function stopRecording() {
    try {
      stopTimer();
      setStatus('Processing audio...');

      if (processor) {
        processor.disconnect();
      }
      if (sourceNode) {
        sourceNode.disconnect();
      }
      if (audioCtx) {
        try { await audioCtx.close(); } catch {}
      }
      if (mediaStream) {
        mediaStream.getTracks().forEach((t) => t.stop());
      }

      // Merge Float32 chunks
      let totalLen = 0;
      for (const c of pcmChunks) totalLen += c.length;
      const merged = new Float32Array(totalLen);
      let offset = 0;
      for (const c of pcmChunks) { merged.set(c, offset); offset += c.length; }

      blob = encodeWAV(merged, recordedSampleRate);
      const url = URL.createObjectURL(blob);
      player.src = url;
      await drawWaveFromBlob(blob);

      setStatus('Ready to upload');
      btnUpload.disabled = false;
      btnRecord.disabled = false;
      btnStop.disabled = true;
    } catch (err) {
      console.error(err);
      setStatus('Failed to process audio', true);
    }
  }

  async function uploadAndPredict() {
    if (!blob) return;
    setStatus('Uploading...');
    resultEl.textContent = '';
    try {
      const form = new FormData();
      form.append('file', blob, 'recording.wav');
      const res = await fetch(API_URL, { method: 'POST', body: form });
      const txt = await res.text();
      let data = null;
      try { data = JSON.parse(txt); } catch { data = { raw: txt }; }
      if (!res.ok) {
        setStatus('Server error', true);
        resultEl.textContent = JSON.stringify(data, null, 2);
        return;
      }
      setStatus('Prediction complete');
      if (data && typeof data === 'object' && 'emotion' in data) {
        const conf = typeof data.confidence === 'number' ? (data.confidence * 100).toFixed(2) + '%' : String(data.confidence || '');
        resultEl.textContent = `Emotion: ${data.emotion} | Confidence: ${conf}`;
      } else {
        resultEl.textContent = JSON.stringify(data, null, 2);
      }
    } catch (err) {
      console.error(err);
      setStatus('Upload failed', true);
      resultEl.textContent = String(err);
    }
  }

  btnRecord.addEventListener('click', startRecording);
  btnStop.addEventListener('click', stopRecording);
  btnUpload.addEventListener('click', uploadAndPredict);
})();


