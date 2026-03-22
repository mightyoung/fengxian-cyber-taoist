"""
运势图表生成器 - 使用 matplotlib 生成可视化图表
支持雷达图、柱状图等，用于紫微斗数预测报告
"""

import os
import io
from typing import List, Tuple, Optional
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import FancyBboxPatch, Circle

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['STHeiti', 'PingFang SC', 'Hiragino Sans GB', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配色方案 - 神秘紫金主题
COLORS = {
    "primary": "#4A4A8A",        # 深紫色
    "secondary": "#7B68EE",       # 中紫色
    "accent": "#FFD700",          # 金色
    "background": "#1A1A2E",     # 深蓝黑
    "surface": "#252540",        # 浅紫黑
    "text": "#FFFFFF",           # 白色文字
    "text_secondary": "#B8B8D0",  # 灰紫色文字
    "success": "#50C878",        # 绿色（吉）
    "warning": "#FFA500",        # 橙色（平）
    "danger": "#FF6B6B",         # 红色（凶）
    "grid": "#3D3D5C",           # 网格线
}


def _hex_to_rgb(hex_color: str) -> Tuple[float]:
    """将十六进制颜色转换为RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))


def _rgb_to_hex(r, g, b) -> str:
    """将RGB转换为十六进制"""
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def generate_radar_chart(
    dimensions: List[str],
    scores: List[float],
    title: str = "五维运势雷达图",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (800, 600)
) -> Optional[bytes]:
    """
    生成雷达图

    Args:
        dimensions: 维度名称列表
        scores: 各维度得分 (0-5)
        title: 图表标题
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    if len(dimensions) != len(scores):
        return None

    # 创建图表
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    # 计算角度
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]  # 闭合

    # 闭合数据
    values = scores + [scores[0]]

    # 绘制网格
    for level in [1, 2, 3, 4, 5]:
        ax.plot(
            [level * np.cos(a) for a in angles],
            [level * np.sin(a) for a in angles],
            color=COLORS["grid"],
            linewidth=0.5,
            alpha=0.5
        )

    # 绘制数据区域
    ax.fill(
        angles,
        values,
        color=COLORS["secondary"],
        alpha=0.25
    )

    # 绘制数据线
    ax.plot(
        angles,
        values,
        color=COLORS["accent"],
        linewidth=2,
        marker='o',
        markersize=8,
        markerfacecolor=COLORS["accent"]
    )

    # 设置维度标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(dimensions, color=COLORS["text"], fontsize=10, fontweight='bold')

    # 设置径向刻度
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], color=COLORS["text_secondary"], fontsize=8)
    ax.set_ylim(0, 5.5)

    # 标题
    ax.set_title(title, color=COLORS["accent"], fontsize=14, fontweight='bold', pad=20)

    # 调整布局
    plt.tight_layout()

    # 保存或返回
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_bar_chart(
    labels: List[str],
    values: List[float],
    title: str = "月度运势走势",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (800, 400),
    color_map: Optional[dict] = None
) -> Optional[bytes]:
    """
    生成柱状图

    Args:
        labels: X轴标签
        values: Y轴值
        title: 图表标题
        output_path: 输出文件路径
        size: 图片尺寸
        color_map: 值到颜色的映射函数

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=COLORS["secondary"], alpha=0.8, edgecolor=COLORS["accent"], linewidth=1)

    # 根据值设置颜色
    if color_map:
        for bar, val in zip(bars, values):
            for threshold, color in sorted(color_map.items()):
                if val >= threshold:
                    bar.set_facecolor(color)

    # 添加数值标签
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.annotate(
            f'{val:.1f}',
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha='center', va='bottom',
            color=COLORS["text"],
            fontsize=9,
            fontweight='bold'
        )

    # 设置标签
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=COLORS["text"], fontsize=10, fontweight='bold')
    ax.set_ylabel('运势指数', color=COLORS["text_secondary"], fontsize=10)
    ax.set_ylim(0, max(values) * 1.2)

    # 网格线
    ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    # 标题
    ax.set_title(title, color=COLORS["accent"], fontsize=14, fontweight='bold', pad=15)

    # 去掉边框
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color(COLORS["grid"])

    ax.tick_params(colors=COLORS["text_secondary"])

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_star_distribution_chart(
    star_data: dict,
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (600, 400)
) -> Optional[bytes]:
    """
    生成星曜分布图

    Args:
        star_data: 星曜数据字典 {"星曜名称": 数量}
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    if not star_data:
        return None

    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    # 排序
    sorted_data = sorted(star_data.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_data]
    values = [item[1] for item in sorted_data]

    # 创建渐变颜色
    base_color = _hex_to_rgb(COLORS["secondary"])
    colors = []
    for i in range(len(values)):
        ratio = 1 - (i / len(values)) * 0.5
        r = min(1, base_color[0] * ratio + 0.3 * (1-ratio))
        g = min(1, base_color[1] * ratio + 0.2 * (1-ratio))
        b = min(1, base_color[2] * ratio + 0.4 * (1-ratio))
        colors.append((r, g, b))

    bars = ax.barh(labels, values, color=colors, alpha=0.8, edgecolor=COLORS["accent"], linewidth=0.5)

    # 数值标签
    for bar, val in zip(bars, values):
        ax.annotate(
            f'{val}',
            xy=(val, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha='left', va='center',
            color=COLORS["text"],
            fontsize=9,
            fontweight='bold'
        )

    ax.set_xlabel('数量', color=COLORS["text_secondary"], fontsize=10)
    ax.set_xlim(0, max(values) * 1.3)
    ax.invert_yaxis()

    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.5, alpha=0.5)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color(COLORS["grid"])

    ax.tick_params(colors=COLORS["text_secondary"])

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_palace_chart(
    palaces: List[str],
    transforms: List[str],
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (700, 700)
) -> Optional[bytes]:
    """
    生成宫位分布环形图

    Args:
        palaces: 宫位列表
        transforms: 各宫位的四化列表
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    # 统计四化类型
    transform_counts = {"化禄": 0, "化权": 0, "化科": 0, "化忌": 0, "无四化": 0}
    for t in transforms:
        if t in transform_counts:
            transform_counts[t] += 1
        else:
            transform_counts["无四化"] += 1

    labels = list(transform_counts.keys())
    sizes = list(transform_counts.values())

    # 颜色映射
    color_map_transform = {
        "化禄": "#50C878",  # 绿色
        "化权": "#7B68EE",  # 紫色
        "化科": "#FFD700",  # 金色
        "化忌": "#FF6B6B",  # 红色
        "无四化": "#4A4A8A"  # 深紫
    }
    colors = [color_map_transform.get(label, COLORS["secondary"]) for label in labels]

    # 环形图
    wedges, texts, autotexts = ax.pie(
        sizes,
        labels=None,
        colors=colors,
        autopct='%1.0f%%',
        pctdistance=0.75,
        startangle=90,
        wedgeprops=dict(width=0.4, edgecolor=COLORS["background"], linewidth=2)
    )

    # 设置百分比文字颜色
    for autotext in autotexts:
        autotext.set_color(COLORS["text"])
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    # 添加图例
    legend_labels = [f'{label} ({count})' for label, count in zip(labels, sizes)]
    ax.legend(
        wedges,
        legend_labels,
        loc="center left",
        bbox_to_anchor=(1, 0.5),
        prop={'size': 10},
        labelcolor=COLORS["text"]
    )

    ax.set_title('四化分布统计', color=COLORS["accent"], fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_timeline_chart(
    months: List[str],
    fortunes: List[str],  # "up", "down", "flat", "peak", "low"
    title: str = "运势时间线",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (900, 300)
) -> Optional[bytes]:
    """
    生成运势时间线图

    Args:
        months: 月份列表
        fortunes: 各月运势 ("up", "down", "flat", "peak", "low")
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    x = np.arange(len(months))

    # 将运势转换为数值
    fortune_values = {
        "peak": 5,
        "up": 4,
        "flat": 3,
        "down": 2,
        "low": 1
    }
    values = [fortune_values.get(f, 3) for f in fortunes]

    # 颜色映射
    fortune_colors = {
        "peak": "#FFD700",  # 金色
        "up": "#50C878",    # 绿色
        "flat": "#7B68EE", # 紫色
        "down": "#FFA500",  # 橙色
        "low": "#FF6B6B"    # 红色
    }
    colors = [fortune_colors.get(f, COLORS["secondary"]) for f in fortunes]

    # 绘制折线
    ax.plot(x, values, color=COLORS["accent"], linewidth=2, alpha=0.8, zorder=2)

    # 绘制点和颜色
    for i, (xi, yi, color) in enumerate(zip(x, values, colors)):
        circle = Circle((xi, yi), 0.2, facecolor=color, edgecolor=COLORS["text"], linewidth=1, zorder=3)
        ax.add_patch(circle)

    # 填充区域
    ax.fill_between(x, 0, values, color=COLORS["secondary"], alpha=0.1)

    # 设置
    ax.set_xticks(x)
    ax.set_xticklabels(months, color=COLORS["text"], fontsize=9, fontweight='bold')
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['低谷', '下行', '平稳', '上升', '高峰'], color=COLORS["text_secondary"], fontsize=8)
    ax.set_ylim(0, 6)
    ax.set_xlim(-0.5, len(months) - 0.5)

    # 网格
    ax.yaxis.grid(True, color=COLORS["grid"], linewidth=0.5, alpha=0.3)
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.tick_params(colors=COLORS["text_secondary"])

    # 图例
    legend_elements = [
        mpatches.Patch(color=fortune_colors["peak"], label='高峰'),
        mpatches.Patch(color=fortune_colors["up"], label='上升'),
        mpatches.Patch(color=fortune_colors["flat"], label='平稳'),
        mpatches.Patch(color=fortune_colors["down"], label='下行'),
        mpatches.Patch(color=fortune_colors["low"], label='低谷'),
    ]
    ax.legend(handles=legend_elements, loc='upper right', ncol=5, prop={'size': 8}, labelcolor=COLORS["text"])

    ax.set_title(title, color=COLORS["accent"], fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_confidence_gauge(
    value: float,
    label: str = "置信度",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (400, 300)
) -> Optional[bytes]:
    """
    生成置信度仪表盘

    Args:
        value: 置信度值 (0-100)
        label: 标签
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])

    # 计算角度
    theta = np.linspace(0, np.pi, 100)
    r = 1

    # 背景弧
    ax.fill_between(
        theta, 0.3, r,
        color=COLORS["grid"],
        alpha=0.3
    )

    # 渐变色带
    colors_gradient = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(theta)))
    for i in range(len(theta) - 1):
        color_idx = min(i, len(colors_gradient) - 1)
        ax.fill_between(
            theta[i:i+2], 0.5, r,
            color=colors_gradient[color_idx],
            alpha=0.5
        )

    # 指针
    value_normalized = min(100, max(0, value)) / 100
    needle_angle = np.pi * (1 - value_normalized)
    needle_x = [0, 0.7 * np.cos(needle_angle)]
    needle_y = [0, 0.7 * np.sin(needle_angle)]
    ax.plot(needle_x, needle_y, color=COLORS["text"], linewidth=3, zorder=10)

    # 中心圆
    center_circle = Circle((0, 0), 0.1, facecolor=COLORS["accent"], edgecolor=COLORS["text"], linewidth=2, zorder=11)
    ax.add_patch(center_circle)

    # 数值文字
    ax.text(
        0, -0.2,
        f'{value:.0f}%',
        ha='center', va='center',
        color=COLORS["accent"],
        fontsize=20,
        fontweight='bold'
    )

    # 标签
    ax.text(
        0, -0.35,
        label,
        ha='center', va='center',
        color=COLORS["text_secondary"],
        fontsize=12
    )

    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-0.5, 1.2)
    ax.set_aspect('equal')
    ax.axis('off')

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_monthly_heatmap(
    monthly_data: List[dict],
    title: str = "2026年每月运势热力图",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (800, 400)
) -> Optional[bytes]:
    """
    生成12月运势热力图

    Args:
        monthly_data: 每月运势数据列表，格式为 [{"month": "1月", "fortune": 3.5, "label": "吉"}, ...]
        title: 图表标题
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    if not monthly_data:
        return None

    # 颜色映射：运势值越高越金，越低越红
    fortune_colors = {
        "peak": "#FFD700",   # 金色 - 高峰
        "up": "#50C878",     # 绿色 - 上升
        "flat": "#7B68EE",   # 紫色 - 平稳
        "down": "#FFA500",   # 橙色 - 下行
        "low": "#FF6B6B",    # 红色 - 低谷
    }

    # 根据运势值确定颜色
    def get_color_by_value(fortune: float) -> str:
        if fortune >= 4.5:
            return fortune_colors["peak"]
        elif fortune >= 3.5:
            return fortune_colors["up"]
        elif fortune >= 2.5:
            return fortune_colors["flat"]
        elif fortune >= 1.5:
            return fortune_colors["down"]
        else:
            return fortune_colors["low"]

    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])
    fig.patch.set_facecolor(COLORS["background"])

    months = [d["month"] for d in monthly_data]
    fortunes = [d["fortune"] for d in monthly_data]
    labels = [d.get("label", "") for d in monthly_data]

    # 构建数据矩阵（3行4列布局）
    n_cols = 4
    n_rows = 3
    data_matrix = np.zeros((n_rows, n_cols))
    month_labels = []
    color_matrix = []

    for i, (month, fortune, label) in enumerate(zip(months, fortunes, labels)):
        row = i // n_cols
        col = i % n_cols
        data_matrix[row, col] = fortune
        month_labels.append(f"{month}\n{label}" if label else month)
        color_matrix.append(get_color_by_value(fortune))

    # 绘制热力图格子
    for i in range(n_rows):
        for j in range(n_cols):
            idx = i * n_cols + j
            if idx < len(monthly_data):
                fortune = fortunes[idx]
                color = get_color_by_value(fortune)
                label_text = labels[idx] if idx < len(labels) else ""

                # 绘制矩形
                rect = FancyBboxPatch(
                    (j + 0.05, n_rows - 1 - i + 0.05),
                    0.9, 0.9,
                    boxstyle="round,pad=0.02,rounding_size=0.1",
                    facecolor=color,
                    edgecolor=COLORS["text"],
                    linewidth=1,
                    alpha=0.85,
                    zorder=2
                )
                ax.add_patch(rect)

                # 添加月份文字
                ax.text(
                    j + 0.5, n_rows - 1 - i + 0.65,
                    months[idx],
                    ha='center', va='center',
                    color=COLORS["text"],
                    fontsize=11,
                    fontweight='bold',
                    zorder=3
                )

                # 添加运势值
                ax.text(
                    j + 0.5, n_rows - 1 - i + 0.35,
                    f"{fortune:.1f}",
                    ha='center', va='center',
                    color=COLORS["background"],
                    fontsize=10,
                    fontweight='bold',
                    zorder=3
                )

                # 添加标签（如果有）
                if label_text:
                    ax.text(
                        j + 0.5, n_rows - 1 - i + 0.15,
                        label_text,
                        ha='center', va='center',
                        color=COLORS["text"],
                        fontsize=7,
                        zorder=3
                    )

    # 添加图例
    legend_elements = [
        mpatches.Patch(color=fortune_colors["peak"], label='高峰(4.5+)'),
        mpatches.Patch(color=fortune_colors["up"], label='上升(3.5+)'),
        mpatches.Patch(color=fortune_colors["flat"], label='平稳(2.5+)'),
        mpatches.Patch(color=fortune_colors["down"], label='下行(1.5+)'),
        mpatches.Patch(color=fortune_colors["low"], label='低谷(<1.5)'),
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper right',
        ncol=5,
        prop={'size': 7},
        labelcolor=COLORS["text"],
        framealpha=0.5,
        facecolor=COLORS["surface"]
    )

    ax.set_xlim(-0.1, n_cols + 0.2)
    ax.set_ylim(-0.1, n_rows + 0.1)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.set_title(title, color=COLORS["accent"], fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


def generate_advice_comparison_chart(
    yi_list: List[str],
    ji_list: List[str],
    title: str = "每月宜忌对比",
    output_path: Optional[str] = None,
    size: Tuple[int, int] = (700, 400)
) -> Optional[bytes]:
    """
    生成宜/忌对比柱状图

    Args:
        yi_list: 宜的事项列表 ["把握机会", "稳健理财", ...]
        ji_list: 忌的事项列表 ["盲目投资", "过度冒险", ...]
        title: 图表标题
        output_path: 输出文件路径
        size: 图片尺寸

    Returns:
        PNG 图像数据 (bytes) 或 None
    """
    if not yi_list and not ji_list:
        return None

    fig, ax = plt.subplots(figsize=(size[0]/100, size[1]/100), dpi=100)
    ax.set_facecolor(COLORS["background"])
    fig.patch.set_facecolor(COLORS["background"])

    # 取较长列表的长度
    max_items = max(len(yi_list), len(ji_list), 1)

    # Y轴位置
    y_positions = np.arange(max_items)

    # 绘制"宜"柱（左侧，正值，绿色）
    if yi_list:
        yi_values = [1] * len(yi_list)
        yi_bars = ax.barh(
            y_positions[:len(yi_list)],
            yi_values,
            height=0.6,
            color=COLORS["success"],
            alpha=0.8,
            edgecolor=COLORS["text"],
            linewidth=0.5,
            zorder=2
        )
        # 添加文字标签
        for bar, text in zip(yi_bars, yi_list):
            ax.text(
                bar.get_width() + 0.05,
                bar.get_y() + bar.get_height() / 2,
                text,
                ha='left', va='center',
                color=COLORS["success"],
                fontsize=9,
                fontweight='bold'
            )

    # 绘制"忌"柱（右侧，负值，红色）
    if ji_list:
        ji_values = [-1] * len(ji_list)
        ji_bars = ax.barh(
            y_positions[:len(ji_list)],
            ji_values,
            height=0.6,
            color=COLORS["danger"],
            alpha=0.8,
            edgecolor=COLORS["text"],
            linewidth=0.5,
            zorder=2
        )
        # 添加文字标签
        for bar, text in zip(ji_bars, ji_list):
            ax.text(
                bar.get_width() - 0.05,
                bar.get_y() + bar.get_height() / 2,
                text,
                ha='right', va='center',
                color=COLORS["danger"],
                fontsize=9,
                fontweight='bold'
            )

    # 中心分隔线
    ax.axvline(x=0, color=COLORS["grid"], linewidth=1.5, zorder=3)

    # 中心标签
    ax.text(
        0, max_items - 0.3,
        "← 宜（好事）        忌（避免）→",
        ha='center', va='top',
        color=COLORS["text_secondary"],
        fontsize=9,
        style='italic'
    )

    # 设置坐标轴
    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-0.5, max_items - 0.5)

    # 隐藏Y轴刻度
    ax.set_yticks([])

    # X轴设置
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(['忌', '', '宜'], color=COLORS["text_secondary"], fontsize=10, fontweight='bold')

    # 网格线
    ax.xaxis.grid(True, color=COLORS["grid"], linewidth=0.5, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    # 去掉边框
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color(COLORS["grid"])
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color(COLORS["grid"])

    ax.tick_params(colors=COLORS["text_secondary"])

    # 添加图例
    legend_elements = [
        mpatches.Patch(color=COLORS["success"], label=f'宜 ({len(yi_list)}项)'),
        mpatches.Patch(color=COLORS["danger"], label=f'忌 ({len(ji_list)}项)'),
    ]
    ax.legend(
        handles=legend_elements,
        loc='upper right',
        ncol=2,
        prop={'size': 9},
        labelcolor=COLORS["text"],
        framealpha=0.5,
        facecolor=COLORS["surface"]
    )

    ax.set_title(title, color=COLORS["accent"], fontsize=14, fontweight='bold', pad=15)

    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=COLORS["background"], bbox_inches='tight', dpi=100)
    buf.seek(0)
    plt.close()

    if output_path:
        with open(output_path, 'wb') as f:
            f.write(buf.getvalue())

    return buf.getvalue()


if __name__ == "__main__":
    # 测试代码
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # 测试雷达图
        radar = generate_radar_chart(
            ["事业", "财运", "感情", "健康", "人际"],
            [4, 3, 4, 3, 4],
            "测试雷达图",
            os.path.join(tmpdir, "radar.png")
        )
        print(f"雷达图: {'生成成功' if radar else '失败'}")

        # 测试柱状图
        bar = generate_bar_chart(
            ["1月", "2月", "3月", "4月", "5月", "6月"],
            [3.5, 4.2, 3.8, 4.5, 4.0, 3.2],
            "月度运势",
            os.path.join(tmpdir, "bar.png"),
            color_map={4: "#50C878", 3: "#7B68EE", 2: "#FFA500"}
        )
        print(f"柱状图: {'生成成功' if bar else '失败'}")

        # 测试仪表盘
        gauge = generate_confidence_gauge(
            75,
            "预测置信度",
            os.path.join(tmpdir, "gauge.png")
        )
        print(f"仪表盘: {'生成成功' if gauge else '失败'}")

        # 测试热力图
        monthly_data = [
            {"month": "1月", "fortune": 4.5, "label": "吉"},
            {"month": "2月", "fortune": 3.8, "label": "吉"},
            {"month": "3月", "fortune": 3.2, "label": "平"},
            {"month": "4月", "fortune": 4.2, "label": "吉"},
            {"month": "5月", "fortune": 2.8, "label": "平"},
            {"month": "6月", "fortune": 1.8, "label": "凶"},
            {"month": "7月", "fortune": 4.0, "label": "吉"},
            {"month": "8月", "fortune": 3.5, "label": "吉"},
            {"month": "9月", "fortune": 2.5, "label": "平"},
            {"month": "10月", "fortune": 4.8, "label": "大吉"},
            {"month": "11月", "fortune": 3.0, "label": "平"},
            {"month": "12月", "fortune": 1.2, "label": "凶"},
        ]
        heatmap = generate_monthly_heatmap(
            monthly_data,
            "2026年每月运势热力图",
            os.path.join(tmpdir, "heatmap.png")
        )
        print(f"热力图: {'生成成功' if heatmap else '失败'}")

        # 测试宜忌对比图
        yi_list = ["把握机会", "稳健理财", "拓展人脉", "学习新知", "低调行事"]
        ji_list = ["盲目投资", "过度冒险", "感情冲动", "消极懈怠", "口舌是非"]
        advice = generate_advice_comparison_chart(
            yi_list,
            ji_list,
            "每月宜忌对比",
            os.path.join(tmpdir, "advice.png")
        )
        print(f"宜忌对比图: {'生成成功' if advice else '失败'}")

        print(f"\n测试文件保存在: {tmpdir}")
