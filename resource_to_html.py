#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import re
import shutil
import markdown
from pathlib import Path
from bs4 import BeautifulSoup


def read_metadata(metadata_file):
    """
    metadata.json 파일을 읽어 책 정보를 가져옵니다.
    """
    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    return metadata


def process_markdown_content(content_file):
    """
    마크다운 파일을 읽고 처리합니다.
    1. 빈줄은 <br />로 변환
    2. 연속된 줄바꿈은 최대 2회로 제한
    3. 마크다운 규칙에 따라 HTML로 파싱
    4. 모든 라인은 <p> 태그로 감싸짐
    """
    with open(content_file, "r", encoding="utf-8") as f:
        content = f.read()

    # 연속된 줄바꿈 최대 2회로 제한
    content = re.sub(r"\n{3,}", "\n\n", content)

    # 각 줄을 개별적으로 처리
    lines = content.split("\n")
    html_lines = []

    for line in lines:
        # 빈 줄은 <br /> 태그로 변환
        if not line.strip():
            html_lines.append("<br />")
        # 헤딩(#으로 시작하는 줄)은 그대로 처리
        elif re.match(r"^#+\s+", line):
            # 마크다운 헤딩을 HTML로 변환
            heading_match = re.match(r"^(#+)\s+(.+)$", line)
            if heading_match:
                heading_level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()
                html_lines.append(
                    f"<h{heading_level}>{heading_text}</h{heading_level}>"
                )
        # 수평선(---, ___, ***)은 <hr> 태그로 변환
        elif re.match(r"^(\*{3,}|-{3,}|_{3,})$", line.strip()):
            html_lines.append("<hr />")
        # 일반 텍스트 줄은 <p> 태그로 감싸기
        else:
            # 마크다운 문법 처리 (굵게, 기울임 등)
            # 굵게 (**text**)
            line = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", line)
            # 기울임 (*text*)
            line = re.sub(r"\*(.*?)\*", r"<em>\1</em>", line)
            # 각 줄을 <p> 태그로 감싸기
            html_lines.append(f"<p>{line}</p>")

    # 모든 HTML 줄을 합치기
    html_content = "\n".join(html_lines)

    return html_content


def create_title_page(metadata):
    """
    책 제목 페이지 HTML을 생성합니다.
    """
    html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('language', 'ko')}" lang="{metadata.get('language', 'ko')}">
<head>
    <meta charset="UTF-8" />
    <title>{metadata.get('title', '제목 없음')}</title>
    <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <div class="title-page">
        <h1 class="title">{metadata.get('title', '제목 없음')}</h1>
        <p class="author">{metadata.get('creator', '저자 미상')}</p>
        <p class="publisher">{metadata.get('publisher', '')}</p>
    </div>
</body>
</html>"""
    return html


def create_chapter_html(title, content, chapter_num):
    """
    챕터 내용을 HTML로 변환합니다.
    """
    html = "<!DOCTYPE html>\n"
    html += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
    html += "<head>\n"
    html += f'    <meta charset="UTF-8" />\n'
    html += f"    <title>{title}</title>\n"
    html += f'    <link rel="stylesheet" type="text/css" href="style.css" />\n'
    html += "</head>\n"
    html += "<body>\n"
    html += '    <div class="chapter">\n'

    # 챕터 제목을 h1 태그로 추가 (이미 content에 있는 경우 제외)
    if title and not content.strip().startswith(f"<h1>{title}</h1>"):
        html += f"        <h1>{title}</h1>\n"

    html += f"        {content}\n"
    html += "    </div>\n"
    html += "</body>\n"
    html += "</html>"

    return html


def create_toc_html(metadata, chapters):
    """
    목차 HTML을 생성합니다.
    """
    toc_items = ""
    for i, title in enumerate(chapters):
        toc_items += f'<li><a href="chapter_{i+1}.html">{title}</a></li>\n'

    html = f"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{metadata.get('language', 'ko')}" lang="{metadata.get('language', 'ko')}">
<head>
    <meta charset="UTF-8" />
    <title>목차</title>
    <link rel="stylesheet" type="text/css" href="style.css" />
</head>
<body>
    <div class="toc">
        <h1>목차</h1>
        <ul>
            {toc_items}
        </ul>
    </div>
</body>
</html>"""
    return html


def create_css():
    """
    스타일시트를 생성합니다.
    """
    css = """body {
    margin: 1em;
    font-family: 'Noto Sans KR', sans-serif;
    line-height: 1.6;
}

.title-page {
    text-align: center;
    margin: 3em auto;
}

.title {
    font-size: 2em;
    margin-bottom: 1em;
}

.author {
    font-size: 1.5em;
    margin-bottom: 0.5em;
}

.publisher {
    font-size: 1.2em;
    color: #666;
}

.toc {
    margin: 2em;
}

.toc ul {
    list-style-type: none;
    padding-left: 1em;
}

.toc li {
    margin-bottom: 0.5em;
}

.chapter {
    margin: 1em;
}

h1, h2, h3, h4, h5, h6 {
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

p {
    margin-bottom: 1em;
    text-indent: 1em;
}

/* 첫 번째 문단은 들여쓰기 없음 */
h1 + p, h2 + p, h3 + p, h4 + p, h5 + p, h6 + p {
    text-indent: 0;
}

strong, b {
    font-weight: bold;
}

em, i {
    font-style: italic;
}
"""
    return css


def extract_chapters(html_content):
    """
    HTML 내용에서 챕터를 추출합니다.
    h1 태그를 기준으로 챕터를 나눕니다.
    """
    # h1 태그로 분할
    chapter_pattern = r"<h1>(.*?)</h1>(.*?)(?=<h1>|$)"
    chapters = re.findall(chapter_pattern, html_content, re.DOTALL)

    # 챕터가 없으면 전체를 하나의 챕터로 처리
    if not chapters:
        return [("내용", html_content)]

    # 각 챕터에 h1 태그를 포함시킴
    processed_chapters = []
    for title, content in chapters:
        processed_chapters.append((title, f"<h1>{title}</h1>{content}"))

    return processed_chapters


def convert_resource_to_html(resource_dir, output_dir):
    """
    resource 폴더의 데이터를 HTML로 변환합니다.
    """
    # 경로 설정
    resource_path = Path(resource_dir)
    metadata_file = resource_path / "metadata.json"
    content_file = resource_path / "content.md"
    cover_file = resource_path / "cover.jpg"
    css_file = resource_path / "style.css"

    # 출력 디렉토리 생성
    output_path = Path(output_dir)
    if output_path.exists():
        shutil.rmtree(output_path)
    output_path.mkdir(parents=True)

    # 메타데이터 읽기
    metadata = read_metadata(metadata_file)

    # 마크다운 내용 처리
    html_content = process_markdown_content(content_file)

    # 챕터 추출
    chapters = extract_chapters(html_content)
    chapter_titles = [title for title, _ in chapters]

    # CSS 파일 복사 또는 생성
    if css_file.exists():
        shutil.copy(css_file, output_path / "style.css")
        print(f"CSS 파일을 복사했습니다: {css_file} -> {output_path / 'style.css'}")
    else:
        with open(output_path / "style.css", "w", encoding="utf-8") as f:
            f.write(create_css())
            print("기본 CSS 파일을 생성했습니다.")

    # 표지 이미지 복사
    if cover_file.exists():
        shutil.copy(cover_file, output_path / "cover.jpg")

    # 제목 페이지 생성
    with open(output_path / "title.html", "w", encoding="utf-8") as f:
        f.write(create_title_page(metadata))

    # 목차 페이지 생성
    with open(output_path / "toc.html", "w", encoding="utf-8") as f:
        f.write(create_toc_html(metadata, chapter_titles))

    # 각 챕터 HTML 파일 생성
    for i, (title, content) in enumerate(chapters):
        chapter_filename = f"chapter_{i+1}.html"
        chapter_content = create_chapter_html(title, content, i + 1)

        with open(output_path / chapter_filename, "w", encoding="utf-8") as f:
            f.write(chapter_content)

    print(f"변환 완료: {resource_dir} -> {output_dir}/")
    print(f"총 {len(chapters)}개의 챕터가 생성되었습니다.")

    return output_dir


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="resource 폴더의 데이터를 HTML로 변환합니다."
    )
    parser.add_argument(
        "--resource-dir",
        default="resource",
        help="리소스 디렉토리 경로 (기본값: resource)",
    )
    parser.add_argument(
        "--output-dir",
        default="output_html",
        help="출력 디렉토리 경로 (기본값: output_html)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.resource_dir):
        print(f"오류: 리소스 디렉토리 '{args.resource_dir}'을 찾을 수 없습니다.")
        return 1

    convert_resource_to_html(args.resource_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
