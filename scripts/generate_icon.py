#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/generate_icon.py
从华文行楷字体生成 NetOps 多尺寸 ICO 图标
蓝色渐变背景 + 行书 "Net" 字样 + 科技感装饰元素

用法:
    python scripts/generate_icon.py          # 生成 ICO
    python scripts/generate_icon.py --preview # 同时生成预览图
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import struct
import sys
import io
from pathlib import Path

# ── 配置 ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR   = PROJECT_ROOT / "assets"
OUTPUT_ICO   = ASSETS_DIR / "netops.ico"
PREVIEW_PNG  = ASSETS_DIR / "netops_preview.png"

TEXT         = "Net"
FONT_PATH    = Path("C:/Windows/Fonts/STXINGKA.TTF")   # 华文行楷
SIZES        = (16, 32, 48, 64, 128, 256)

# 蓝色主色调（科技感渐变）
BG_TOP       = (15, 30, 60)       # 深海蓝（顶部）
BG_BOTTOM    = (25, 80, 180)      # 科技蓝（底部）
FG_COLOR     = (255, 255, 255)    # 白字
GLOW_COLOR   = (100, 180, 255)    # 发光色
# ──────────────────────────────────────────────────────


def create_gradient_bg(size: int, radius: int) -> Image.Image:
    """创建圆角渐变背景"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 绘制圆角矩形蒙版
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, size, size], radius=radius, fill=255)

    # 逐行绘制渐变
    for y in range(size):
        ratio = y / max(size - 1, 1)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # 应用圆角蒙版
    img.putalpha(mask)
    return img


def add_tech_decoration(img: Image.Image, size: int) -> Image.Image:
    """添加科技感装饰：微妙的光晕 + 节点效果"""
    draw = ImageDraw.Draw(img)
    # 四角微弱光点（仅在较大尺寸添加）
    if size >= 48:
        dot_r = max(1, size // 64)
        dot_color = (*GLOW_COLOR, 80)
        # 四角
        positions = [
            (size * 0.15, size * 0.15),
            (size * 0.85, size * 0.15),
            (size * 0.15, size * 0.85),
            (size * 0.85, size * 0.85),
        ]
        for x, y in positions:
            draw.ellipse(
                [x - dot_r, y - dot_r, x + dot_r, y + dot_r],
                fill=dot_color,
            )
    return img


def render_master_image(size: int = 256) -> Image.Image:
    """渲染 256×256 主图像"""
    radius = int(size * 0.18)  # 圆角半径

    # 渐变背景
    img = create_gradient_bg(size, radius)

    # 科技装饰
    img = add_tech_decoration(img, size)

    # 发光层（文字底部光晕）
    glow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)

    # 文字
    font_size = int(size * 0.48)  # "Net" 占画布 48% 高度
    font = ImageFont.truetype(str(FONT_PATH), font_size)

    # 计算文字居中位置
    bbox = glow_draw.textbbox((0, 0), TEXT, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1] - int(size * 0.02)  # 微偏上

    # 绘制发光效果（大尺寸才有意义）
    if size >= 64:
        glow_font = ImageFont.truetype(str(FONT_PATH), font_size)
        for offset in range(3, 0, -1):
            alpha = int(30 * (4 - offset))
            glow_draw.text(
                (tx, ty), TEXT, font=glow_font,
                fill=(*GLOW_COLOR, alpha),
            )

    # 叠加发光层
    img = Image.alpha_composite(img, glow_layer)

    # 绘制主文字（白色）
    draw = ImageDraw.Draw(img)
    draw.text((tx, ty), TEXT, font=font, fill=FG_COLOR + (255,))

    return img


def _png_blob(img: Image.Image) -> bytes:
    """将 PIL Image 转为 PNG 字节"""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _dib_bytes(img: Image.Image) -> bytes:
    """生成 BITMAPINFOHEADER + 像素数据（无 alpha，兼容 XP）"""
    # 转为 RGB（去掉 alpha）
    rgb = img.convert("RGB")
    buf = io.BytesIO()
    rgb.save(buf, format="BMP")
    bmp = buf.getvalue()
    # 跳过 14 字节 BITMAPFILEHEADER
    return bmp[14:]


def build_ico() -> None:
    """生成多尺寸 ICO 文件（手动构造，确保多帧正确）"""
    import io as _io

    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 渲染主图像（256×256）
    master = render_master_image(256)

    # 生成各尺寸帧
    frames = []
    for s in SIZES:
        frame = master.resize((s, s), Image.LANCZOS)
        frames.append(frame)

    # 手动构造 ICO 二进制
    # 256×256 帧用 PNG 压缩，其余用 DIB（BMP 去掉文件头）
    blobs = []
    for i, (s, frame) in enumerate(zip(SIZES, frames)):
        if s >= 256:
            # PNG 压缩（Vista+ 支持）
            blob = _png_blob(frame)
        else:
            # DIB 格式（兼容 XP）
            blob = _dib_bytes(frame)
        blobs.append(blob)

    # ICO 文件头: Reserved(2) + Type=1(2) + Count(2)
    count = len(SIZES)
    header = struct.pack("<HHH", 0, 1, count)

    # 计算数据偏移
    dir_size = 6 + count * 16
    data_offset = dir_size
    offsets = []
    data_blocks = b""
    for blob in blobs:
        offsets.append(data_offset + len(data_blocks))
        data_blocks += blob

    # 构造目录项（每项 16 字节）
    # ICO 目录项格式: Width(1) Height(1) ColorCount(1) Reserved(1) Planes(2) BitCount(2) Size(4) Offset(4)
    directory = b""
    for i, s in enumerate(SIZES):
        w = 0 if s >= 256 else s
        h = 0 if s >= 256 else s
        blob = blobs[i]
        is_png = s >= 256
        # Planes=1, BitCount=0 for PNG, 24 for DIB
        planes = 1
        bpp = 0 if is_png else 24
        directory += struct.pack(
            "<BBBBHHII",
            w, h, 0, 0,       # Width, Height, ColorCount, Reserved
            planes,           # Planes (2 bytes)
            bpp,              # BitCount (2 bytes, 0=PNG)
            len(blob),        # SizeInBytes (4 bytes)
            offsets[i],       # Offset (4 bytes)
        )

    # 写入文件
    with open(str(OUTPUT_ICO), "wb") as f:
        f.write(header + directory + data_blocks)

    # 验证输出
    verify_ico(OUTPUT_ICO)


def verify_ico(path: Path) -> None:
    """验证 ICO 文件结构"""
    with open(path, "rb") as f:
        d = f.read()
    _, _, count = struct.unpack_from("<HHH", d, 0)
    print("[OK] Generate success: {}".format(path))
    print("  File size: {:,} bytes ({:.1f} KB)".format(len(d), len(d)/1024))
    print("  Image count: {}".format(count))
    for i in range(count):
        off = 6 + i * 16
        w, h, _, _, bpp, sz, data_off = struct.unpack_from("<BBBBHII", d, off)
        w = w or 256
        fmt = "PNG" if bpp == 0 else "{}bpp".format(bpp)
        print("    [{}] {:>3}x{:<3}  {:>4}  {:>7,} B @{}".format(i, w, h, fmt, sz, data_off))


def save_preview() -> None:
    """保存预览图（512×512，含多尺寸展示）"""
    preview_size = 512
    preview = Image.new("RGBA", (preview_size, preview_size), (240, 240, 245, 255))
    draw = ImageDraw.Draw(preview)

    # 标题
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 28)
    except Exception:
        title_font = ImageFont.load_default()
    draw.text((20, 15), "NetOps Logo Preview", font=title_font, fill=(60, 60, 60, 255))

    # 渲染主图
    master = render_master_image(256)
    preview.paste(master, (20, 60), master)

    # 展示各尺寸
    x_offset = 300
    y_offset = 60
    for s in [16, 32, 48, 64, 128]:
        frame = master.resize((s, s), Image.LANCZOS)
        # 放大显示（保持像素感）
        display_size = max(s, 32)
        display = frame.resize((display_size, display_size), Image.NEAREST)
        preview.paste(display, (x_offset, y_offset), display)
        # 尺寸标注
        draw.text((x_offset + display_size + 10, y_offset + display_size // 2 - 8),
                  f"{s}×{s}", font=title_font, fill=(100, 100, 100, 255))
        y_offset += display_size + 15

    preview.save(str(PREVIEW_PNG))
    print("[OK] Preview saved: {}".format(PREVIEW_PNG))


if __name__ == "__main__":
    if not FONT_PATH.exists():
        print(f"✗ 字体不存在: {FONT_PATH}")
        print("  请确认 Windows 系统安装了华文行楷字体")
        sys.exit(1)

    print("=" * 50)
    print("  NetOps Logo 生成器")
    print("  字体: 华文行楷 (STXINGKA.TTF)")
    print("  文字: \"Net\"")
    print("  风格: 行书 + 科技蓝渐变")
    print("=" * 50)

    build_ico()

    # 如果带 --preview 参数，同时生成预览图
    if "--preview" in sys.argv:
        save_preview()

    print("\n提示: 运行 pyinstaller NetworkConfigGenerator.spec 重新打包 EXE")
