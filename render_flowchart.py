#!/usr/bin/env python3
"""Render tennis-coach pipeline flowchart — improved version."""

from PIL import Image, ImageDraw, ImageFont
import os, math

PINGFANG = "/System/Library/AssetsV2/com_apple_MobileAsset_Font8/86ba2c91f017a3749571a82f2c6d890ac7ffb2fb.asset/AssetData/PingFang.ttc"
HEITI    = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_DIR = os.path.expanduser("~/.claude/skills/canvas-design/canvas-fonts")

def load_font(name, size):
    try: return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except: return ImageFont.load_default()

def load_cn(size):
    for path, idx in [(PINGFANG, 4), (PINGFANG, 1), (HEITI, 0)]:
        try: return ImageFont.truetype(path, size, index=idx)
        except: pass
    return ImageFont.load_default()

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H  = 1400, 1560
SC    = 2
img   = Image.new("RGB", (W*SC, H*SC), "#F7F6F2")
d     = ImageDraw.Draw(img)
def s(v): return int(v * SC)

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = "#F7F6F2"
INK         = "#111827"
INK_MUTED   = "#6B7280"
INK_FAINT   = "#9CA3AF"
ACCENT      = "#1B4F8A"        # deep blue — input / output
ACCENT2     = "#2563EB"        # medium blue — arrows, step badges
LINE        = "#CBD5E1"

COMPUTE_BG  = "#FFFFFF"        # pure computation nodes
COMPUTE_BR  = "#CBD5E1"

API_BG      = "#EFF6FF"        # external cloud API
API_BR      = "#93C5FD"
API_INK     = "#1D4ED8"

LOCAL_BG    = "#F0FDF4"        # local model
LOCAL_BR    = "#86EFAC"
LOCAL_INK   = "#15803D"

OPT_BG      = "#FFFBEB"        # optional / rule-based
OPT_BR      = "#FCD34D"
OPT_INK     = "#92400E"

DARK_BG     = "#1E293B"        # output terminal bar

# ── Fonts ─────────────────────────────────────────────────────────────────────
f_title   = load_font("GeistMono-Bold.ttf",    26)
f_mono    = load_font("DMMono-Regular.ttf",    17)
f_mono_sm = load_font("DMMono-Regular.ttf",    14)
f_tag     = load_font("GeistMono-Regular.ttf", 13)
f_badge   = load_font("GeistMono-Bold.ttf",    13)
f_tech    = load_font("DMMono-Regular.ttf",    15)
f_cn_xl   = load_cn(30)
f_cn_lg   = load_cn(26)
f_cn_md   = load_cn(21)
f_cn_sm   = load_cn(16)

# ── Helpers ───────────────────────────────────────────────────────────────────
def tw(txt, font):
    bb = d.textbbox((0,0), txt, font=font)
    return bb[2] - bb[0]

def th_of(txt, font):
    bb = d.textbbox((0,0), txt, font=font)
    return bb[3] - bb[1]

def tc(txt, cx, y, font, color=INK):
    d.text((s(cx) - tw(txt,font)//2, s(y)), txt, font=font, fill=color)

def tl(txt, x, y, font, color=INK):
    d.text((s(x), s(y)), txt, font=font, fill=color)

def rect(x, y, w, h, fill, outline=None, r=10, lw=2):
    d.rounded_rectangle([s(x),s(y),s(x+w),s(y+h)],
                        radius=s(r), fill=fill,
                        outline=outline, width=s(lw) if outline else 0)

def hline(x1, y, x2, color=LINE, lw=1):
    d.line([(s(x1),s(y)),(s(x2),s(y))], fill=color, width=s(lw))

def arrow(cx, y1, y2, color=ACCENT2, lw=2):
    d.line([(s(cx),s(y1)),(s(cx),s(y2)-s(9))], fill=color, width=s(lw))
    ah, aw = s(9), s(5)
    tip = (s(cx), s(y2))
    d.polygon([tip,(tip[0]-aw,tip[1]-ah),(tip[0]+aw,tip[1]-ah)], fill=color)

def dot(cx, cy, r=4, color=ACCENT2):
    r=s(r); cx,cy=s(cx),s(cy)
    d.ellipse([cx-r,cy-r,cx+r,cy+r], fill=color)

def step_badge(cx, y, label):
    """Rounded pill badge for step number."""
    bw, bh = 70, 24
    rect(cx - bw//2, y, bw, bh, ACCENT2, None, r=12, lw=0)
    tc(label, cx, y+4, f_badge, "#FFFFFF")

def or_divider(x, y, w):
    """Horizontal divider with OR label in center."""
    hline(x+20, y, x+w//2-20, LINE)
    hline(x+w//2+20, y, x+w-20, LINE)
    or_label = "OR"
    bw2 = tw(or_label, f_badge) + 16
    rect(x+w//2-bw2//2, y-10, bw2, 20, "#F1F5F9", LINE, r=10, lw=1)
    tc(or_label, x+w//2, y-7, f_badge, INK_MUTED)

# ── Subtle dot-grid background ────────────────────────────────────────────────
for gx in range(40, W, 40):
    for gy in range(40, H, 40):
        dot(gx, gy, r=1, color="#DEDAD4")

# ── Header ────────────────────────────────────────────────────────────────────
d.rectangle([0, 0, s(W), s(68)], fill=DARK_BG)
tc("TENNIS COACH  —  AI PIPELINE ARCHITECTURE", W//2, 14, f_title, "#F8FAFC")
tc("计算机视觉 × 大语言模型  ·  技术路线流程图", W//2, 44, f_cn_sm, "#94A3B8")
hline(0, 68, W, "#334155", lw=1)

# ── Layout constants ──────────────────────────────────────────────────────────
CX  = W // 2          # 700
NW  = 560
NX  = CX - NW // 2   # 420
NH  = 72              # standard node height
SUB_W  = 240
SUB_H  = 110
SUB_LX = NX + 22
SUB_RX = NX + NW - 22 - SUB_W
BCL    = SUB_LX + SUB_W // 2
BCR    = SUB_RX + SUB_W // 2

# ── Y positions ───────────────────────────────────────────────────────────────
Y_INPUT  = 90
Y_S01    = 202   # h = 222
Y_S02    = 478
Y_S03    = 592
Y_S04A   = 706
Y_S04B   = 820   # h = 238
Y_OUTPUT = 1112

# ── Arrows ────────────────────────────────────────────────────────────────────
arrow(CX, Y_INPUT + NH,       Y_S01)
arrow(CX, Y_S01 + 222,        Y_S02)
arrow(CX, Y_S02 + NH,         Y_S03)
arrow(CX, Y_S03 + NH,         Y_S04A)
arrow(CX, Y_S04A + NH,        Y_S04B)
arrow(CX, Y_S04B + 238,       Y_OUTPUT)

# ── INPUT ─────────────────────────────────────────────────────────────────────
rect(CX-150, Y_INPUT, 300, NH, ACCENT, None, r=36, lw=0)
tc("图片输入  /  INPUT", CX, Y_INPUT+10, f_cn_lg, "#FFFFFF")
tc("Upload a photo to start", CX, Y_INPUT+42, f_mono_sm, "#93C5FD")

# ── STEP 01 — dual branch ─────────────────────────────────────────────────────
BH1 = 222
rect(NX, Y_S01, NW, BH1, COMPUTE_BG, COMPUTE_BR, r=12, lw=2)
# left accent strip
d.rectangle([s(NX), s(Y_S01), s(NX)+s(5), s(Y_S01+BH1)], fill=ACCENT2)
step_badge(CX, Y_S01 - 14, "STEP 01")
tc("人体关键点检测", CX, Y_S01+10, f_cn_xl, INK)
tc("Human Keypoint Detection", CX, Y_S01+46, f_mono_sm, INK_MUTED)

# OR divider between sub-boxes
or_divider(NX+16, Y_S01+82, NW-32)

# Left: Baidu API (cloud)
rect(SUB_LX, Y_S01+90, SUB_W, SUB_H, API_BG, API_BR, r=8, lw=1)
tc("百度人体分析 API", BCL, Y_S01+96, f_cn_md, API_INK)
tc("云端  ·  17 关键点", BCL, Y_S01+122, f_cn_sm, INK_MUTED)
tc("Baidu Body Analysis  ·  Cloud", BCL, Y_S01+148, f_tag, INK_FAINT)
# cloud icon dot
dot(SUB_LX+SUB_W-16, Y_S01+98, r=5, color=API_BR)

# Right: MediaPipe (local)
rect(SUB_RX, Y_S01+90, SUB_W, SUB_H, LOCAL_BG, LOCAL_BR, r=8, lw=1)
tc("MediaPipe Pose", BCR, Y_S01+96, f_cn_md, LOCAL_INK)
tc("本地离线  ·  33→17 点", BCR, Y_S01+122, f_cn_sm, INK_MUTED)
tc("Local Offline  ·  Google Model", BCR, Y_S01+148, f_tag, INK_FAINT)
dot(SUB_RX+SUB_W-16, Y_S01+98, r=5, color=LOCAL_BR)

dot(CX, Y_S01+BH1-10)

# ── STEP 02 ───────────────────────────────────────────────────────────────────
rect(NX, Y_S02, NW, NH, COMPUTE_BG, COMPUTE_BR, r=12, lw=2)
d.rectangle([s(NX), s(Y_S02), s(NX)+s(5), s(Y_S02+NH)], fill=ACCENT2)
step_badge(CX, Y_S02 - 14, "STEP 02")
tc("关节角度计算", CX, Y_S02+10, f_cn_xl, INK)
tc("余弦定理  ·  7 核心角度  ·  Vector Dot Product", CX, Y_S02+46, f_cn_sm, INK_MUTED)

# ── STEP 03 ───────────────────────────────────────────────────────────────────
rect(NX, Y_S03, NW, NH, COMPUTE_BG, COMPUTE_BR, r=12, lw=2)
d.rectangle([s(NX), s(Y_S03), s(NX)+s(5), s(Y_S03+NH)], fill=ACCENT2)
step_badge(CX, Y_S03 - 14, "STEP 03")
tc("自动动作匹配", CX, Y_S03+10, f_cn_xl, INK)
tc("加权 RMSE  ·  肩/肘权重×2.5  ·  12 标准动作模板", CX, Y_S03+46, f_cn_sm, INK_MUTED)

# ── STEP 04a ──────────────────────────────────────────────────────────────────
rect(NX, Y_S04A, NW, NH, COMPUTE_BG, COMPUTE_BR, r=12, lw=2)
d.rectangle([s(NX), s(Y_S04A), s(NX)+s(5), s(Y_S04A+NH)], fill=ACCENT2)
step_badge(CX, Y_S04A - 14, "STEP 04")
tc("偏差分析与非线性评分", CX, Y_S04A+10, f_cn_xl, INK)
tc("平方惩罚评分  ·  阈值检测  ·  0 – 100 分  ·  问题按权重排序", CX, Y_S04A+46, f_cn_sm, INK_MUTED)

# ── STEP 05 — dual branch ─────────────────────────────────────────────────────
BH5 = 238
rect(NX, Y_S04B, NW, BH5, COMPUTE_BG, COMPUTE_BR, r=12, lw=2)
d.rectangle([s(NX), s(Y_S04B), s(NX)+s(5), s(Y_S04B+BH5)], fill=ACCENT2)
step_badge(CX, Y_S04B - 14, "STEP 05")
tc("改进建议生成", CX, Y_S04B+10, f_cn_xl, INK)
tc("Feedback Generation", CX, Y_S04B+44, f_mono_sm, INK_MUTED)

or_divider(NX+16, Y_S04B+82, NW-32)

# Left: rule-based
rect(SUB_LX, Y_S04B+90, SUB_W, SUB_H+16, OPT_BG, OPT_BR, r=8, lw=1)
tc("规则化文本建议", BCL, Y_S04B+96, f_cn_md, OPT_INK)
tc("预设文案 · 7 角度偏差", BCL, Y_S04B+122, f_cn_sm, INK_MUTED)
tc("Rule-based  ·  Always on", BCL, Y_S04B+150, f_tag, INK_FAINT)
dot(SUB_LX+SUB_W-16, Y_S04B+98, r=5, color=OPT_BR)

# Right: Qwen VL (optional)
rect(SUB_RX, Y_S04B+90, SUB_W, SUB_H+16, API_BG, API_BR, r=8, lw=1)
tc("通义千问 VL 模型", BCR, Y_S04B+96, f_cn_md, API_INK)
tc("语义分析（可选）", BCR, Y_S04B+122, f_cn_sm, INK_MUTED)
tc("qwen-vl-max  ·  Optional", BCR, Y_S04B+150, f_tag, INK_FAINT)
dot(SUB_RX+SUB_W-16, Y_S04B+98, r=5, color=API_BR)

dot(CX, Y_S04B+BH5-10)

# ── OUTPUT ────────────────────────────────────────────────────────────────────
rect(NX, Y_OUTPUT, NW, NH+8, DARK_BG, None, r=12, lw=0)
d.rectangle([s(NX), s(Y_OUTPUT), s(NX)+s(5), s(Y_OUTPUT+NH+8)], fill=ACCENT2)
tc("骨骼可视化  ·  评分报告  ·  进步曲线", CX, Y_OUTPUT+8, f_cn_lg, "#F8FAFC")
tc("Skeleton  ·  Score Report  ·  History & Progress Chart", CX, Y_OUTPUT+44, f_mono_sm, "#64748B")

# ── Tech stack ────────────────────────────────────────────────────────────────
TSY = Y_OUTPUT + NH + 8 + 50
hline(60, TSY-20, W-60, "#CBD5E1", lw=1)
tc("TECH  STACK", CX, TSY-16, f_tag, INK_FAINT)

tech_items = [
    ("Python 3.11+",    DARK_BG,  "#F8FAFC"),
    ("MediaPipe 0.10+", ACCENT,   "#FFFFFF"),
    ("OpenCV",          ACCENT,   "#FFFFFF"),
    ("NumPy",           "#374151","#FFFFFF"),
    ("requests",        "#374151","#FFFFFF"),
    ("qwen-vl-max",     ACCENT2,  "#FFFFFF"),
    ("Chart.js",        "#374151","#FFFFFF"),
    ("PIL / Pillow",    "#374151","#FFFFFF"),
]

pad_x, t_h, gap = 18, 36, 8
widths  = [tw(t, f_tech)+pad_x*2 for t,_,_ in tech_items]
total_w = sum(widths) + gap*(len(tech_items)-1)
cx_cur  = CX - total_w//2
for (t, bg, fg), tw2 in zip(tech_items, widths):
    rect(cx_cur, TSY, tw2, t_h, bg, None, r=6, lw=0)
    tl(t, cx_cur+(tw2-tw(t,f_tech))//2, TSY+10, f_tech, fg)
    cx_cur += tw2 + gap

# ── Legend ────────────────────────────────────────────────────────────────────
LEG_Y = TSY + t_h + 30
hline(60, LEG_Y-6, W-60, "#E2E8F0", lw=1)

legend_items = [
    (API_BG,   API_BR,   "云端 API  /  Cloud API"),
    (LOCAL_BG, LOCAL_BR, "本地模型  /  Local Model"),
    (OPT_BG,   OPT_BR,   "规则引擎  /  Rule Engine"),
    (COMPUTE_BG, COMPUTE_BR, "本地计算  /  Computation"),
]
lw2 = 180
total_lw = lw2 * len(legend_items) + 16 * (len(legend_items)-1)
lx = CX - total_lw//2
for bg, br, label in legend_items:
    rect(lx, LEG_Y, lw2, 30, bg, br, r=6, lw=1)
    tc(label, lx+lw2//2, LEG_Y+7, f_cn_sm, INK_MUTED)
    lx += lw2 + 16

# ── Footer ────────────────────────────────────────────────────────────────────
foot_y = LEG_Y + 46
hline(60, foot_y, W-60, LINE, lw=1)
tc("tennis_coach  ·  AI Pipeline Architecture  ·  2026", CX, foot_y+10, f_tag, INK_FAINT)

# ── Crop & save ───────────────────────────────────────────────────────────────
final_h = foot_y + 46
crop = img.crop((0, 0, s(W), s(final_h)))
out  = crop.resize((W, final_h), Image.LANCZOS)
path = os.path.expanduser("~/科创/tennis_coach/doc/pipeline_flowchart.png")
out.save(path, "PNG", dpi=(144,144))
print(f"Saved: {path}  ({W}×{final_h}px)")
