"""
运势报告PDF生成器 - 美化版
使用 fpdf2 库 + STHeiti TTF 字体支持中文
支持图表嵌入、优雅的样式设计
"""

import os
import re
from io import BytesIO
from typing import Optional, List

import fpdf
from fpdf.enums import XPos, YPos


# 字体路径
_BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Light.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    os.path.join(_BACKEND_ROOT, "fonts", "NotoSansSC.otf"),
]

_font_registered = False
_font_info = None

# 配色方案 - 优雅紫金主题
COLORS = {
    "primary": (74, 74, 138),        # 深紫色
    "secondary": (123, 104, 238),   # 中紫色
    "accent": (255, 215, 0),        # 金色
    "background": (240, 240, 250),  # 浅色背景（更易读）
    "surface": (248, 248, 255),      # 卡片背景
    "surface_dark": (37, 37, 64),  # 深色卡片
    "text": (51, 51, 51),            # 深色文字
    "text_light": (255, 255, 255),   # 浅色文字
    "text_secondary": (100, 100, 120), # 次要文字
    "success": (40, 167, 69),        # 绿色（吉）
    "warning": (255, 193, 7),        # 橙色（平）
    "danger": (220, 53, 69),        # 红色（凶）
    "border": (200, 200, 220),       # 边框色
}


def _find_font():
    """查找可用的CJK字体"""
    for path in FONT_PATHS:
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No suitable CJK font found. Tried: {FONT_PATHS}")


def _ensure_font(pdf: fpdf.FPDF):
    """确保字体已注册到PDF"""
    global _font_registered, _font_info
    if _font_registered and _font_info:
        return

    font_path = _find_font()
    ext = os.path.splitext(font_path)[1].lower()

    if "STHeiti" in font_path:
        family = "STHeiti"
    elif "PingFang" in font_path:
        family = "PingFang"
    elif "Hiragino" in font_path:
        family = "Hiragino"
    elif "Noto" in font_path:
        family = "NotoSansSC"
    else:
        family = os.path.splitext(os.path.basename(font_path))[0]

    subfont_index = 0
    if ext == ".ttc":
        subfont_index = 0

    pdf.add_font(
        family=family,
        style="",
        fname=font_path,
        collection_font_number=subfont_index,
    )

    _font_info = (family, font_path, subfont_index)
    _font_registered = True


def markdown_to_pdf(
    markdown_text: str,
    title: str = "紫微斗数运势预测报告",
    output_path: Optional[str] = None,
    author: str = "FengxianCyberTaoist",
    charts: Optional[dict] = None,
    user_info: Optional[dict] = None,
    heatmap: Optional[bytes] = None,
    monthly_advice: Optional[List[dict]] = None,
) -> bytes:
    """
    将 Markdown 内容转换为 PDF（优雅样式）

    Args:
        markdown_text: Markdown 格式的报告内容
        title: 报告标题
        output_path: 输出文件路径
        author: 作者
        charts: 图表字典
        user_info: 用户信息
        heatmap: 热力图图片数据
        monthly_advice: 月度行动建议列表

    Returns:
        PDF 字节数据
    """
    pdf = _PDFWithCJK()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)

    # 注册字体
    _ensure_font(pdf)
    family = _font_info[0]

    # 封面页
    pdf.add_page()
    _render_cover(pdf, title, family, user_info)

    # 用户信息详情页
    if user_info:
        pdf.add_page()
        _render_user_detail_page(pdf, user_info, family)

    # 图表页 - 每页只放一个图表，避免错乱
    if charts:
        _render_charts_pages(pdf, charts, family)

    # 热力图页
    if heatmap:
        pdf.add_page()
        _render_heatmap_page(pdf, heatmap, family)

    # 月度行动清单
    if monthly_advice:
        pdf.add_page()
        _render_monthly_action_page(pdf, monthly_advice, family)

    # 内容页
    blocks = _parse_markdown(markdown_text)
    for block in blocks:
        _render_block(pdf, block, family)

    if output_path:
        pdf.output(output_path)
        return b""
    else:
        buf = BytesIO()
        pdf.output(buf)
        return buf.getvalue()


def _render_cover(pdf: fpdf.FPDF, title: str, family: str, user_info: Optional[dict] = None):
    """渲染优雅封面"""
    pdf.w - pdf.l_margin - pdf.r_margin

    # 顶部装饰线
    pdf.set_draw_color(*COLORS["accent"])
    pdf.set_line_width(3)
    pdf.line(pdf.l_margin, 30, pdf.w - pdf.r_margin, 30)

    pdf.ln(40)

    # 主标题
    pdf.set_font(family, size=28)
    pdf.set_text_color(*COLORS["primary"])
    pdf.multi_cell(0, 14, _clean_text(title), align="C")

    pdf.ln(10)

    # 副标题
    pdf.set_font(family, size=14)
    pdf.set_text_color(*COLORS["secondary"])
    pdf.multi_cell(0, 10, "FengxianCyberTaoist 紫微斗数智能分析系统", align="C")

    pdf.ln(30)

    # 用户信息卡片（简洁版）
    if user_info:
        _render_simple_user_card(pdf, user_info, family)

    pdf.ln(20)

    # 装饰分隔线
    _render_decorative_divider(pdf)

    # 系统信息
    pdf.ln(15)
    pdf.set_font(family, size=10)
    pdf.set_text_color(*COLORS["text_secondary"])
    from datetime import datetime
    now = datetime.now()
    footer = f"报告生成时间: {now.strftime('%Y年%m月%d日')}  |  Powered by FengxianCyberTaoist"
    pdf.cell(0, 6, footer, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 底部装饰线
    pdf.ln(10)
    pdf.set_draw_color(*COLORS["accent"])
    pdf.set_line_width(3)
    pdf.line(pdf.l_margin, pdf.h - 30, pdf.w - pdf.r_margin, pdf.h - 30)


def _render_simple_user_card(pdf: fpdf.FPDF, user_info: dict, family: str):
    """渲染简洁用户卡片"""
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    card_x = pdf.l_margin + 20
    card_width = page_width - 40

    # 卡片背景
    pdf.set_fill_color(*COLORS["surface"])
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(1)
    pdf.rect(card_x, pdf.get_y(), card_width, 35, style="FD")

    inner_x = card_x + 15
    inner_y = pdf.get_y() + 8

    # 姓名
    pdf.set_xy(inner_x, inner_y)
    pdf.set_font(family, size=16)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(card_width - 30, 10, f"命主: {user_info.get('name', '命主')}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 年份
    pdf.set_x(inner_x)
    pdf.set_font(family, size=12)
    pdf.set_text_color(*COLORS["secondary"])
    pdf.cell(card_width - 30, 8, f"{user_info.get('year', '2026')}年运势预测", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _render_user_detail_page(pdf: fpdf.FPDF, user_info: dict, family: str):
    """渲染用户详情页"""
    pdf.w - pdf.l_margin - pdf.r_margin

    # 标题
    pdf.ln(10)
    pdf.set_font(family, size=18)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(0, 12, "命盘信息概览", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)

    # 分隔线
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(1)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
    pdf.ln(15)

    # 信息卡片
    items = [
        ("命主姓名", user_info.get('name', '未知')),
        ("预测年份", f"{user_info.get('year', '2026')}年"),
        ("出生信息", user_info.get('birth', '未提供')),
        ("综合判断", user_info.get('judgment', '运势平稳')),
    ]

    for label, value in items:
        _render_info_row(pdf, label, value, family)
        pdf.ln(8)


def _render_info_row(pdf: fpdf.FPDF, label: str, value: str, family: str):
    """渲染信息行"""
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font(family, size=11)
    pdf.set_text_color(*COLORS["text_secondary"])
    pdf.cell(40, 8, f"{label}: ", new_x=XPos.RIGHT, new_y=YPos.TOP)

    pdf.set_font(family, size=12)
    pdf.set_text_color(*COLORS["text"])
    pdf.cell(page_width - 40, 8, _clean_text(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _render_decorative_divider(pdf: fpdf.FPDF):
    """渲染装饰分隔线"""
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    center_x = page_width / 2 + pdf.l_margin

    # 中心装饰
    pdf.set_fill_color(*COLORS["accent"])
    pdf.circle(center_x, pdf.get_y() + 2, 4, style="F")

    # 左右线条
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(1)
    pdf.line(pdf.l_margin + 40, pdf.get_y() + 2, center_x - 10, pdf.get_y() + 2)
    pdf.line(center_x + 10, pdf.get_y() + 2, pdf.w - pdf.r_margin - 40, pdf.get_y() + 2)

    pdf.ln(10)


def _render_charts_pages(pdf: fpdf.FPDF, charts: dict, family: str):
    """渲染图表页 - 每页一个图表，避免错乱"""
    chart_list = [
        ("radar", "五维运势雷达图", charts.get("radar")),
        ("timeline", "全年运势走势图", charts.get("timeline")),
        ("bar", "月度运势柱状图", charts.get("bar")),
        ("gauge", "预测置信度", charts.get("gauge")),
    ]

    for key, title, image_data in chart_list:
        if image_data:
            pdf.add_page()
            _render_single_chart(pdf, title, image_data, family)


def _render_single_chart(pdf: fpdf.FPDF, title: str, image_data: bytes, family: str):
    """渲染单个图表页面"""
    from PIL import Image
    from io import BytesIO as PILBytesIO

    # 页面标题
    pdf.ln(10)
    pdf.set_font(family, size=18)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(0, 12, title, align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(15)

    # 计算图片尺寸
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    img = Image.open(PILBytesIO(image_data))
    img_width, img_height = img.size

    # 按宽度自适应
    max_width = page_width * 0.85
    scale = max_width / img_width
    render_width = img_width * scale
    render_height = img_height * scale

    # 最大高度限制
    max_height = pdf.h - pdf.get_y() - 40
    if render_height > max_height:
        scale = max_height / img_height
        render_width = img_width * scale
        render_height = max_height

    # 居中放置
    x = pdf.l_margin + (page_width - render_width) / 2

    pdf.image(PILBytesIO(image_data), x=x, w=render_width)


def _render_heatmap_page(pdf: fpdf.FPDF, image_data: bytes, family: str):
    """渲染热力图页面"""
    from PIL import Image
    from io import BytesIO as PILBytesIO

    # 标题
    pdf.ln(10)
    pdf.set_font(family, size=18)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(0, 12, "年度运势热力图", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(15)

    # 计算图片尺寸
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    img = Image.open(PILBytesIO(image_data))
    img_width, img_height = img.size

    max_width = page_width * 0.9
    scale = max_width / img_width
    render_width = img_width * scale
    render_height = img_height * scale

    max_height = pdf.h - pdf.get_y() - 40
    if render_height > max_height:
        scale = max_height / img_height
        render_width = img_width * scale
        render_height = max_height

    x = pdf.l_margin + (page_width - render_width) / 2

    pdf.image(PILBytesIO(image_data), x=x, w=render_width)


def _render_monthly_action_page(pdf: fpdf.FPDF, monthly_data: List[dict], family: str):
    """渲染月度行动清单页面"""
    # 标题
    pdf.ln(10)
    pdf.set_font(family, size=18)
    pdf.set_text_color(*COLORS["primary"])
    pdf.cell(0, 12, "月度行动指南", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(10)

    # 渲染每月卡片
    for month_entry in monthly_data:
        _render_monthly_card(pdf, month_entry, family)


def _render_monthly_card(pdf: fpdf.FPDF, monthly_data: dict, family: str):
    """渲染单个月份的行动卡片"""
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    month = monthly_data.get("month", "")
    fortune_score = monthly_data.get("fortune_score", 3.5)
    fortune_label = monthly_data.get("fortune_label", "平")
    yi_list = monthly_data.get("yi", [])
    ji_list = monthly_data.get("ji", [])
    finance = monthly_data.get("finance", "")
    health = monthly_data.get("health", "")

    # 卡片背景
    pdf.ln(5)
    start_y = pdf.get_y()

    pdf.set_fill_color(*COLORS["surface"])
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(0.5)

    # 计算卡片高度
    card_height = 45 + (len(yi_list) + len(ji_list)) * 5

    # 检查是否需要换页
    if start_y + card_height > pdf.h - 30:
        pdf.add_page()
        start_y = pdf.get_y()

    pdf.rect(pdf.l_margin, start_y, page_width, card_height, style="FD")

    inner_x = pdf.l_margin + 10
    inner_width = page_width - 20

    # 月份标题
    pdf.set_xy(inner_x, start_y + 5)
    pdf.set_font(family, size=14)
    pdf.set_text_color(*COLORS["primary"])

    # 根据运势标签设置颜色
    if fortune_label in ["吉", "大吉"]:
        pdf.set_text_color(*COLORS["success"])
    elif fortune_label == "凶":
        pdf.set_text_color(*COLORS["danger"])
    else:
        pdf.set_text_color(*COLORS["warning"])

    pdf.cell(inner_width, 8, f"{month}月", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 运势标签
    pdf.set_x(inner_x)
    pdf.set_font(family, size=10)
    pdf.set_text_color(*COLORS["text_secondary"])
    pdf.cell(inner_width, 6, f"运势评分: {fortune_score:.1f}/5.0  ({fortune_label})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 宜
    pdf.set_x(inner_x)
    pdf.set_font(family, size=10)
    pdf.set_text_color(*COLORS["success"])
    yi_text = "、".join(yi_list[:4]) if yi_list else "顺势而为"
    pdf.multi_cell(inner_width, 5, f"【宜】{_clean_text(yi_text)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 忌
    pdf.set_x(inner_x)
    pdf.set_font(family, size=10)
    pdf.set_text_color(*COLORS["danger"])
    ji_text = "、".join(ji_list[:4]) if ji_list else "谨慎行事"
    pdf.multi_cell(inner_width, 5, f"【忌】{_clean_text(ji_text)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 理财建议
    if finance:
        pdf.set_x(inner_x)
        pdf.set_font(family, size=9)
        pdf.set_text_color(*COLORS["text"])
        pdf.multi_cell(inner_width, 5, f"理财: {_clean_text(finance)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 健康建议
    if health:
        pdf.set_x(inner_x)
        pdf.set_font(family, size=9)
        pdf.set_text_color(*COLORS["text"])
        pdf.multi_cell(inner_width, 5, f"健康: {_clean_text(health)}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)


def _render_block(pdf: fpdf.FPDF, block: dict, family: str):
    """渲染单个Markdown块"""
    bt = block["type"]

    if bt == "blank":
        pdf.ln(3)
        return

    if bt == "h1":
        pdf.ln(8)
        # 左侧装饰条
        pdf.set_fill_color(*COLORS["primary"])
        pdf.rect(pdf.l_margin, pdf.get_y(), 4, 8, style="F")
        pdf.set_font(family, size=15)
        pdf.set_text_color(*COLORS["primary"])
        pdf.set_x(pdf.l_margin + 10)
        pdf.cell(0, 8, _clean_text(block["content"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(4)
        return

    if bt == "h2":
        pdf.ln(6)
        pdf.set_font(family, size=13)
        pdf.set_text_color(*COLORS["secondary"])
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 8, _clean_text(block["content"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        return

    if bt == "h3":
        pdf.ln(4)
        pdf.set_font(family, size=11)
        pdf.set_text_color(*COLORS["accent"])
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 7, _clean_text(block["content"]), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2)
        return

    if bt == "hr":
        pdf.ln(5)
        pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_draw_color(*COLORS["border"])
        pdf.set_line_width(0.5)
        pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())
        pdf.ln(8)
        return

    if bt == "code":
        _render_code_block(pdf, block["content"], family)
        return

    if bt == "table":
        _render_table(pdf, block["rows"], family)
        return

    if bt == "list":
        _render_list(pdf, block["items"], family)
        return

    if bt == "paragraph":
        _render_paragraph(pdf, block["content"], family)
        return


def _render_code_block(pdf: fpdf.FPDF, content: str, family: str):
    """渲染代码块"""
    pdf.ln(5)
    code = _strip_emoji(content)
    lines = code.split("\n")
    line_count = min(len(lines), 15)

    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    pdf.set_fill_color(45, 45, 65)
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(0.5)
    pdf.rect(pdf.l_margin, pdf.get_y(), page_width, line_count * 5 + 6, style="FD")

    pdf.set_font(family, size=8)
    pdf.set_text_color(200, 200, 220)
    pdf.set_x(pdf.l_margin + 4)
    for line in lines[:15]:
        pdf.set_x(pdf.l_margin + 4)
        pdf.cell(0, 5, line[:80], new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(8)


def _render_table(pdf: fpdf.FPDF, rows: List[str], family: str):
    """渲染表格"""
    if not rows:
        return

    data_rows = []
    for row in rows:
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        if all(re.match(r"^[-:\s]+$", c) for c in cells):
            continue
        data_rows.append([_strip_emoji(_clean_text(c)) for c in cells])

    if not data_rows:
        return

    num_cols = len(data_rows[0])
    page_width = pdf.w - pdf.l_margin - pdf.r_margin
    col_width = page_width / num_cols

    pdf.set_font(family, size=9)
    pdf.set_fill_color(*COLORS["primary"])
    pdf.set_text_color(*COLORS["text_light"])
    pdf.set_draw_color(*COLORS["border"])
    pdf.set_line_width(0.3)

    # 表头
    for cell in data_rows[0]:
        pdf.cell(col_width, 7, cell[:20], border=1, align="C", fill=True)
    pdf.ln()

    # 数据行
    for row_idx, row in enumerate(data_rows[1:]):
        if row_idx % 2 == 0:
            pdf.set_fill_color(*COLORS["surface"])
        else:
            pdf.set_fill_color(255, 255, 255)

        pdf.set_font(family, size=9)
        pdf.set_text_color(*COLORS["text"])

        for cell in row:
            pdf.cell(col_width, 6, cell[:20], border=1, align="C", fill=True)
        pdf.ln()

    pdf.ln(8)


def _render_list(pdf: fpdf.FPDF, items: List[str], family: str):
    """渲染列表"""
    pdf.set_font(family, size=10)
    page_width = pdf.w - pdf.l_margin - pdf.r_margin

    for item in items:
        cleaned = _clean_text(item)
        is_sub = item.startswith("  ") or item.startswith("\t")

        # 根据内容选择颜色
        bullet = "●"
        bullet_color = COLORS["text"]

        if any(kw in item for kw in ["吉", "好运", "机会", "收获", "把握"]):
            bullet_color = COLORS["success"]
        elif any(kw in item for kw in ["凶", "注意", "谨慎", "破财", "小人"]):
            bullet_color = COLORS["danger"]
        elif any(kw in item for kw in ["平", "稳定", "一般"]):
            bullet_color = COLORS["warning"]

        indent = 12 if is_sub else 8
        x = pdf.get_x()

        pdf.set_x(x + indent)
        pdf.set_text_color(*bullet_color)
        pdf.cell(8, 6, bullet, new_x=XPos.RIGHT, new_y=YPos.TOP)

        pdf.set_text_color(*COLORS["text"])
        pdf.set_font(family, size=9 if is_sub else 10)
        pdf.multi_cell(page_width - indent - 10, 6, cleaned)

    pdf.ln(3)


def _render_paragraph(pdf: fpdf.FPDF, content: str, family: str):
    """渲染段落"""
    cleaned = _clean_text(content)

    # 引用块
    if content.strip().startswith(">"):
        pdf.ln(3)
        page_width = pdf.w - pdf.l_margin - pdf.r_margin
        pdf.set_fill_color(248, 248, 255)
        pdf.set_draw_color(*COLORS["secondary"])
        pdf.set_line_width(1)
        pdf.set_left_margin(pdf.l_margin + 5)
        pdf.rect(pdf.l_margin, pdf.get_y(), page_width - 10, 18, style="FD")

        pdf.set_font(family, size=11)
        pdf.set_text_color(*COLORS["primary"])
        pdf.set_x(pdf.l_margin + 10)
        pdf.multi_cell(page_width - 20, 6, cleaned)
        pdf.set_left_margin(20)
        pdf.ln(6)
        return

    # 普通段落
    pdf.set_font(family, size=10)
    pdf.set_text_color(*COLORS["text"])
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, cleaned)
    pdf.ln(4)


def _strip_emoji(text: str) -> str:
    """移除emoji字符"""
    emoji_pattern = re.compile(
        r"[\U0001F600-\U0001F64F]"
        r"|[\U0001F300-\U0001F5FF]"
        r"|[\U0001F680-\U0001F6FF]"
        r"|[\U0001F1E0-\U0001F1FF]"
        r"|[\U0001F900-\U0001F9FF]"
        r"|[\U0001FA00-\U0001FAFF]"
        r"|[\U00002600-\U000026FF]"
        r"|[\u2640-\u2642]"
        r"|[\u2764]"
        r"|[\u2700-\u27BF]"
        r"|[\U0001F004\U0001F0CF]"
        r"|\ufe0f|\ufe0e"
    )
    return emoji_pattern.sub("", text)


def _clean_text(text: str) -> str:
    """清理Markdown标记"""
    text = text.replace("\ufe0f", "").replace("\ufe0e", "")
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"__(.+?)__", r"\1", text)
    text = re.sub(r"_(.+?)_", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[-*•+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
    return text.strip()


def _parse_markdown(text: str) -> List[dict]:
    """解析Markdown为块列表"""
    text = text.replace("\ufe0f", "").replace("\ufe0e", "")
    lines = text.strip().split("\n")
    blocks = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            blocks.append({"type": "blank"})
            i += 1
            continue

        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            blocks.append({"type": "code", "lang": lang, "content": "\n".join(code_lines)})
            i += 1
            continue

        if stripped.startswith("# ") and not stripped.startswith("##"):
            blocks.append({"type": "h1", "content": stripped[2:]})
            i += 1
            continue

        if stripped.startswith("## ") and not stripped.startswith("###"):
            blocks.append({"type": "h2", "content": stripped[3:]})
            i += 1
            continue

        if stripped.startswith("### "):
            blocks.append({"type": "h3", "content": stripped[4:]})
            i += 1
            continue

        if stripped.startswith("---") or stripped.startswith("***"):
            blocks.append({"type": "hr"})
            i += 1
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            table_lines = [stripped]
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            blocks.append({"type": "table", "rows": table_lines})
            continue

        if re.match(r"^\s*[-*•+] ", stripped) or re.match(r"^\s*\d+\. ", stripped):
            list_items = []
            while i < len(lines):
                item_text = lines[i].strip()
                if not item_text:
                    break
                if re.match(r"^\s*[-*•+] ", item_text):
                    item_text = re.sub(r"^\s*[-*•+] ", "", item_text)
                elif re.match(r"^\s*\d+\. ", item_text):
                    item_text = re.sub(r"^\s*\d+\. ", "", item_text)
                else:
                    break
                list_items.append(item_text)
                i += 1
            if list_items:
                blocks.append({"type": "list", "items": list_items})
            continue

        para_lines = [stripped]
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if not next_line:
                break
            if next_line.startswith(("#", "-", "*", ">", "|", "```", "---")):
                break
            para_lines.append(next_line)
            j += 1
        blocks.append({"type": "paragraph", "content": " ".join(para_lines)})
        i = j

    return blocks


class _PDFWithCJK(fpdf.FPDF):
    """支持中文的PDF类"""

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("Helvetica", size=8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 5, f"Page {self.page_no()}", align="C")
