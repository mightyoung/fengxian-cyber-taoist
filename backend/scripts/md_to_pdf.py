#!/usr/bin/env python3
"""将Markdown转换为PDF"""

import argparse
import markdown
from weasyprint import HTML, CSS


def convert_md_to_pdf(md_file, output_file):
    """将Markdown文件转换为PDF"""

    # 读取Markdown内容
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 转换为HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc']
    )

    # 添加样式
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            body {{
                font-family: "PingFang SC", "Microsoft YaHei", "SimHei", sans-serif;
                font-size: 12pt;
                line-height: 1.6;
                color: #333;
            }}
            h1 {{
                font-size: 24pt;
                color: #1E2761;
                border-bottom: 2px solid #1E2761;
                padding-bottom: 10px;
                text-align: center;
            }}
            h2 {{
                font-size: 18pt;
                color: #2C5F2D;
                margin-top: 20pt;
                border-left: 4px solid #2C5F2D;
                padding-left: 10px;
            }}
            h3 {{
                font-size: 14pt;
                color: #065A82;
                margin-top: 15pt;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15pt 0;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8pt;
                text-align: left;
            }}
            th {{
                background-color: #1E2761;
                color: white;
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            strong {{
                color: #990011;
            }}
            .warning {{
                background-color: #FFF3CD;
                border-left: 4px solid #FFC107;
                padding: 10pt;
                margin: 10pt 0;
            }}
            .info {{
                background-color: #D1ECF1;
                border-left: 4px solid #17A2B8;
                padding: 10pt;
                margin: 10pt 0;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2pt 4pt;
                border-radius: 3pt;
                font-family: Consolas, monospace;
            }}
            blockquote {{
                border-left: 4px solid #6D2E46;
                margin: 10pt 0;
                padding: 10pt 20pt;
                background-color: #FCF6F5;
                color: #6D2E46;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """

    # 生成PDF
    HTML(string=styled_html).write_pdf(output_file, stylesheets=[CSS(string='''
        @page {{
            size: A4;
            margin: 2cm;
        }}
    ''')])

    print(f"PDF已生成: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='将Markdown转换为PDF')
    parser.add_argument('input', help='输入的Markdown文件')
    parser.add_argument('output', help='输出的PDF文件')
    args = parser.parse_args()

    convert_md_to_pdf(args.input, args.output)
