'use strict';

const API = 'http://localhost:5000';
const lightState = { low_beam: 0, high_beam: 0, turn_left: 0, turn_right: 0 };
let afuState = 0;

/* ═══════════════════════════════════════════════════════════
   VITESSE – jauge canvas animée
═══════════════════════════════════════════════════════════ */
const cvs = document.getElementById('spd-canvas');
const c2  = cvs.getContext('2d');
const SZ  = 192;
let cur = 0, tgt = 0;

function drawSpeed(s) {
  c2.clearRect(0, 0, SZ, SZ);
  const cx = SZ/2, cy = SZ/2, r = 80;
  const sa = Math.PI * .75, tot = Math.PI * 1.5, pct = s / 100;

  // fond de piste
  c2.beginPath(); c2.arc(cx, cy, r, sa, sa + tot);
  c2.strokeStyle = '#0a1420'; c2.lineWidth = 13; c2.lineCap = 'round'; c2.stroke();

  // arc de valeur
  if (pct > 0) {
    const col = pct < .5
      ? `hsl(${120 - pct * 80}, 70%, 50%)`
      : `hsl(${40 - (pct - .5) * 90}, 80%, 50%)`;
    c2.beginPath(); c2.arc(cx, cy, r, sa, sa + tot * pct);
    c2.strokeStyle = col; c2.lineWidth = 13; c2.lineCap = 'round'; c2.stroke();
    c2.shadowColor = col; c2.shadowBlur = 14;
    c2.beginPath(); c2.arc(cx, cy, r, sa, sa + tot * pct);
    c2.strokeStyle = col; c2.lineWidth = 3; c2.stroke();
    c2.shadowBlur = 0;
  }

  // graduations
  for (let i = 0; i <= 10; i++) {
    const a = sa + (i / 10) * tot, l = i % 5 === 0 ? 11 : 5;
    c2.beginPath();
    c2.moveTo(cx + Math.cos(a) * (r + 5), cy + Math.sin(a) * (r + 5));
    c2.lineTo(cx + Math.cos(a) * (r + 5 + l), cy + Math.sin(a) * (r + 5 + l));
    c2.strokeStyle = i % 5 === 0 ? '#2d4a60' : '#162230';
    c2.lineWidth = i % 5 === 0 ? 1.5 : .8; c2.lineCap = 'butt'; c2.stroke();
    if (i % 5 === 0) {
      c2.fillStyle = '#2d4a60'; c2.font = '9px Share Tech Mono';
      c2.textAlign = 'center'; c2.textBaseline = 'middle';
      c2.fillText(i * 10, cx + Math.cos(a) * (r + 22), cy + Math.sin(a) * (r + 22));
    }
  }

  // bague extérieure
  c2.beginPath(); c2.arc(cx, cy, r + 9, 0, Math.PI * 2);
  c2.strokeStyle = '#15222e'; c2.lineWidth = 1; c2.stroke();

  // aiguille
  const na = sa + tot * pct;
  c2.save(); c2.translate(cx, cy); c2.rotate(na);
  c2.beginPath(); c2.moveTo(0, 5); c2.lineTo(r - 4, 0); c2.lineTo(0, -5);
  c2.fillStyle = '#f0a020'; c2.shadowColor = '#f0a020'; c2.shadowBlur = 11; c2.fill();
  c2.restore(); c2.shadowBlur = 0;

  // moyeu
  c2.beginPath(); c2.arc(cx, cy, 9, 0, Math.PI * 2); c2.fillStyle = '#162230'; c2.fill();
  c2.beginPath(); c2.arc(cx, cy, 4, 0, Math.PI * 2); c2.fillStyle = '#f0a020'; c2.fill();
}

(function loopSpeed() {
  const d = tgt - cur;
  if (Math.abs(d) > .15) {
    cur += d * .14;
    drawSpeed(cur);
    document.getElementById('spd-num').textContent = Math.round(cur);
  }
  requestAnimationFrame(loopSpeed);
})();

/* ═══════════════════════════════════════════════════════════
   GAZ – jauge demi-cercle animée
═══════════════════════════════════════════════════════════ */
const gc   = document.getElementById('gas-canvas');
const gCtx = gc.getContext('2d');
const GW = 174, GH = 87;
let gCur = 0, gTgt = 0;

function drawGas(v) {
  gCtx.clearRect(0, 0, GW, GH);
  const cx = GW / 2, cy = GH, r = GH - 10;
  const pct = Math.min(v / 255, 1);
  const a0 = Math.PI, span = Math.PI;

  // fond
  gCtx.beginPath(); gCtx.arc(cx, cy, r, a0, a0 + span);
  gCtx.strokeStyle = '#0a1420'; gCtx.lineWidth = 13; gCtx.lineCap = 'round'; gCtx.stroke();

  // zones colorées fixes
  [
    [0, .33, 'rgba(32,192,96,.16)'],
    [.33, .67, 'rgba(224,128,32,.16)'],
    [.67, 1,   'rgba(224,48,48,.16)'],
  ].forEach(([f, t, c]) => {
    gCtx.beginPath(); gCtx.arc(cx, cy, r, a0 + span * f, a0 + span * t);
    gCtx.strokeStyle = c; gCtx.lineWidth = 13; gCtx.lineCap = 'butt'; gCtx.stroke();
  });

  // arc de valeur
  if (pct > 0) {
    const col = pct < .33 ? '#20c060' : pct < .67 ? '#e08020' : '#e03030';
    gCtx.beginPath(); gCtx.arc(cx, cy, r, a0, a0 + span * pct);
    gCtx.strokeStyle = col; gCtx.lineWidth = 13; gCtx.lineCap = 'round'; gCtx.stroke();
    gCtx.shadowColor = col; gCtx.shadowBlur = 11;
    gCtx.beginPath(); gCtx.arc(cx, cy, r, a0, a0 + span * pct);
    gCtx.strokeStyle = col; gCtx.lineWidth = 3; gCtx.lineCap = 'round'; gCtx.stroke();
    gCtx.shadowBlur = 0;
  }

  // marques de graduation
  [0, .33, .67, 1].forEach(p => {
    const ang = a0 + span * p;
    const x1 = cx + Math.cos(ang) * (r + 2), y1 = cy + Math.sin(ang) * (r + 2);
    const x2 = cx + Math.cos(ang) * (r - 13), y2 = cy + Math.sin(ang) * (r - 13);
    gCtx.beginPath(); gCtx.moveTo(x1, y1); gCtx.lineTo(x2, y2);
    gCtx.strokeStyle = '#1a2d3e'; gCtx.lineWidth = 1.2; gCtx.stroke();
  });

  // aiguille
  const na = a0 + span * pct;
  gCtx.save(); gCtx.translate(cx, cy); gCtx.rotate(na);
  gCtx.beginPath(); gCtx.moveTo(0, 4); gCtx.lineTo(r - 14, 0); gCtx.lineTo(0, -4);
  gCtx.fillStyle = '#f0a020'; gCtx.shadowColor = '#f0a020'; gCtx.shadowBlur = 9; gCtx.fill();
  gCtx.restore(); gCtx.shadowBlur = 0;

  // moyeu
  gCtx.beginPath(); gCtx.arc(cx, cy, 7, 0, Math.PI * 2); gCtx.fillStyle = '#162230'; gCtx.fill();
  gCtx.beginPath(); gCtx.arc(cx, cy, 3, 0, Math.PI * 2); gCtx.fillStyle = '#f0a020'; gCtx.fill();
}

function updateGasUI(v) {
  const pct = v / 255;
  let col, status;
  if (pct < .33)      { col = '#20c060'; status = 'NOMINAL';    }
  else if (pct < .67) { col = '#e08020'; status = 'ATTENTION';  }
  else                { col = '#e03030'; status = 'CRITIQUE ⚠'; }

  document.getElementById('gas-val').style.color    = col;
  document.getElementById('gas-val').textContent    = Math.round(v);
  document.getElementById('gas-status').style.color = col;
  document.getElementById('gas-status').textContent = status;

  const bar = document.getElementById('gas-bar');
  bar.style.width      = (pct * 100) + '%';
  bar.style.background = col;
  bar.style.boxShadow  = pct > .33 ? `0 0 8px ${col}` : 'none';
}

(function loopGas() {
  const d = gTgt - gCur;
  if (Math.abs(d) > .2) { gCur += d * .12; drawGas(gCur); updateGasUI(gCur); }
  requestAnimationFrame(loopGas);
})();

/* ═══════════════════════════════════════════════════════════
   RADAR ARRIÈRE
   Clés API : arr_g_ext | arr_g_int | arr_d_int | arr_d_ext
═══════════════════════════════════════════════════════════ */
function rcol(v) {
  if (v < 64)  return '#e03030';
  if (v < 128) return '#e08020';
  if (v < 192) return '#c8c020';
  return '#1a2d3e';
}

function updateRadar(barId, valId, arcId, v) {
  const pct = (1 - v / 255) * 100;
  const col = rcol(v);

  const b = document.getElementById(barId);
  b.style.width      = pct + '%';
  b.style.background = col;
  b.style.boxShadow  = v < 128 ? `0 0 5px ${col}` : 'none';

  const ve = document.getElementById(valId);
  ve.textContent  = v;
  ve.style.color  = v < 192 ? col : 'var(--text)';

  const arc = document.getElementById(arcId);
  if (arc) {
    arc.setAttribute('stroke', col);
    arc.setAttribute('stroke-width', v < 64 ? '5.5' : v < 128 ? '4' : '3.5');
  }
}

/* ═══════════════════════════════════════════════════════════
   ÉCLAIRAGE
═══════════════════════════════════════════════════════════ */
function updateLight(id, stId, val, warn = false) {
  const el = document.getElementById(id);
  const st = document.getElementById(stId);
  el.classList.remove('on', 'onb', 'blink');
  if (val) {
    if (warn)              el.classList.add('blink');
    else if (id === 'li-high') el.classList.add('onb');
    else                   el.classList.add('on');
    st.textContent = warn ? 'WARNING' : 'ON';
  } else {
    st.textContent = 'OFF';
  }
}

function updateCarLights(l) {
  const tll = document.getElementById('tl-l');
  const tlr = document.getElementById('tl-r');
  if (tll) tll.setAttribute('fill', l.turn_left  ? '#8a2800' : '#1a0808');
  if (tlr) tlr.setAttribute('fill', l.turn_right ? '#8a2800' : '#1a0808');
}

/* ═══════════════════════════════════════════════════════════
   APPLICATION DE L'ÉTAT COMPLET
═══════════════════════════════════════════════════════════ */
function apply(s) {
  // Radar – clés renommées côté API
  updateRadar('bar-age', 'val-age', 'arc-age', s.radar.arr_g_ext);
  updateRadar('bar-agi', 'val-agi', 'arc-agi', s.radar.arr_g_int);
  updateRadar('bar-adi', 'val-adi', 'arc-adi', s.radar.arr_d_int);
  updateRadar('bar-ade', 'val-ade', 'arc-ade', s.radar.arr_d_ext);

  // Vitesse
  tgt = s.speed;

  // Gaz
  if (s.gas !== undefined) gTgt = s.gas;

  // Éclairage
  const l = s.lights, warn = l.turn_left && l.turn_right;
  updateLight('li-low',   'ls-low',   l.low_beam);
  updateLight('li-high',  'ls-high',  l.high_beam);
  updateLight('li-left',  'ls-left',  l.turn_left,  warn);
  updateLight('li-right', 'ls-right', l.turn_right, warn);
  updateCarLights(l);

  // AFU
  const ai = document.getElementById('afu-ring');
  const al = document.getElementById('afu-lbl');
  if (s.emergency_braking) {
    ai.classList.add('active'); al.classList.add('active');
  } else {
    ai.classList.remove('active'); al.classList.remove('active');
  }

  // Timestamp
  document.getElementById('last-update').textContent =
    new Date().toTimeString().slice(0, 8);
}

/* ═══════════════════════════════════════════════════════════
   POLLING
═══════════════════════════════════════════════════════════ */
let connOk = true;

async function poll() {
  try {
    const res = await fetch(`${API}/api/all`);
    apply(await res.json());
    if (!connOk) {
      const d = document.getElementById('conn-dot');
      d.style.background = 'var(--green)';
      d.style.boxShadow  = '0 0 7px var(--green)';
      connOk = true;
    }
  } catch {
    if (connOk) {
      const d = document.getElementById('conn-dot');
      d.style.background = 'var(--red)';
      d.style.boxShadow  = '0 0 7px var(--red)';
      connOk = false;
    }
  }
}

setInterval(poll, 300);

/* ═══════════════════════════════════════════════════════════
   SIMULATEUR
═══════════════════════════════════════════════════════════ */
function toggleSim() {
  const c = document.getElementById('sim-ctrl');
  c.classList.toggle('hidden');
  document.getElementById('sim-toggle').textContent =
    c.classList.contains('hidden') ? '⚙ SIM' : '✕ SIM';
}

async function post(url, body) {
  return fetch(`${API}${url}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
}

async function postRadar(sensor, v) { await post(`/api/radar/${sensor}`, { value: +v }); }
async function postSpeed(v)         { await post('/api/speed',           { value: +v }); }
async function postGas(v)           { await post('/api/gas',             { value: +v }); }

async function toggleLight(light, btnId) {
  lightState[light] = lightState[light] ? 0 : 1;
  document.getElementById(btnId).classList.toggle('on', !!lightState[light]);
  await post(`/api/lights/${light}`, { status: lightState[light] });
}

async function toggleWarning() {
  const on = !(lightState.turn_left && lightState.turn_right);
  lightState.turn_left = lightState.turn_right = on ? 1 : 0;
  ['btn-left', 'btn-right', 'btn-warn'].forEach(id =>
    document.getElementById(id).classList.toggle('on', on)
  );
  for (const l of ['turn_left', 'turn_right'])
    await post(`/api/lights/${l}`, { status: on ? 1 : 0 });
}

async function toggleAFU() {
  afuState = afuState ? 0 : 1;
  document.getElementById('btn-afu').classList.toggle('on-r', !!afuState);
  await post('/api/braking/emergency', { status: afuState });
}

const sl = ms => new Promise(r => setTimeout(r, ms));

async function runScenario() {
  for (let s = 0; s <= 70; s += 5) { await post('/api/speed', { value: s }); await sl(80); }
  await post('/api/lights/low_beam', { status: 1 }); await sl(400);
  await post('/api/lights/turn_left', { status: 1 }); await sl(1200);
  await post('/api/lights/turn_left', { status: 0 });
  for (let v = 255; v >= 20; v -= 18) {
    await post('/api/radar/arr_g_ext', { value: v });
    await post('/api/radar/arr_g_int', { value: v });
    await sl(70);
  }
  for (let g = 0; g <= 200; g += 12) { await post('/api/gas', { value: g }); await sl(55); }
  await post('/api/braking/emergency', { status: 1 });
  for (let s = 70; s >= 0; s -= 7) { await post('/api/speed', { value: s }); await sl(100); }
  await sl(800);
  await post('/api/braking/emergency', { status: 0 });
  await post('/api/lights/low_beam', { status: 0 });
  for (const sensor of ['arr_g_ext', 'arr_g_int'])
    await post(`/api/radar/${sensor}`, { value: 255 });
  for (let g = 200; g >= 0; g -= 18) { await post('/api/gas', { value: g }); await sl(45); }
}

/* ── Init ── */
drawSpeed(0);
drawGas(0);
updateGasUI(0);
poll();
