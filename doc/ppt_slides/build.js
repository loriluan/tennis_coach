process.env.NODE_PATH = '/Users/I072157/.nvm/versions/node/v20.19.6/lib/node_modules';
require('module').Module._initPaths();
const MODULE_ROOT = '/Users/I072157/.nvm/versions/node/v20.19.6/lib/node_modules';
const pptxgen = require(MODULE_ROOT + '/pptxgenjs');
const html2pptx = require('/Users/I072157/.claude/skills/pptx/scripts/html2pptx');
const path = require('path');

const DIR = '/Users/I072157/科创/tennis_coach/doc/ppt_slides';
const IMG = '/Users/I072157/科创/tennis_coach/data/docsource';

const BDR = (color) => ({ line: { color, width: 1.5 } });

async function build() {
    const pptx = new pptxgen();
    pptx.layout = 'LAYOUT_16x9';
    pptx.title = '基于计算机视觉与大语言模型的网球动作智能教练系统';

    const files = [
        'slide01.html',
        'slide_toc.html',
        'slide_sec1.html',
        'slide02.html',
        'slide03.html',
        'slide_sec2.html',
        'slide04.html',
        'slide04b.html',
        'slide05.html',
        'slide04c.html',
        'slide06.html',
        'slide08.html',
        'slide09.html',
        'slide_sec3.html',
        'slide10.html',
        'slide11.html',
        'slide11b.html',
        'slide12.html',
        'slide_thanks.html',
    ];

    for (const f of files) {
        const { slide } = await html2pptx(path.join(DIR, f), pptx);

        // 分节页：蜂窝 + 扫描线
        if (f === 'slide_sec1.html' || f === 'slide_sec2.html' || f === 'slide_sec3.html') {
            const colors = { 'slide_sec1.html': '00D4FF', 'slide_sec2.html': '10B981', 'slide_sec3.html': 'F59E0B' };
            const col = colors[f];
            for (const yPct of [0.3, 0.5, 0.7]) {
                slide.addShape(pptx.shapes.RECTANGLE, { x: 4.5, y: 5.625 * yPct, w: 5.5, h: 0.01, fill: { color: col, transparency: 75 }, line: { color: col, transparency: 75, width: 0 } });
            }
            const hexW = 0.42, hexH = 0.42, hexGap = 0.1;
            const totalW = 3 * hexW + 2 * hexGap;
            const totalH = 3 * hexH + 2 * hexGap;
            const startX = 7.25 - totalW / 2;
            const startY = 5.625 / 2 - totalH / 2 - 0.3;
            const grid = [[0,0],[1,0],[2,0],[0,1],[1,1],[2,1],[0,2],[1,2],[2,2]];
            const litCells = new Set(['0,1','1,0','1,2','2,1']);
            for (const [ci, ri] of grid) {
                const key = `${ci},${ri}`;
                const isCenter = ci===1 && ri===1;
                const isLit = litCells.has(key);
                const x = startX + ci * (hexW + hexGap);
                const y = startY + ri * (hexH + hexGap);
                const tr = isCenter ? 0 : isLit ? 40 : 80;
                slide.addShape(pptx.shapes.ROUNDED_RECTANGLE, { x, y, w: hexW, h: hexH, rectRadius: 0.08, fill: { color: col, transparency: tr }, line: { color: col, transparency: Math.max(tr-10,0), width: 0.5 } });
            }
            const ballSize = hexW * 0.75;
            const cx = startX + (hexW + hexGap) + (hexW - ballSize) / 2;
            const cy = startY + (hexH + hexGap) + (hexH - ballSize) / 2;
            slide.addShape(pptx.shapes.OVAL, { x: cx, y: cy, w: ballSize, h: ballSize, fill: { color: 'C5E82A' }, line: { color: 'A0C010', width: 0.5 } });
            const nums = { 'slide_sec1.html': '01', 'slide_sec2.html': '02', 'slide_sec3.html': '03' };
            slide.addText(nums[f], { x: 7.2, y: 3.4, w: 2.5, h: 1.8, fontSize: 96, bold: true, color: col, transparency: 92, align: 'center' });
        }

        // slide04b 训练方式
        if (f === 'slide04b.html') {
            const h = 3.8;
            const w1 = h * (900 / 1372);
            slide.addImage({ path: `${IMG}/第一页.jpg`, x: 4.5, y: 0.85, w: w1, h, ...BDR('1E3A5F') });
            const w2 = h * (892 / 1340);
            slide.addImage({ path: `${IMG}/第四页.jpg`, x: 4.5 + w1 + 0.15, y: 0.85, w: w2, h, ...BDR('1E3A5F') });
        }

        // slide04c 评估模式
        if (f === 'slide04c.html') {
            const h = 3.8, w = h * (1330 / 1730);
            slide.addImage({ path: `${IMG}/评估模式.png`, x: 5.2, y: 0.85, w, h, ...BDR('00D4FF') });
        }

        // slide05 双引擎检测
        if (f === 'slide05.html') {
            const h = 3.8, w = h * (898 / 1390);
            slide.addImage({ path: `${IMG}/第三页.jpg`, x: 3.6, y: 0.9, w, h, ...BDR('00D4FF') });
        }

        // slide09 系统架构 — 不加图片

        // slide10 实验一二
        if (f === 'slide10.html') {
            const addImg = (imgPath, x, y, w, h, label, color) => {
                slide.addImage({ path: imgPath, x, y, w, h, ...BDR(color) });
                slide.addText(label, { x, y: y+h+0.04, w, h: 0.22, fontSize: 9, color, align: 'center' });
            };
            addImg(`${IMG}/正确姿势.png`,       0.500, 2.217, 0.938, 1.600, '输入图片',      '10B981');
            addImg(`${IMG}/正确姿势关键点.png`, 1.550, 1.384, 0.899, 1.600, '关键点检测',    '10B981');
            addImg(`${IMG}/正确姿势大语言.jpg`, 2.144, 3.081, 2.465, 1.484, '评分 & LLM分析','10B981');
            addImg(`${IMG}/错误姿势.jpg`,        5.000, 1.050, 1.300, 1.600, '输入图片',      'F97316');
            addImg(`${IMG}/错误姿势关键点.jpg`,  5.000, 2.750, 1.300, 1.600, '关键点检测',    'F97316');
            addImg(`${IMG}/错误姿势大语言.jpg`,  6.450, 1.615, 2.800, 2.171, '评分 & LLM分析','F97316');
        }

        // slide11 实验三四
        if (f === 'slide11.html') {
            const addImg = (imgPath, x, y, w, h, label, color) => {
                slide.addImage({ path: imgPath, x, y, w, h, ...BDR(color) });
                slide.addText(label, { x, y: y+h+0.04, w, h: 0.22, fontSize: 9, color, align: 'center' });
            };
            const maxW=2.0, maxH=2.2, imgY=1.22;
            const place = (imgPath, ratio, cx, slot, label, col) => {
                let w=Math.min(maxW,maxH*ratio), h=w/ratio;
                if (h>maxH) { h=maxH; w=h*ratio; }
                addImg(imgPath, cx+slot*(maxW+0.1)+(maxW-w)/2, imgY+(maxH-h)/2, w, h, label, col);
            };
            place(`${IMG}/正确姿势关键帧截.jpg`,   674/1056,  0.5, 0, '视频截帧',    '10B981');
            place(`${IMG}/正确视频结果.jpg`,       1622/1346, 0.5, 1, '视频评分结果','10B981');
            place(`${IMG}/错误姿势关键帧截频.jpg`, 1626/1326, 5.1, 0, '视频截帧',    'F97316');
            place(`${IMG}/错误视频关键帧.jpg`,      562/878,  5.1, 1, '关键点检测',  'F97316');
        }

        // slide11b 进步曲线
        if (f === 'slide11b.html') {
            const h = 3.8, w = h * (890 / 1054);
            slide.addImage({ path: `${IMG}/第五页.jpg`, x: 5.15, y: 0.85, w, h, ...BDR('10B981') });
        }

        // slide12 总结 — 不加图片

        console.log(`${f} done`);
    }

    await pptx.writeFile({ fileName: '/Users/I072157/科创/tennis_coach/doc/tennis_coach_presentation.pptx' });
    console.log('PPTX saved.');
}

build().catch(e => { console.error(e); process.exit(1); });
