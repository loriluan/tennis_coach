const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        AlignmentType, HeadingLevel, LevelFormat, BorderStyle, WidthType,
        ShadingType, VerticalAlign, PageBreak } = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: 'CCCCCC' };
const cb = { top: border, bottom: border, left: border, right: border };
const cs = (fill) => ({ fill, type: ShadingType.CLEAR });

const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 180 }, children: [new TextRun({ text, bold: true })] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 240, after: 120 }, children: [new TextRun({ text, bold: true })] });
const p  = (text) => new Paragraph({ spacing: { before: 80, after: 80 }, children: [new TextRun(text)] });
const pb = () => new Paragraph({ children: [new PageBreak()] });
const bl = (text, ref) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { before: 60, after: 60 }, children: [new TextRun(text)] });

const numConfig = ['b1','b2','b3','b4','b5'].map(ref => ({
  reference: ref,
  levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 560, hanging: 280 } } } }]
}));

const days = [
  {
    title: '第零天（课题准备日）— 跟随老师代码示例，学习 AI 应用开发基础',
    ref: 'b1',
    plan: [
      '阅读老师提供的 Python 示例代码，理解 AI API 调用的基本模式',
      '实践：完成车辆检测程序（vehicle_detector）',
      '实践：完成人脸识别程序（baidu_ai/face_recognition）',
      '实践：完成语言学习 Agent（AILearning/src/demo1）',
      '总结各程序的共性规律，思考能否迁移到体育动作分析场景',
    ],
    records: [
      '在老师提供的 Python 代码框架基础上，完成三个练习程序，初步掌握 AI API 调用的基本开发模式。',
      'vehicle_detector：调用通义千问 qwen-vl-max，输入路口照片，识别南北/东西方向车辆数量，配套实现 HTTP 服务接口。理解了多模态"图片+Prompt"输入方式及结构化输出解析。',
      'baidu_ai/face_recognition：基于百度 AIP SDK，实现人脸注册、单人识别、合照群体识别三个功能，结果持久化存储。',
      '语言学习 Agent（demo1）：基于 LLM 实现自适应出题模式，根据上一题作答情况动态调整难度，3-4 题后给出综合评估，支持通义千问和 OpenAI 双 provider。',
      '总结：三个程序的共同结构是"输入→调用AI→解析输出→结构化结果"，与体育动作分析高度吻合，由此萌生了做网球动作智能教练的想法。',
    ],
    commits: [
      ['全天', 'vehicle_detector', 'detector.py + server.py，qwen-vl-max车辆计数'],
      ['全天', 'baidu_ai/face_recognition', '人脸注册/识别/合照群体识别'],
      ['全天', 'AILearning/src/demo1', '语言学习Agent + 自适应评估模式'],
    ]
  },
  {
    title: '第一天（7月20日）— 选题构思与项目初始化',
    ref: 'b1',
    plan: [
      '从体育动作打分的通用框架出发，确定以网球作为切入场景',
      '规划项目目录结构，搭建 HTTP 服务器骨架',
      '接入百度人体分析 API 完成关键点检测',
      '实现关节角度计算基础版（向量点积法）',
      '搭建前端页面雏形，支持图片上传与结果展示',
    ],
    records: [
      '选题思考：人体姿态估计技术已在篮球、体操等运动中有所应用，核心思路是"关键点→关节角度→与标准模板对比"，这套框架在逻辑上是通用的。',
      '选择网球的原因：动作技术规范明确、业余爱好者群体大、专业教练资源稀缺、现有智能分析工具极少，痛点真实。',
      '技术路线确定：双引擎架构（百度API在线+MediaPipe离线），两套方案统一输出17点格式，后续模块无需感知检测来源。',
      '14:22 完成首次提交，建立项目骨架：server.py（HTTP路由）、keypoint.py（百度API）、mediapipe_keypoint.py（本地模型）、analyzer.py（角度计算）、data.py（常量定义）、templates.py（模板管理）、前端三件套。',
      '当日新增21个文件，1256行代码。',
    ],
    commits: [
      ['14:22', 'Initial commit', '项目骨架，21文件 +1256行'],
      ['18:00', 'docs: README完善', '安装与使用说明'],
    ]
  },
  {
    title: '第二天（7月21日上午）— 核心算法实现',
    ref: 'b2',
    plan: [
      '完整实现关节角度计算，支持2D/3D双模式',
      '实现模板管理：多次训练加权均值合并',
      '实现逐角度对比，生成问题列表并按严重程度排序',
      '实现线性评分初版，验证系统端到端流程',
    ],
    records: [
      'calc_angle()：以关节顶点b为原点，构造BA、BC向量，用向量点积公式计算夹角。设置max/min夹紧防止浮点误差越界，use_3d=True时引入z轴分量。',
      'extract_angles()：遍历ANGLE_DEFS批量计算7个核心角度（上肢4个、下肢2个、躯干1个）。',
      'compare_to_template()：逐角度对比，超出容差生成问题条目，附带改进建议文本，按严重程度排序。',
      'save_template()：新动作直接存储，已有动作按加权均值公式合并，多次训练样本均匀融合。',
      '下午录入初始模板数据：正手击球、反手击球、发球等基础动作。',
    ],
    commits: [
      ['全天', 'analyzer.py核心函数实现', '角度计算、模板匹配、问题列表'],
      ['下午', '录入模板数据', 'tennis_templates.json初始版本'],
    ]
  },
  {
    title: '第三天（7月21日下午-晚上）— 历史追踪与语义分析',
    ref: 'b3',
    plan: [
      '新增 history.py：持久化保存每次评估记录',
      '前端新增进步曲线Tab，使用Chart.js绘制折线图',
      '接入通义千问 qwen-vl-max，实现视觉语义分析',
      '优化VL Prompt，覆盖握拍、击球点等5个分析维度',
    ],
    records: [
      '20:45 提交 feat: add history tracking and progress chart。',
      'history.py：采用JSON文件存储（无需数据库），按学员分组，每条记录含时间戳、动作类型、评分、角度、问题列表。新增三个API接口。',
      '进步曲线：Chart.js折线图，横轴时间，纵轴得分，鼠标悬停显示动作类型与问题数，支持按学员筛选。',
      'VL语义分析：调用qwen-vl-max，Prompt覆盖5个维度：握拍方式、击球点位置、击球点偏差影响、眼神头部、最重要改进建议。设计为可选模块，无API Key时自动跳过。',
    ],
    commits: [
      ['20:45', 'feat: history & progress chart', 'history.py +69行，前端 +120行'],
      ['21:30', 'docs: 研究文档', '开题报告、流程图等'],
      ['22:00', 'data: 样本数据', 'history.json初始化'],
    ]
  },
  {
    title: '第四天（7月22日）— 算法升级与流程图',
    ref: 'b4',
    plan: [
      '升级为加权RMSE匹配：肩角2.5、肘角2.0权重',
      '升级为非线性平方惩罚评分',
      '绘制系统流程图，整理技术路线文档',
    ],
    records: [
      '12:59 提交 feat: weighted RMSE matching and nonlinear scoring，是算法层面最重要的一次升级。',
      '加权RMSE：RMSE = √(Σwᵢ(θᵢ-θᵢ*)² / Σwᵢ)，重要关节对匹配结果影响更大，动作阶段识别准确率明显提升。',
      '非线性评分：ratio = |偏差|/阈值，penalty += w × min(ratio², 4)，单角度上限4倍防止一个极端角度压垮总分。score = 100 × (1 - penalty/max_penalty)。',
      '问题列表按 权重×|偏差| 降序排列，最关键问题优先展示。',
      '绘制系统流程图（训练路径+评估路径双分支），为答辩材料准备图表。',
    ],
    commits: [
      ['12:59', 'feat: weighted RMSE + nonlinear scoring', 'analyzer.py +47行，data.py +12行'],
      ['14:20', 'docs: 流程图v1', '双分支结构'],
      ['16:05', 'docs: 流程图v2', '图例与算法标注'],
    ]
  },
  {
    title: '第五天（7月23日）— 视频模块、Bug修复与实验验证',
    ref: 'b5',
    plan: [
      '完整实现 video_analyzer.py：帧提取、逐帧分析、多帧聚合、批量训练',
      '修复三个已知后端Bug',
      '前端新增"上传下一个"按钮，视频评估新增拍摄角度选项',
      '编写测试脚本，完成四组实验验证（共80次测试）',
      '代码整理收尾',
    ],
    records: [
      '19:37 完成大体量提交，14个文件，新增约1700行。',
      'video_analyzer.py：extract_frames() 均匀采样视频帧，analyze_video_frames() 逐帧检测分析，train_from_video() 支持均值/最高分帧/第一帧三种策略，batch_train_from_video() 一次训练多动作阶段。',
      'Bug1：base64变量遮蔽全局模块，改用video_bytes变量名解决。',
      'Bug2：float|None语法不兼容Python 3.9，改用Optional[float]解决。',
      'Bug3：dict对象用属性访问方式，改为字典键访问解决。',
      '四组实验（图片/视频 × 规范/不规范）：实验一100分、实验二68分、实验三82.2分（最佳帧97分）、实验四62.8分。80次测试成功76次，成功率95%。',
    ],
    commits: [
      ['19:37', 'fix: 视频分析+前端功能', 'video_analyzer.py +471行，server.py +249行'],
      ['21:15', 'refactor: 代码整理', '测试文件移入tests/，固定端口8080'],
    ]
  }
];

const children = [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 300 },
    children: [new TextRun({ text: '开发日志', bold: true, size: 48, color: '1A3550', font: 'Arial' })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 100 },
    children: [new TextRun({ text: '基于计算机视觉与大语言模型的网球动作智能教练系统', size: 24, color: '475569' })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 0, after: 500 },
    children: [new TextRun({ text: '开发周期：2026年7月20日 — 2026年7月23日', size: 22, color: '64748B' })] }),
];

days.forEach((day, idx) => {
  children.push(pb());
  children.push(h1(day.title));

  children.push(h2('工作计划'));
  day.plan.forEach(item => children.push(bl(item, day.ref)));

  children.push(h2('工作记录'));
  day.records.forEach(item => children.push(p(item)));

  children.push(new Paragraph({ spacing: { before: 200, after: 80 }, children: [new TextRun({ text: '提交记录', bold: true })] }));
  children.push(new Table({
    columnWidths: [1500, 2800, 5060],
    margins: { top: 80, bottom: 80, left: 160, right: 160 },
    rows: [
      new TableRow({ tableHeader: true, children:
        ['时间', '提交说明', '变更内容'].map((text, i) =>
          new TableCell({ borders: cb, width: { size: [1500,2800,5060][i], type: WidthType.DXA },
            shading: cs('D6E8F5'), children: [new Paragraph({ alignment: AlignmentType.CENTER,
              children: [new TextRun({ text, bold: true, size: 22 })] })] }))
      }),
      ...day.commits.map(([t, s, c]) => new TableRow({ children:
        [t, s, c].map((text, i) =>
          new TableCell({ borders: cb, width: { size: [1500,2800,5060][i], type: WidthType.DXA },
            shading: cs('FFFFFF'), children: [new Paragraph({ alignment: i===0 ? AlignmentType.CENTER : AlignmentType.LEFT,
              children: [new TextRun({ text, size: 21 })] })] }))
      }))
    ]
  }));
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: 'Arial', size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 30, bold: true, color: '1A3550', font: 'Arial' },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { size: 25, bold: true, color: '1A3550', font: 'Arial' },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ]
  },
  numbering: { config: numConfig },
  sections: [{ properties: { page: { margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } }, children }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync('/Users/I072157/科创/tennis_coach/doc/开发日志_五天工作计划与记录.docx', buf);
  console.log('Done');
});
