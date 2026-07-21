#!/usr/bin/env python3
"""Render tennis-coach pipeline flowchart — Chinese-aware version."""

from PIL import Image, ImageDraw, ImageFont
import os

FONT_DIR  = os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts")
PINGFANG  = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
HEITI     = "/System/Library/Fonts/STHeiti Medium.ttc"

def load_font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except:
        return ImageFont.load_default()

def load_cn(size, bold=False):
    """Load a font that renders Chinese characters."""
    # Try PingFang SC Medium (index 4), then Regular, then Heiti
    for path, idx in [(PINGFANG, 4), (PINGFANG, 1), (HEITI, 0)]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except:
            pass
    return ImageFont.load_default()

# ── Canvas ──────────────────────────────────────────────────────────────────
W, H     = 1400, 1420
SCALE    = 2
img      = Image.new("RGB", (W*SCALE, H*SCALE), "#F5F3EE")
d        = ImageDraw.Draw(img)

def s(v): return v * SCALE

# ── Palette ──────────────────────────────────────────────────────────────────
BG      = "#F5F3EE"
INK     = "#1A1A1A"
ACCENT  = "#1B4F8A"
ACCENT2 = "#2D7DD2"
NEUTRAL = "#C8C2B6"
NODE_BG = "#FFFFFF"
OPT_BG  = "#EBF3FB"
OPT_BOR = "#7AADD4"
GOLD_BG = "#FFFDF5"
GOLD_BR = "#C8A96E"
TECH_BG = "#1A1A1A"
TECH_FG = "#F5F3EE"

# ── Fonts ─────────────────────────────────────────────────────────────────────
# Mono / Latin  (GeistMono / DMMono)
f_title   = load_font("GeistMono-Bold.ttf",    28)
f_mono    = load_font("DMMono-Regular.ttf",    18)
f_mono_sm = load_font("DMMono-Regular.ttf",    15)
f_tag     = load_font("GeistMono-Regular.ttf", 14)
f_tech    = load_font("DMMono-Regular.ttf",    15)
# Chinese  (PingFang SC)
f_cn_lg   = load_cn(28)   # main node CJK title
f_cn_md   = load_cn(22)   # sub-node CJK label
f_cn_sm   = load_cn(16)   # small CJK annotation

# ── Helpers ───────────────────────────────────────────────────────────────────
def rect(x, y, w, h, fill, outline, radius=10, lw=2):
    x,y,w,h,radius,lw = s(x),s(y),s(w),s(h),s(radius),s(lw)
    d.rounded_rectangle([x,y,x+w,y+h], radius=radius,
                        fill=fill, outline=outline, width=lw)

def tw_of(txt, font):
    bb = d.textbbox((0,0), txt, font=font)
    return bb[2]-bb[0]

def text_center(txt, cx, y, font, color=INK):
    w = tw_of(txt, font)
    d.text((s(cx)-w//2, s(y)), txt, font=font, fill=color)

def text_left(txt, x, y, font, color=INK):
    d.text((s(x), s(y)), txt, font=font, fill=color)

def arrow_down(cx, y1, y2, color=ACCENT2, lw=2):
    d.line([(s(cx),s(y1)),(s(cx),s(y2)-s(10))], fill=color, width=s(lw))
    ah,aw = s(10),s(6)
    tip = (s(cx), s(y2))
    d.polygon([tip,(tip[0]-aw,tip[1]-ah),(tip[0]+aw,tip[1]-ah)], fill=color)

def fine_line(x1,y1,x2,y2,color=NEUTRAL,lw=1):
    d.line([(s(x1),s(y1)),(s(x2),s(y2))], fill=color, width=s(lw))

def dot(cx,cy,r=5,color=ACCENT2):
    r=s(r); cx,cy=s(cx),s(cy)
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)

# ── Background grid ───────────────────────────────────────────────────────────
for gx in range(0,W,50): fine_line(gx,0,gx,H,"#ECEAE4")
for gy in range(0,H,50): fine_line(0,gy,W,gy,"#ECEAE4")

# ── Header bar ────────────────────────────────────────────────────────────────
d.rectangle([0,0,s(W),s(72)], fill=TECH_BG)
text_center("TENNIS COACH  —  AI PIPELINE ARCHITECTURE", W//2, 18, f_title, TECH_FG)
sub_cn = "计算机视觉 × 大语言模型  ·  技术路线流程图"
text_center(sub_cn, W//2, 46, f_cn_sm, "#8899AA")

fine_line(60,82,W-60,82,NEUTRAL)

# ── Layout ────────────────────────────────────────────────────────────────────
CX  = W//2      # 700
NW  = 540       # node width
NH  = 66        # standard node height
NX  = CX-NW//2  # 430

def accent_bar(x, y, h):
    d.rectangle([s(x),s(y),s(x)+s(6),s(y+h)], fill=ACCENT)

# ── Y-positions ───────────────────────────────────────────────────────────────
Y_INPUT   = 100
Y_S01     = 210   # branch node (h=210)
Y_S02     = 460
Y_S03     = 578
Y_S04A    = 696
Y_S04B    = 810   # branch node (h=230)
Y_OUTPUT  = 1090

# ── Arrows ────────────────────────────────────────────────────────────────────
arrow_down(CX, Y_INPUT+NH, Y_S01)
arrow_down(CX, Y_S01+210,  Y_S02)
arrow_down(CX, Y_S02+NH,   Y_S03)
arrow_down(CX, Y_S03+NH,   Y_S04A)
arrow_down(CX, Y_S04A+NH,  Y_S04B)
arrow_down(CX, Y_S04B+230, Y_OUTPUT)

# ── INPUT ─────────────────────────────────────────────────────────────────────
rect(CX-130, Y_INPUT, 260, NH, ACCENT, ACCENT, radius=33, lw=0)
text_center("图片输入  /  INPUT", CX, Y_INPUT+8, f_cn_md, "#FFFFFF")
text_center("Image Input", CX, Y_INPUT+38, f_mono_sm, "#B0C8E8")

# ── STEP 01 — dual branch ─────────────────────────────────────────────────────
BH1 = 210
rect(NX, Y_S01, NW, BH1, NODE_BG, INK, lw=2)
accent_bar(NX, Y_S01, BH1)
text_left("STEP  01", NX+18, Y_S01+6, f_tag, "#999")
text_center("人体关键点检测", CX, Y_S01+16, f_cn_lg, INK)
text_center("Human Keypoint Detection", CX, Y_S01+50, f_mono_sm, "#888")
fine_line(NX+20, Y_S01+74, NX+NW-20, Y_S01+74, NEUTRAL)

BCL = NX + NW//4
BCR = NX + 3*NW//4
bw, bh2 = 210, 108
BLX = NX + 20
BRX = NX + NW - 20 - bw

rect(BLX, Y_S01+82, bw, bh2, OPT_BG, OPT_BOR, radius=8, lw=1)
text_center("百度人体分析 API", BCL, Y_S01+88, f_cn_md, ACCENT)
text_center("云端  ·  17 关键点", BCL, Y_S01+114, f_cn_sm, "#555")
text_center("Baidu Body Analysis", BCL, Y_S01+136, f_tag, "#AAA")

rect(BRX, Y_S01+82, bw, bh2, OPT_BG, OPT_BOR, radius=8, lw=1)
text_center("MediaPipe Pose", BCR, Y_S01+88, f_cn_md, ACCENT)
text_center("本地离线  ·  33→17点", BCR, Y_S01+114, f_cn_sm, "#555")
text_center("Local Offline Model", BCR, Y_S01+136, f_tag, "#AAA")

dot(CX, Y_S01+BH1-12)

# ── STEP 02 ───────────────────────────────────────────────────────────────────
rect(NX, Y_S02, NW, NH, NODE_BG, INK, lw=2)
accent_bar(NX, Y_S02, NH)
text_left("STEP  02", NX+18, Y_S02+6, f_tag, "#999")
text_center("关节角度计算", CX, Y_S02+14, f_cn_lg, INK)
text_center("Joint Angle Extraction  ·  Vector Dot Product  ·  7 core angles", CX, Y_S02+44, f_mono_sm, "#888")

# ── STEP 03 ───────────────────────────────────────────────────────────────────
rect(NX, Y_S03, NW, NH, NODE_BG, INK, lw=2)
accent_bar(NX, Y_S03, NH)
text_left("STEP  03", NX+18, Y_S03+6, f_tag, "#999")
text_center("自动动作匹配", CX, Y_S03+14, f_cn_lg, INK)
text_center("RMSE Minimization  ·  12 Standard Action Templates", CX, Y_S03+44, f_mono_sm, "#888")

# ── STEP 04a ──────────────────────────────────────────────────────────────────
rect(NX, Y_S04A, NW, NH, NODE_BG, INK, lw=2)
accent_bar(NX, Y_S04A, NH)
text_left("STEP  04a", NX+18, Y_S04A+6, f_tag, "#999")
text_center("偏差分析与评分", CX, Y_S04A+14, f_cn_lg, INK)
text_center("Deviation Analysis  ·  Threshold Check  ·  0 – 100 Score", CX, Y_S04A+44, f_mono_sm, "#888")

# ── STEP 04b — dual branch ────────────────────────────────────────────────────
BH4 = 230
rect(NX, Y_S04B, NW, BH4, NODE_BG, INK, lw=2)
accent_bar(NX, Y_S04B, BH4)
text_left("STEP  04b", NX+18, Y_S04B+6, f_tag, "#999")
text_center("改进建议生成", CX, Y_S04B+16, f_cn_lg, INK)
text_center("Feedback Generation", CX, Y_S04B+50, f_mono_sm, "#888")
fine_line(NX+20, Y_S04B+74, NX+NW-20, Y_S04B+74, NEUTRAL)

bh4b = 120
rect(BLX, Y_S04B+82, bw, bh4b, GOLD_BG, GOLD_BR, radius=8, lw=1)
text_center("规则化文本建议", BCL, Y_S04B+88, f_cn_md, "#7A5C00")
text_center("预设改进文案", BCL, Y_S04B+114, f_cn_sm, "#888")
text_center("Rule-based Advice", BCL, Y_S04B+136, f_tag, "#BBB")
text_center("7 关节角度偏差", BCL, Y_S04B+154, f_tag, "#AAA")

rect(BRX, Y_S04B+82, bw, bh4b, OPT_BG, OPT_BOR, radius=8, lw=1)
text_center("通义千问 VL 模型", BCR, Y_S04B+88, f_cn_md, ACCENT)
text_center("语义分析（可选）", BCR, Y_S04B+114, f_cn_sm, "#555")
text_center("qwen-vl-max  API", BCR, Y_S04B+136, f_tag, "#999")
text_center("握拍 / 击球点 分析", BCR, Y_S04B+154, f_tag, "#AAA")

dot(CX, Y_S04B+BH4-12)

# ── OUTPUT ───────────────────────────────────────────────────────────────────
rect(NX, Y_OUTPUT, NW, NH, TECH_BG, TECH_BG, radius=10, lw=0)
d.rectangle([s(NX),s(Y_OUTPUT),s(NX)+s(6),s(Y_OUTPUT+NH)], fill=ACCENT2)
text_center("结果展示  ·  骨骼可视化  ·  历史记录存储", CX, Y_OUTPUT+10, f_cn_md, "#FFFFFF")
text_center("Visualization  ·  Score Report  ·  History Records", CX, Y_OUTPUT+40, f_tag, "#8899AA")

# ── Tech stack ────────────────────────────────────────────────────────────────
TSY = Y_OUTPUT + NH + 52
fine_line(60, TSY-18, W-60, TSY-18, NEUTRAL)
text_center("TECH  STACK", CX, TSY-14, f_tag, NEUTRAL)

tech_items = [
    ("Python 3.11", TECH_BG, TECH_FG),
    ("MediaPipe 0.10+", ACCENT, "#FFF"),
    ("OpenCV", ACCENT, "#FFF"),
    ("NumPy", "#444", "#FFF"),
    ("requests", "#444", "#FFF"),
    ("qwen-vl-max", "#2D7DD2", "#FFF"),
    ("HTML5 Canvas", "#555", "#FFF"),
    ("Chart.js", "#555", "#FFF"),
]

pad_x, th, gap = 18, 36, 10
widths = [tw_of(t, f_tech)+pad_x*2 for t,_,_ in tech_items]
total_w = sum(widths)+gap*(len(tech_items)-1)
cx_cur = CX - total_w//2
for (t,bg,fg),tw2 in zip(tech_items,widths):
    rect(cx_cur, TSY, tw2, th, bg, bg, radius=6, lw=0)
    text_left(t, cx_cur+(tw2-tw_of(t,f_tech))//2, TSY+10, f_tech, fg)
    cx_cur += tw2+gap

# ── Footer ────────────────────────────────────────────────────────────────────
foot_y = TSY+th+38
fine_line(60, foot_y, W-60, foot_y, NEUTRAL)
text_center("tennis_coach  ·  AI Pipeline Architecture  ·  2026", CX, foot_y+8, f_tag, NEUTRAL)

# ── Crop & save ───────────────────────────────────────────────────────────────
final_h = foot_y + 46
crop = img.crop((0, 0, s(W), s(final_h)))
out  = crop.resize((W, final_h), Image.LANCZOS)
path = os.path.expanduser("~/科创/tennis_coach/pipeline_flowchart.png")
out.save(path, "PNG", dpi=(144,144))
print(f"Saved: {path}  ({W}×{final_h}px)")
