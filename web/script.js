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

// ── 通用：上传下一个的按钮HTML ────────────────────────────────

function getNextUploadHtml(buttonText, buttonId) {
  return `
    <div class="next-upload-bar" style="margin-top:16px;padding:12px;background:#f0f9ff;border-radius:8px;text-align:center">
      <button id="${buttonId}" class="btn-secondary">${buttonText}</button>
    </div>
  `;
}

// ── 通用：重置上传区域（清空预览、文件、画布，禁用按钮） ──────

function resetUpload(uploadConfig) {
  // uploadConfig: { b64Var, fileInputId, previewId, canvasId, placeholderId, btnId, resultId }
  if (uploadConfig.b64VarName) {
    // Clear the base64 variable (passed as string name in global scope)
    if (uploadConfig.b64VarName === 'trainB64') trainB64 = null;
    else if (uploadConfig.b64VarName === 'trainVideoB64') { trainVideoB64 = null; trainVideoMime = 'video/mp4'; }
    else if (uploadConfig.b64VarName === 'trainBatchB64') { trainBatchB64 = null; trainBatchMime = 'video/mp4'; }
    else if (uploadConfig.b64VarName === 'evalB64') { evalB64 = null; evalMime = 'image/jpeg'; }
    else if (uploadConfig.b64VarName === 'evalVideoB64') { evalVideoB64 = null; evalVideoMime = 'video/mp4'; }
  }
  // Clear file input
  const fileInput = document.getElementById(uploadConfig.fileInputId);
  if (fileInput) fileInput.value = '';
  
  // Hide preview
  const preview = document.getElementById(uploadConfig.previewId);
  if (preview) {
    preview.classList.add('hidden');
    preview.style.display = 'none';
    if (preview.tagName === 'VIDEO') {
      preview.pause();
      preview.removeAttribute('src');
      preview.removeAttribute('controls');
      preview.load();
    } else {
      preview.src = '';
      preview.srcset = '';
    }
  }
  
  // Hide canvas
  const canvas = document.getElementById(uploadConfig.canvasId);
  if (canvas) canvas.classList.add('hidden');
  
  // Show placeholder (remove hidden from the placeholder container itself)
  const placeholder = document.getElementById(uploadConfig.placeholderId);
  if (placeholder) {
    placeholder.classList.remove('hidden');
  }
  
  // Disable button
  const btn = document.getElementById(uploadConfig.btnId);
  if (btn) btn.disabled = true;
  
  // Hide result
  const result = document.getElementById(uploadConfig.resultId);
  if (result) result.classList.add('hidden');
}

// ── 图片上传通用逻辑 ──────────────────────────────────────────

function setupUpload(areaId, inputId, previewId, onFile) {
  const area    = document.getElementById(areaId);
  const input   = document.getElementById(inputId);
  const preview = document.getElementById(previewId);

  area.addEventListener('click', () => input.click());
  input.addEventListener('change', e => { if (e.target.files[0]) handle(e.target.files[0]); });
  area.addEventListener('dragenter', e => { 
    e.preventDefault(); 
    e.stopPropagation(); 
    area.classList.add('drag-over'); 
  });
  area.addEventListener('dragover', e => { 
    e.preventDefault(); 
    e.stopPropagation(); 
    area.classList.add('drag-over'); 
  });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault(); 
    e.stopPropagation(); 
    area.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) handle(e.dataTransfer.files[0]);
  });

  function handle(file) {
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.classList.remove('hidden');
      const placeholder = document.getElementById(areaId).querySelector('div');
      if (placeholder) placeholder.classList.add('hidden');
      
      // 如果是视频，阻止自动播放并添加控件
      if (preview.tagName === 'VIDEO') {
        preview.pause();
        preview.removeAttribute('autoplay');
        preview.setAttribute('controls', 'true');
        preview.style.display = 'block';
      } else {
        preview.style.display = 'inline-block';
      }
      
      onFile(e.target.result.split(',')[1], file.type || 'image/jpeg');
    };
    reader.onerror = (err) => {
      console.error('FileReader error:', err);
      alert('文件读取失败，请重试');
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
      </div>
      ${getNextUploadHtml('📷 上传下一张图片训练', 'train-next-btn')}`;
    resultEl.classList.remove('hidden');

    // 绑定"上传下一个"按钮
    document.getElementById('train-next-btn')?.addEventListener('click', () => {
      resetUpload({
        b64VarName: 'trainB64',
        fileInputId: 'train-img-input',
        previewId: 'train-preview',
        canvasId: 'train-canvas',
        placeholderId: 'train-placeholder',
        btnId: 'train-btn',
        resultId: 'train-result',
      });
    });
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`; errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('train-btn').disabled = false;
  }
});

// ── 视频训练模式 ──────────────────────────────────────────────

let trainVideoB64 = null, trainVideoMime = 'video/mp4';

setupUpload('train-video-upload', 'train-video-input', 'train-video-preview', (b64, mime) => {
  trainVideoB64 = b64;
  trainVideoMime = mime;
  document.getElementById('train-video-btn').disabled = false;
});

document.getElementById('train-video-btn').addEventListener('click', async () => {
  if (!trainVideoB64) return;
  
  const action = document.getElementById('train-video-action').value;
  const provider = document.getElementById('train-video-provider').value;
  const strategy = document.getElementById('train-video-strategy').value;
  const maxFrames = parseInt(document.getElementById('video-max-frames').value) || 30;
  const minInterval = parseFloat(document.getElementById('video-interval').value) || 0.5;
  
  const statusEl = document.getElementById('train-video-status');
  const errorEl  = document.getElementById('train-video-error');
  const resultEl = document.getElementById('train-video-result');
  
  statusEl.textContent = '正在分析视频并训练模板，请稍候（可能需要几十秒）...';
  statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  resultEl.classList.add('hidden');
  document.getElementById('train-video-btn').disabled = true;
  
  try {
    const resp = await fetch('/api/tennis-train-video', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        video: trainVideoB64,
        mime: trainVideoMime,
        action: action,
        provider: provider,
        max_frames: maxFrames,
        min_interval: minInterval,
        strategy: strategy,
      }),
    });
    
    const data = await resp.json();
    statusEl.classList.add('hidden');
    
    if (!data.ok) {
      errorEl.textContent = data.error;
      errorEl.classList.remove('hidden');
      return;
    }
    
    // 显示训练结果 + 上传下一个按钮
    resultEl.innerHTML = `
      <strong>✅ 视频训练完成！「${data.action}」模板已保存</strong>
      <div style="margin-top:12px;padding:12px;background:#f0f9ff;border-radius:6px">
        <div style="font-size:0.9rem;line-height:1.8">
          <div><strong>训练策略：</strong>${data.strategy}</div>
          <div><strong>检测方案：</strong>${data.provider} ${data.use_3d ? '(3D模式)' : '(2D模式)'}</div>
          <div><strong>视频处理：</strong>共${data.total_frames}帧，成功分析${data.analyzed_frames}帧，失败${data.failed_frames}帧</div>
          <div><strong>使用帧：</strong>${data.used_frame_timestamp}秒（得分：${data.used_frame_score}）</div>
          <div><strong>模板样本：</strong>累计 ${data.sample_count} 张样本</div>
        </div>
      </div>
      <div class="angle-grid" style="margin-top:12px">
        ${Object.entries(data.angles).map(([k, v]) =>
          `<div class="angle-chip"><div class="name">${k}</div><div class="val">${v}°</div></div>`
        ).join('')}
      </div>
      ${getNextUploadHtml('🎬 上传下一个视频训练', 'train-video-next-btn')}`;
    resultEl.classList.remove('hidden');

    // 绑定"上传下一个"按钮
    document.getElementById('train-video-next-btn')?.addEventListener('click', () => {
      resetUpload({
        b64VarName: 'trainVideoB64',
        fileInputId: 'train-video-input',
        previewId: 'train-video-preview',
        canvasId: null,
        placeholderId: 'train-video-placeholder',
        btnId: 'train-video-btn',
        resultId: 'train-video-result',
      });
    });
    
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`;
    errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('train-video-btn').disabled = false;
  }
});

// ── 批量视频训练模式 ──────────────────────────────────────────

let trainBatchB64 = null, trainBatchMime = 'video/mp4';

setupUpload('train-batch-upload', 'train-batch-input', 'train-batch-preview', (b64, mime) => {
  trainBatchB64 = b64;
  trainBatchMime = mime;
  document.getElementById('train-batch-btn').disabled = false;
});

document.getElementById('train-batch-btn').addEventListener('click', async () => {
  if (!trainBatchB64) return;
  
  // 获取选中的动作
  const checkboxes = document.querySelectorAll('.batch-action-checkbox:checked');
  const actions = Array.from(checkboxes).map(cb => cb.value);
  
  if (actions.length === 0) {
    alert('请至少选择一个动作类型');
    return;
  }
  
  const provider = document.getElementById('train-batch-provider').value;
  const strategy = document.getElementById('train-batch-strategy').value;
  const maxFrames = parseInt(document.getElementById('video-max-frames').value) || 30;
  const minInterval = parseFloat(document.getElementById('video-interval').value) || 0.5;
  
  const statusEl = document.getElementById('train-batch-status');
  const errorEl  = document.getElementById('train-batch-error');
  const resultEl = document.getElementById('train-batch-result');
  
  statusEl.textContent = `正在批量训练 ${actions.length} 个动作模板，请稍候（可能需要1-2分钟）...`;
  statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  resultEl.classList.add('hidden');
  document.getElementById('train-batch-btn').disabled = true;
  
    try {
    console.log('发送批量训练请求...', {actions, provider, strategy});
    const resp = await fetch('/api/tennis-train-video-batch', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        video: trainBatchB64,
        mime: trainBatchMime,
        actions: actions,
        provider: provider,
        max_frames: maxFrames,
        min_interval: minInterval,
        strategy: strategy,
      }),
    });
    
    console.log('响应状态:', resp.status, resp.statusText);
    
    if (!resp.ok) {
      throw new Error(`HTTP错误: ${resp.status} ${resp.statusText}`);
    }
    
    const data = await resp.json();
    console.log('响应数据:', data);
    statusEl.classList.add('hidden');
    
    if (!data.ok) {
      errorEl.textContent = data.error;
      errorEl.classList.remove('hidden');
      return;
    }
    
    // 显示批量训练结果
    let resultsHtml = `
      <strong>✅ 批量训练完成！成功训练 ${data.successful_actions}/${data.total_actions} 个动作模板</strong>
      <div style="margin-top:12px;padding:12px;background:#f0f9ff;border-radius:6px">
        <div style="font-size:0.9rem;line-height:1.8">
          <div><strong>检测方案：</strong>${data.provider} ${data.use_3d ? '(3D模式)' : '(2D模式)'}</div>
          <div><strong>视频处理：</strong>共${data.total_frames}帧，成功分析${data.analyzed_frames}帧</div>
          <div><strong>训练策略：</strong>${strategy === 'all' ? '多帧平均' : strategy === 'best' ? '最佳帧' : '第一帧'}</div>
        </div>
      </div>
    `;
    
    // 显示每个动作的结果
    if (data.results && data.results.length > 0) {
      resultsHtml += '<div style="margin-top:16px">';
      data.results.forEach((result, index) => {
        resultsHtml += `
          <div style="margin-top:12px;padding:12px;background:#f9fafb;border-radius:6px;border-left:3px solid #3b82f6">
            <div style="font-weight:600;margin-bottom:8px">${index + 1}. ${result.action}</div>
            <div style="font-size:0.85rem;color:#666;margin-bottom:8px">
              策略：${result.strategy} | 样本数：${result.sample_count}
            </div>
            <div class="angle-grid">
              ${Object.entries(result.angles).map(([k, v]) =>
                `<div class="angle-chip"><div class="name">${k}</div><div class="val">${v}°</div></div>`
              ).join('')}
            </div>
          </div>
        `;
      });
      resultsHtml += '</div>';
    }
    
    // 添加上传下一个按钮
    resultsHtml += getNextUploadHtml('🎬 上传下一个视频批量训练', 'train-batch-next-btn');
    
    resultEl.innerHTML = resultsHtml;
    resultEl.classList.remove('hidden');

    // 绑定"上传下一个"按钮
    document.getElementById('train-batch-next-btn')?.addEventListener('click', () => {
      resetUpload({
        b64VarName: 'trainBatchB64',
        fileInputId: 'train-batch-input',
        previewId: 'train-batch-preview',
        canvasId: null,
        placeholderId: 'train-batch-placeholder',
        btnId: 'train-batch-btn',
        resultId: 'train-batch-result',
      });
    });
    
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`;
    errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('train-batch-btn').disabled = false;
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
    const cameraAngle = document.getElementById('eval-camera-angle').value;
    const actionType = document.getElementById('eval-action-type').value;
    const provider = document.getElementById('eval-provider').value;
    const resp = await fetch('/api/tennis-evaluate', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ 
        image: evalB64, 
        mime: evalMime, 
        player: document.getElementById('eval-player').value,
        camera_angle: cameraAngle,
        action_type: actionType,
        provider: provider,
      }),
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

    const addToTemplateHtml = `
      <div style="margin-top:16px;padding:12px;background:#f0fdf4;border-radius:8px;border:2px dashed #22c55e">
        <div style="font-weight:600;margin-bottom:8px;color:#166534">💡 将此动作添加到训练模板？</div>
        <p style="font-size:0.85rem;color:#15803d;margin-bottom:12px">
          当前识别为「${r['动作']}」，可将此样本添加到标准模板库中
        </p>
        <button id="add-to-template-btn" class="btn-primary" style="background:#22c55e;border-color:#22c55e">
          ✓ 添加到训练模板
        </button>
        <span id="add-template-status" style="margin-left:12px;font-size:0.85rem"></span>
      </div>
    `;

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
      ${vlHtml}
      ${addToTemplateHtml}
      ${getNextUploadHtml('🎾 上传下一张图片评估', 'eval-next-btn')}`;
    reportEl.classList.remove('hidden');

    // 绑定添加到模板按钮事件
    document.getElementById('add-to-template-btn')?.addEventListener('click', async () => {
      const statusEl = document.getElementById('add-template-status');
      const btn = document.getElementById('add-to-template-btn');
      btn.disabled = true;
      statusEl.textContent = '正在添加...';
      statusEl.style.color = '#15803d';

      try {
        const resp = await fetch('/api/tennis-train', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            image: evalB64,
            action: r['动作'],
            provider: provider,
          }),
        });
        const data = await resp.json();
        if (data.ok) {
          statusEl.textContent = `✅ 添加成功！（累计 ${data.sample_count} 张样本）`;
          statusEl.style.color = '#166534';
          btn.textContent = '✓ 已添加';
          btn.disabled = true;
        } else {
          statusEl.textContent = `❌ 添加失败：${data.error}`;
          statusEl.style.color = '#dc2626';
          btn.disabled = false;
        }
      } catch(e) {
        statusEl.textContent = `❌ 请求失败：${e.message}`;
        statusEl.style.color = '#dc2626';
        btn.disabled = false;
      }
    });

    // 绑定"上传下一个"按钮
    document.getElementById('eval-next-btn')?.addEventListener('click', () => {
      resetUpload({
        b64VarName: 'evalB64',
        fileInputId: 'eval-img-input',
        previewId: 'eval-preview',
        canvasId: 'eval-canvas',
        placeholderId: 'eval-placeholder',
        btnId: 'eval-btn',
        resultId: 'eval-report',
      });
    });
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`; errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('eval-btn').disabled = false;
  }
});

// ── 视频评估模式 ──────────────────────────────────────────────

let evalVideoB64 = null, evalVideoMime = 'video/mp4';

setupUpload('eval-video-upload', 'eval-video-input', 'eval-video-preview', (b64, mime) => {
  evalVideoB64 = b64; evalVideoMime = mime;
  document.getElementById('eval-video-btn').disabled = false;
});

document.getElementById('eval-video-btn').addEventListener('click', async () => {
  if (!evalVideoB64) return;
  
  const statusEl = document.getElementById('eval-video-status');
  const errorEl  = document.getElementById('eval-video-error');
  const resultEl = document.getElementById('eval-video-result');
  
  const provider = document.getElementById('eval-provider').value;
  const cameraAngle = document.getElementById('eval-video-camera-angle').value;
  
  // 获取选中的动作类型（可多选）
  const actionCheckboxes = document.querySelectorAll('.eval-video-action-checkbox:checked');
  const actionTypes = Array.from(actionCheckboxes).map(cb => cb.value);
  
  const maxFrames = parseInt(document.getElementById('eval-video-max-frames').value) || 20;
  const minInterval = parseFloat(document.getElementById('eval-video-interval').value) || 1.0;
  
  statusEl.textContent = '正在分析视频，请稍候（可能需要几十秒）...';
  statusEl.classList.remove('hidden');
  errorEl.classList.add('hidden');
  resultEl.classList.add('hidden');
  document.getElementById('eval-video-btn').disabled = true;
  
  try {
    const resp = await fetch('/api/tennis-video', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        video: evalVideoB64,
        mime: evalVideoMime,
        provider: provider,
        camera_angle: cameraAngle,
        action_types: actionTypes,
        max_frames: maxFrames,
        min_interval: minInterval,
      }),
    });
    
    const data = await resp.json();
    statusEl.classList.add('hidden');
    
    if (!data.ok) {
      errorEl.textContent = data.error;
      errorEl.classList.remove('hidden');
      return;
    }
    
    // 显示分析结果 + 上传下一个按钮（在结果区域下方）
    renderEvalVideoReport(data.analysis, data.report, data.vl_analysis);
    
    // 添加上传下一个按钮
    const nextBtnContainer = document.createElement('div');
    nextBtnContainer.innerHTML = getNextUploadHtml('🎬 上传下一个视频评估', 'eval-video-next-btn');
    document.getElementById('eval-video-summary').appendChild(nextBtnContainer.firstElementChild);
    
    document.getElementById('eval-video-next-btn')?.addEventListener('click', () => {
      resetUpload({
        b64VarName: 'evalVideoB64',
        fileInputId: 'eval-video-input',
        previewId: 'eval-video-preview',
        canvasId: null,
        placeholderId: 'eval-video-placeholder',
        btnId: 'eval-video-btn',
        resultId: 'eval-video-result',
      });
    });
    
    resultEl.classList.remove('hidden');
    
  } catch(e) {
    statusEl.classList.add('hidden');
    errorEl.textContent = `请求失败：${e.message}`;
    errorEl.classList.remove('hidden');
  } finally {
    document.getElementById('eval-video-btn').disabled = false;
  }
});

function renderEvalVideoReport(analysis, reportText, vlAnalysis) {
  const summaryEl = document.getElementById('eval-video-summary');
  const framesEl = document.getElementById('eval-video-frames-list');
  
  const summary = analysis.summary;
  
  // 总结部分
  let summaryHtml = `
    <div class="score-banner" style="margin-bottom:20px">
      <div class="score-circle ${summary.average_score >= 80 ? 'good' : summary.average_score >= 60 ? 'ok' : 'poor'}" 
           style="width:80px;height:80px;font-size:1.8rem">
        ${summary.average_score}
      </div>
      <div class="score-info">
        <h3>视频分析总结</h3>
        <p>平均得分：${summary.average_score}分</p>
        <p>成功分析：${analysis.analyzed_frames} / ${analysis.total_frames} 帧</p>
      </div>
    </div>
  `;
  
  // 检测到的动作
  if (summary.actions_detected && Object.keys(summary.actions_detected).length > 0) {
    summaryHtml += '<h4 style="margin-top:20px">检测到的动作</h4><div style="display:flex;gap:8px;flex-wrap:wrap">';
    for (const [action, count] of Object.entries(summary.actions_detected)) {
      summaryHtml += `<span class="angle-chip">${action}: ${count}次</span>`;
    }
    summaryHtml += '</div>';
  }
  
  // 最常见问题
  if (summary.common_issues && Object.keys(summary.common_issues).length > 0) {
    summaryHtml += '<h4 style="margin-top:20px">最常见问题</h4><div style="display:flex;gap:8px;flex-wrap:wrap">';
    for (const [issue, count] of Object.entries(summary.common_issues)) {
      summaryHtml += `<span class="angle-chip" style="background:#fef3c7">${issue}: ${count}次</span>`;
    }
    summaryHtml += '</div>';
  }
  
  // 最佳/最差帧
  if (summary.best_frame) {
    const best = summary.best_frame;
    summaryHtml += `
      <div style="margin-top:20px;padding:12px;background:#dcfce7;border-radius:8px">
        <strong>🏆 最佳动作帧</strong> 
        时间点: ${best.timestamp}秒 | 得分: ${best.score} | 动作: ${best.action || '未知'}
      </div>
    `;
  }
  
  if (summary.worst_frame && summary.worst_frame.score !== null) {
    const worst = summary.worst_frame;
    summaryHtml += `
      <div style="margin-top:10px;padding:12px;background:#fee2e2;border-radius:8px">
        <strong>⚠️ 最需改进帧</strong> 
        时间点: ${worst.timestamp}秒 | 得分: ${worst.score} | 动作: ${worst.action || '未知'}
        ${worst.issues && worst.issues.length > 0 ? `<div style="margin-top:8px;font-size:0.9rem">
          问题: ${worst.issues.slice(0, 3).map(i => `${i['角度名称']}${i['方向']}`).join('、')}
        </div>` : ''}
      </div>
    `;
  }
  
  // VL语义分析
  if (vlAnalysis) {
    summaryHtml += `
      <div style="margin-top:20px;padding:16px;background:#f0f9ff;border-radius:8px;border-left:4px solid #3b82f6">
        <div style="font-weight:600;margin-bottom:12px;font-size:1.1rem">🤖 通义千问 VL 语义分析（最佳帧）</div>
        <div style="white-space:pre-wrap;font-size:0.9rem;line-height:1.8">${vlAnalysis}</div>
      </div>
    `;
  }
  
  // 文字报告
  summaryHtml += `
    <div style="margin-top:20px;padding:16px;background:#f9fafb;border-radius:8px">
      <h4 style="margin-top:0">详细报告</h4>
      <pre style="white-space:pre-wrap;font-family:monospace;font-size:0.85rem;line-height:1.6">${reportText}</pre>
    </div>
  `;
  
  summaryEl.innerHTML = summaryHtml;
  
  // 逐帧结果（只显示有问题的帧）
  const problemFrames = analysis.frames.filter(f => f.success && f.issues && f.issues.length > 0);
  
  if (problemFrames.length > 0) {
    let framesHtml = '<h4 style="margin-top:30px">问题帧详情（前10帧）</h4>';
    
    problemFrames.slice(0, 10).forEach(frame => {
      framesHtml += `
        <div style="margin-top:12px;padding:12px;border:1px solid #e5e7eb;border-radius:8px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <strong>⏱️ ${frame.timestamp}秒</strong>
            <span class="score-badge ${frame.score >= 80 ? 'good' : frame.score >= 60 ? 'ok' : 'poor'}">${frame.score}分</span>
          </div>
          <div style="font-size:0.85rem;color:#666;margin-bottom:8px">
            动作: ${frame.action || '未知'}
          </div>
          <div style="display:flex;gap:6px;flex-wrap:wrap">
            ${frame.issues.map(iss => `
              <span class="angle-chip" style="background:#fee2e2">
                ${iss['角度名称']} ${iss['方向']} ${iss['偏差'] > 0 ? '+' : ''}${iss['偏差']}°
              </span>
            `).join('')}
          </div>
        </div>
      `;
    });
    
    framesEl.innerHTML = framesHtml;
  } else {
    framesEl.innerHTML = '<p style="margin-top:20px;color:#16a34a">✅ 所有帧的动作都很规范！</p>';
  }
}

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
    document.getElementById('panel-history').classList.toggle('hidden',   mode !== 'history');
    if (mode === 'templates') loadTemplates();
    if (mode === 'history')   initHistoryPanel();
  });
});

// ── 进步曲线 ──────────────────────────────────────────────────

let historyChart = null;

async function initHistoryPanel() {
  const select = document.getElementById('history-player-select');
  try {
    const resp = await fetch('/api/history-players');
    const data = await resp.json();
    const current = select.value;
    select.innerHTML = '<option value="">全部学员</option>';
    (data.players || []).forEach(p => {
      const opt = document.createElement('option');
      opt.value = opt.textContent = p;
      select.appendChild(opt);
    });
    if (current) select.value = current;
  } catch(e) {}
  await loadHistory();
}

async function loadHistory() {
  const player = document.getElementById('history-player-select').value;
  const url = '/api/history-records' + (player ? `?player=${encodeURIComponent(player)}` : '');
  try {
    const resp = await fetch(url);
    const data = await resp.json();
    const records = data.records || [];

    const chartWrap = document.getElementById('history-chart-wrap');
    const tableWrap = document.getElementById('history-table-wrap');
    const emptyEl   = document.getElementById('history-empty');

    if (!records.length) {
      chartWrap.classList.add('hidden');
      tableWrap.classList.add('hidden');
      emptyEl.classList.remove('hidden');
      return;
    }
    emptyEl.classList.add('hidden');
    chartWrap.classList.remove('hidden');
    tableWrap.classList.remove('hidden');

    // 曲线图
    const labels = records.map(r => r.time.slice(5, 16));  // MM-DD HH:mm
    const scores = records.map(r => r.score);

    if (historyChart) historyChart.destroy();
    const ctx = document.getElementById('history-chart').getContext('2d');
    historyChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: '得分',
          data: scores,
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37,99,235,0.08)',
          pointBackgroundColor: scores.map(s => s >= 80 ? '#16a34a' : s >= 60 ? '#d97706' : '#dc2626'),
          pointRadius: 5,
          tension: 0.3,
          fill: true,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              afterBody: (items) => {
                const r = records[items[0].dataIndex];
                return [`动作：${r.action}`, `问题数：${r.issue_count}`, `置信度：${r.confidence}%`];
              },
            },
          },
        },
        scales: {
          y: { min: 0, max: 100, title: { display: true, text: '得分' } },
          x: { ticks: { maxRotation: 45 } },
        },
      },
    });

    // 明细表格
    const tbody = document.querySelector('#history-table tbody');
    tbody.innerHTML = [...records].reverse().map(r => {
      const scoreClass = r.score >= 80 ? 'good' : r.score >= 60 ? 'ok' : 'poor';
      return `<tr>
        <td>${r.time}</td>
        <td>${r.player}</td>
        <td>${r.action}</td>
        <td><span class="score-badge ${scoreClass}">${r.score}</span></td>
        <td>${r.issue_count}</td>
        <td>${r.confidence}%</td>
      </tr>`;
    }).join('');
  } catch(e) {
    document.getElementById('history-empty').textContent = `加载失败：${e.message}`;
    document.getElementById('history-empty').classList.remove('hidden');
  }
}

document.getElementById('history-load-btn').addEventListener('click', loadHistory);

document.getElementById('history-clear-btn').addEventListener('click', async () => {
  const player = document.getElementById('history-player-select').value;
  const msg = player ? `确定清空「${player}」的所有记录吗？` : '确定清空所有学员的历史记录吗？';
  if (!confirm(msg)) return;
  await fetch('/api/history-clear', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({player}),
  });
  await initHistoryPanel();
});