#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import os


def convert_txt_to_html(input_file, output_file, add_toc=True, css_file=None):
    """
    txt 파일을 HTML 파일로 변환합니다.
    - # 으로 시작하는 줄은 <h1> 태그로 변환
    - ## 으로 시작하는 줄은 <h2> 태그로 변환
    - ### 으로 시작하는 줄은 <h3> 태그로 변환 (이하 동일)
    - 모든 줄은 <p> 태그로 변환
    - 빈 줄은 <br /> 태그로 변환

    매개변수:
    - input_file: 입력 텍스트 파일 경로
    - output_file: 출력 HTML 파일 경로
    - add_toc: 목차 추가 여부 (기본값: True)
    - css_file: 외부 CSS 파일 경로 (기본값: None)
    """
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 헤딩 정보를 저장할 리스트 (목차 생성용)
    headings = []

    html_content = []
    html_content.append("<!DOCTYPE html>")
    html_content.append('<html lang="ko">')
    html_content.append("<head>")
    html_content.append('    <meta charset="UTF-8">')
    html_content.append(
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">'
    )

    # 첫 번째 줄을 제목으로 사용
    title = lines[0].strip() if lines else "변환된 HTML"
    html_content.append(f"    <title>{title}</title>")

    # CSS 스타일 추가
    if css_file and os.path.exists(css_file):
        html_content.append(f'    <link rel="stylesheet" href="{css_file}">')
    else:
        html_content.append("    <style>")
        html_content.append(
            "        body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }"
        )
        html_content.append(
            "        h1 { color: #333; text-align: center; margin-bottom: 30px; }"
        )
        html_content.append("        h2 { color: #444; margin-top: 20px; }")
        html_content.append("        h3 { color: #555; margin-top: 15px; }")
        html_content.append("        h4 { color: #666; margin-top: 10px; }")
        html_content.append("        h5 { color: #777; margin-top: 10px; }")
        html_content.append("        h6 { color: #888; margin-top: 10px; }")
        html_content.append("        p { margin-bottom: 10px; }")
        html_content.append(
            "        .toc { background-color: #f8f8f8; padding: 15px; border-radius: 5px; margin-bottom: 30px; }"
        )
        html_content.append("        .toc h2 { margin-top: 0; }")
        html_content.append("        .toc ul { padding-left: 20px; }")
        html_content.append("        .toc a { text-decoration: none; color: #0066cc; }")
        html_content.append("        .toc a:hover { text-decoration: underline; }")
        html_content.append("    </style>")

    html_content.append("</head>")
    html_content.append("<body>")

    # 목차 자리 표시 (나중에 채울 예정)
    if add_toc:
        toc_placeholder_index = len(html_content)
        html_content.append("<!-- TOC_PLACEHOLDER -->")

    heading_counter = 0

    for line in lines:
        line = line.strip()

        # 빈 줄은 <br /> 태그로 처리
        if not line:
            html_content.append("<br />")
            continue

        # 헤딩 처리 (# 스타일)
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            heading_level = len(heading_match.group(1))  # #의 개수
            heading_text = heading_match.group(2).strip()

            heading_counter += 1
            heading_id = f"heading_{heading_counter}"

            html_content.append(
                f'<h{heading_level} id="{heading_id}">{heading_text}</h{heading_level}>'
            )
            headings.append((heading_id, heading_text, heading_level))
        else:
            # 일반 텍스트는 <p> 태그로 처리
            html_content.append(f"<p>{line}</p>")

    # 목차 생성
    if add_toc and headings:
        toc_html = ['<div class="toc">']
        toc_html.append("<h2>목차</h2>")
        toc_html.append("<ul>")

        for heading_id, heading_text, level in headings:
            # 제목이 너무 길면 잘라서 표시
            short_heading = (
                heading_text[:50] + "..." if len(heading_text) > 50 else heading_text
            )
            indent = "    " * (level - 1)
            toc_html.append(
                f'{indent}<li><a href="#{heading_id}">{short_heading}</a></li>'
            )

        toc_html.append("</ul>")
        toc_html.append("</div>")

        # 목차 자리에 실제 목차 삽입
        html_content[toc_placeholder_index] = "\n".join(toc_html)

    html_content.append("</body>")
    html_content.append("</html>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_content))

    print(f"변환 완료: {input_file} -> {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="텍스트 파일을 HTML로 변환합니다.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input.txt",
        help="입력 텍스트 파일 경로 (기본값: input.txt)",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="output.html",
        help="출력 HTML 파일 경로 (기본값: output.html)",
    )
    parser.add_argument(
        "--no-toc", action="store_true", help="목차를 생성하지 않습니다."
    )
    parser.add_argument("--css", help="외부 CSS 파일 경로")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"오류: 입력 파일 '{args.input_file}'을 찾을 수 없습니다.")
        return 1

    convert_txt_to_html(
        args.input_file, args.output_file, add_toc=not args.no_toc, css_file=args.css
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
