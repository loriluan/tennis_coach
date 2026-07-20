// ── 骨骼连线定义（百度17点） ──────────────────────────────────
const SKELETON = [
  ['top_head',       'neck'],
  ['neck',           'left_shoulder'],
  ['neck',           'right_shoulder'],
  ['left_shoulder',  'left_elbow'],
  ['left_elbow',     'left_wrist'],
  ['right_shoulder', 'right_elbow'],
  ['right_elbow',    'right_wrist'],
  ['neck',           'pelvis'],
  ['pelvis',         'left_hip'],
  ['pelvis',         'right_hip'],
  ['left_hip',       'left_knee'],
  ['left_knee',      'left_ankle'],
  ['right_hip',      'right_knee'],
  ['right_knee',     'right_ankle'],
];

const PART_COLOR = {
  arm:  '#3b82f6',
  leg:  '#22c55e',
  body: '#f59e0b',
};

// ── Canvas 骨骼绘制 ───────────────────────────────────────────

function drawSkeleton(canvas, imgEl, parts) {
  const img = imgEl;
  canvas.width  = img.naturalWidth  || img.width;
  canvas.height = img.naturalHeight || img.height;
  canvas.classList.remove('hidden');
  const ctx = canvas.getContext('2d');
  ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

  // 连线
  ctx.lineWidth = 3;
  SKELETON.forEach(([a, b]) => {
    const pa = parts[a], pb = parts[b];
    if (!pa || !pb || pa.score < 0.3 || pb.score < 0.3) return;
    ctx.strokeStyle = '#facc15';
    ctx.beginPath();
    ctx.moveTo(pa.x, pa.y);
    ctx.lineTo(pb.x, pb.y);
    ctx.stroke();
  });

  // 关键点
  Object.values(parts).forEach(p => {
    if (p.score < 0.3) return;
    ctx.beginPath();
    ctx.arc(p.x, p.y, 5, 0, Math.PI * 2);
    ctx.fillStyle = '#ef4444';
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  });
}

// ── 图片上传通用逻辑 ──────────────────────────────────────────

function setupUpload(areaId, inputId, previewId, onFile) {
  const area    = document.getElementById(areaId);
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  area.addEventListener('click', () => input.click());
  input.addEventListener('change', e => { if (e.target.files[0]) handle(e.target.files[0]); });
  area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault(); area.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]);
  });

  function handle(file) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.classList.remove('hidden');
      document.getElementById(areaId).querySelector('div')?.classList.add('hidden');
      onFile(e.target.result.split(',')[1], file.type || 'image/jpeg');
    };
    reader.readAsDataURL(file);
  }
}

// ── 训练模式 ──────────────────────────────────────────────────

let trainB64 = null;

setupUpload('train-upload', 'train-img-input', 'train-preview', (b64) => {
  trainB64 = b64;
  document.getElementById('train-btn').disabled = false;
});

document.getElementById('train-btn').addEventListener('click', async () => {
  if (!trainB64) return;
  const action = document.getElementById('train-action').value;
  const statusEl = document.getElementById('train-status');
  const errorEl  = document.getElementById('train-error');
  const resultEl = document.getElementById('train-result');
  statusEl.textContent = '正在提取关键点...'; statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden'); resultEl.classList.add('hidden');
  document.getElementById('train-btn').disabled = true;

  try {
    // 先画骨骼图
    const kpResp = await fetch('/api/tennis-keypoint', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image: trainB64}),
    });
    const kpData = await kpResp.json();
    if (kpData.ok && kpData.persons?.[0]) {
      drawSkeleton(
        document.getElementById('train-canvas'),
        document.getElementById('train-preview'),
        kpData.persons[0]
      );
    }

    statusEl.textContent = '正在保存标准模板...';
    const resp = await fetch('/api/tennis-train', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image: trainB64, action}),
    });
    const data = await resp.json();
    statusEl.classList.add('hidden');
    if (!data.ok) { errorEl.textContent = data.error; errorEl.classList.remove('hidden'); return; }

    resultEl.innerHTML = `
      <strong>✅ 「${data.action}」模板已保存（累计 ${data.sample_count} 张样本）</strong>
      <div class="angle-grid">
        ${Object.entries(data.angles).map(([k, v]) =>
          `<div class="angle-chip"><div class="name">${k}</div><div class="val">${v}°</div></div>`
        ).join('')}
      </div>`;
    resultEl.classList.remove('hidden');
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`; errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('train-btn').disabled = false;
  }
});

// ── 评估模式 ──────────────────────────────────────────────────

let evalB64 = null;
let evalMime = 'image/jpeg';

setupUpload('eval-upload', 'eval-img-input', 'eval-preview', (b64, mime) => {
  evalB64 = b64;
  evalMime = mime;
  document.getElementById('eval-btn').disabled = false;
});

document.getElementById('eval-btn').addEventListener('click', async () => {
  if (!evalB64) return;
  const statusEl = document.getElementById('eval-status');
  const errorEl  = document.getElementById('eval-error');
  const reportEl = document.getElementById('eval-report');
  statusEl.textContent = 'AI 识别动作阶段中，请稍候...'; statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden'); reportEl.classList.add('hidden');
  document.getElementById('eval-btn').disabled = true;

  try {
    const resp = await fetch('/api/tennis-evaluate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image: evalB64, mime: evalMime}),
    });
    const data = await resp.json();
    statusEl.classList.add('hidden');
    if (!data.ok) { errorEl.textContent = data.error; errorEl.classList.remove('hidden'); return; }

    if (data.keypoints) {
      drawSkeleton(
        document.getElementById('eval-canvas'),
        document.getElementById('eval-preview'),
        data.keypoints
      );
    }

    const r = data.report;
    const scoreClass = r['得分'] >= 80 ? 'good' : r['得分'] >= 60 ? 'ok' : 'poor';
    const issuesHtml = r['问题列表'].length === 0
      ? '<div class="issue-item ok"><div class="issue-advice">✅ 所有关键角度均在标准范围内，动作规范！</div></div>'
      : r['问题列表'].map(iss => `
          <div class="issue-item">
            <div class="issue-header">
              <span class="issue-name">⚠️ ${iss['角度名称']}  ${iss['方向']}</span>
              <span class="issue-vals">标准 ${iss['标准值']}° → 实际 ${iss['实际值']}°（偏差 ${iss['偏差'] > 0 ? '+' : ''}${iss['偏差']}°）</span>
            </div>
            <div class="issue-advice">${iss['建议']}</div>
          </div>`).join('');

    const vlHtml = r['VL语义分析']
      ? `<div class="vl-block">
          <div class="vl-title">🤖 通义千问 VL 语义分析</div>
          <div class="vl-content">${r['VL语义分析'].replace(/\n/g, '<br>')}</div>
        </div>`
      : '';

    reportEl.innerHTML = `
      <div class="score-banner">
        <div class="score-circle ${scoreClass}">${r['得分']}</div>
        <div class="score-info">
          <h3>自动识别：${r['动作']}</h3>
          <p>匹配置信度 ${r['识别置信度']}%</p>
          <p>${r['总结']}</p>
        </div>
      </div>
      <div class="issues-list">${issuesHtml}</div>
      ${vlHtml}`;
    reportEl.classList.remove('hidden');
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`; errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('eval-btn').disabled = false;
  }
});

// ── 已训练动作面板 ────────────────────────────────────────────

async function loadTemplates() {
  const el = document.getElementById('templates-list');
  try {
    const resp = await fetch('/api/tennis-templates');
    const data = await resp.json();
    if (!data.ok || !Object.keys(data.templates).length) {
      el.innerHTML = '<p class="no-template">还没有训练任何动作，请先在训练模式中上传标准照片。</p>';
      return;
    }
    el.innerHTML = Object.entries(data.templates).map(([action, info]) => `
      <div class="template-card">
        <h3>${action}</h3>
        <p>已录入 ${info.sample_count} 张样本 · 覆盖角度：${info.angles.join('、')}</p>
      </div>`).join('');
  } catch(e) {
    el.innerHTML = `<p class="error">加载失败：${e.message}</p>`;
  }
}

// ── Compare mode ──────────────────────────────────────────────

let compareB64 = null, compareMime = 'image/jpeg';

setupUpload('compare-upload', 'compare-img-input', 'compare-preview', (b64, mime) => {
  compareB64 = b64; compareMime = mime;
  document.getElementById('compare-btn').disabled = false;
});

function renderCompareReport(containerId, canvasId, previewId, data) {
  const el = document.getElementById(containerId);
  if (!data.ok) {
    el.innerHTML = `<p class="error">${data.error}</p>`;
    return;
  }
  const r = data.report;
  if (data.keypoints) {
    drawSkeleton(document.getElementById(canvasId),
                 document.getElementById(previewId), data.keypoints);
  }
  const scoreClass = r['得分'] >= 80 ? 'good' : r['得分'] >= 60 ? 'ok' : 'poor';
  const issuesHtml = r['问题列表'].length === 0
    ? '<div class="issue-item ok"><div class="issue-advice">✅ 动作规范！</div></div>'
    : r['问题列表'].map(iss => `
        <div class="issue-item">
          <div class="issue-header">
            <span class="issue-name">⚠️ ${iss['角度名称']} ${iss['方向']}</span>
            <span class="issue-vals">标准${iss['标准值']}° → 实际${iss['实际值']}°</span>
          </div>
          <div class="issue-advice">${iss['建议']}</div>
        </div>`).join('');
  el.innerHTML = `
    <div class="score-banner" style="margin-bottom:10px">
      <div class="score-circle ${scoreClass}" style="width:50px;height:50px;font-size:1.1rem">${r['得分']}</div>
      <div class="score-info">
        <h3 style="font-size:.9rem">${r['动作']}</h3>
        <p style="font-size:.8rem">置信度 ${r['识别置信度']}%</p>
        <p style="font-size:.8rem">${r['总结']}</p>
      </div>
    </div>
    <div class="issues-list">${issuesHtml}</div>`;

  // 角度对比表
  const angles = r['学员角度'];
  const std    = r['标准角度'];
  const rows = Object.entries(angles).map(([k, v]) => {
    const s = std[k] ?? '-';
    const diff = s !== '-' ? (v - s).toFixed(1) : '-';
    const color = diff !== '-' && Math.abs(diff) > 20 ? '#dc2626' : '#16a34a';
    return `<tr>
      <td>${k}</td><td>${v}°</td><td>${s}°</td>
      <td style="color:${color};font-weight:600">${diff !== '-' ? (diff > 0 ? '+' : '') + diff + '°' : '-'}</td>
    </tr>`;
  }).join('');
  el.innerHTML += `
    <table style="width:100%;font-size:.78rem;margin-top:10px;border-collapse:collapse">
      <thead><tr style="background:#f9fafb">
        <th style="padding:5px 8px;text-align:left">角度</th>
        <th>实测</th><th>标准</th><th>偏差</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

document.getElementById('compare-btn').addEventListener('click', async () => {
  if (!compareB64) return;
  const statusEl = document.getElementById('compare-status');
  const errorEl  = document.getElementById('compare-error');
  statusEl.textContent = '正在同时调用两种方案，请稍候（MediaPipe 首次运行较慢）...';
  statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  document.getElementById('compare-result').classList.add('hidden');
  document.getElementById('compare-btn').disabled = true;

  try {
    const resp = await fetch('/api/tennis-compare', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({image: compareB64, mime: compareMime}),
    });
    const data = await resp.json();
    statusEl.classList.add('hidden');
    if (!data.ok) { errorEl.textContent = data.error; errorEl.classList.remove('hidden'); return; }

    document.getElementById('compare-result').classList.remove('hidden');
    renderCompareReport('baidu-report', 'baidu-canvas', 'compare-preview', data.results.baidu);
    renderCompareReport('mp-report',    'mp-canvas',    'compare-preview', data.results.mediapipe);
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`; errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('compare-btn').disabled = false;
  }
});

// ── 模式切换 ──────────────────────────────────────────────────

document.querySelectorAll('.mode-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.mode-tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    const mode = tab.dataset.mode;
    document.getElementById('panel-train').classList.toggle('hidden',     mode !== 'train');
    document.getElementById('panel-eval').classList.toggle('hidden',      mode !== 'eval');
    document.getElementById('panel-compare').classList.toggle('hidden',   mode !== 'compare');
    document.getElementById('panel-templates').classList.toggle('hidden', mode !== 'templates');
    if (mode === 'templates') loadTemplates();
  });
});
