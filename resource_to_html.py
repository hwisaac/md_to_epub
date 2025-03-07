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


def read_colophon(colophon_file):
    """
    colophon.json 파일을 읽어 판권 정보를 가져옵니다.
    """
    with open(colophon_file, "r", encoding="utf-8") as f:
        colophon = json.load(f)
    return colophon


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
    css = """
@font-face {
    font-family: 'Pretendard';
    src: url('fonts/PretendardVariable.woff2') format('woff2');
    font-weight: 100 900;
    font-style: normal;
}

body {
    font-family: 'Pretendard', sans-serif;
    margin: 5%;
    text-align: justify;
    line-height: 1.6;
}

h1 {
    text-align: center;
    font-size: 1.5em;
    font-weight: bold;
    margin-bottom: 1em;
    color: #333;
}

h2 {
    text-align: left;
    font-size: 1.2em;
    font-weight: bold;
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: #444;
}

h3 {
    font-size: 1.1em;
    margin-top: 0.8em;
    color: #555;
}

h4, h5, h6 {
    font-size: 1em;
    margin-top: 0.6em;
    color: #666;
}

p {
    margin-top: 0.5em;
    margin-bottom: 0.5em;
}

.title-page {
    text-align: center;
}

.title-page h1 {
    margin-top: 30%;
    font-size: 2em;
}

.title-page .author {
    margin-top: 3em;
    font-style: italic;
}

.title-page .date {
    margin-top: 1em;
    font-size: 0.9em;
    color: #666;
}

.toc ol {
    padding-left: 2em;
}

.toc li {
    margin-bottom: 0.5em;
}

.toc a {
    text-decoration: none;
    color: #0066cc;
}

.toc a:hover {
    text-decoration: underline;
}

ul{
    list-style-type: none;
}
hr{
  background-color: #fff;
  padding: 0;
  margin: 80px;
  border: 0;
  height: 1px;
  background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(0, 0, 0, 0.75), rgba(0, 0, 0, 0));
}
"""
    return css


def create_colophon_html(colophon):
    """
    판권 페이지 HTML을 생성합니다.
    """
    html = "<!DOCTYPE html>\n"
    html += '<html xmlns="http://www.w3.org/1999/xhtml">\n'
    html += "<head>\n"
    html += '    <meta charset="UTF-8" />\n'
    html += "    <title>판권</title>\n"
    html += '    <link rel="stylesheet" type="text/css" href="style.css" />\n'
    html += "</head>\n"
    html += "<body>\n"
    html += '    <div class="colophon">\n'

    # 제목
    if "title" in colophon:
        html += f'        <h1>{colophon["title"]}</h1>\n'

    # 초판 발행일
    if "first_published" in colophon:
        html += f'        <p><span class="label">초판 발행</span> {colophon["first_published"]}</p>\n'

    # 저자
    if "author" in colophon:
        html += (
            f'        <p><span class="label">지은이</span> {colophon["author"]}</p>\n'
        )

    # 번역자
    if "translator" in colophon:
        html += f'        <p><span class="label">옮긴이</span> {colophon["translator"]}</p>\n'

    # 발행인
    if "publisher" in colophon and "editor" in colophon["publisher"]:
        html += f'        <p><span class="label">발행인</span> {colophon["publisher"]["editor"]}</p>\n'

    # 출판사
    if "publisher" in colophon and "name" in colophon["publisher"]:
        html += f'        <p><span class="label">발행처</span> {colophon["publisher"]["name"]}</p>\n'

    # 출판 등록 정보
    if "publication_registration" in colophon:
        reg = colophon["publication_registration"]
        if "date" in reg and "number" in reg:
            html += f'        <p><span class="label">출판등록</span> {reg["date"]} {reg["number"]}</p>\n'

    # 주소
    if "address" in colophon and "street" in colophon["address"]:
        html += f'        <p><span class="label">주소</span> {colophon["address"]["street"]}</p>\n'

    # 연락처
    if "contact" in colophon:
        contact = colophon["contact"]
        email = contact["email"]
        fax = contact["fax"]
        html += f'        <p><span class="label">문의</span> {email}</p>\n'
        html += f'        <p><span class="label">팩스</span> {fax}</p>\n'

    # ISBN
    if "isbn" in colophon:
        html += f'        <p><span class="label">ISBN</span> {colophon["isbn"]}</p>\n'

    # 가격
    if "price" in colophon:
        html += f'        <p><span class="label">정가</span> {colophon["price"]}</p>\n'
    # 저작권 고지
    if "copyright_notice" in colophon:
        html += f'        <p>{colophon["copyright_notice"]}</p>\n'

    html += "    </div>\n"
    html += "</body>\n"
    html += "</html>"

    return html


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
    colophon_file = resource_path / "colophon.json"
    fonts_dir = Path("fonts")

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

    # 폰트 폴더 복사
    if fonts_dir.exists():
        output_fonts_dir = output_path / "fonts"
        output_fonts_dir.mkdir(exist_ok=True)

        # 폰트 파일 복사
        for font_file in fonts_dir.glob("*"):
            if font_file.is_file():
                shutil.copy(font_file, output_fonts_dir / font_file.name)
                print(
                    f"폰트 파일을 복사했습니다: {font_file} -> {output_fonts_dir / font_file.name}"
                )

    # 표지 이미지 복사
    if cover_file.exists():
        shutil.copy(cover_file, output_path / "cover.jpg")

    # 제목 페이지 생성
    with open(output_path / "title.html", "w", encoding="utf-8") as f:
        f.write(create_title_page(metadata))

    # 목차 페이지 생성
    with open(output_path / "toc.html", "w", encoding="utf-8") as f:
        f.write(create_toc_html(metadata, chapter_titles))

    # 판권 페이지 생성
    if colophon_file.exists():
        colophon = read_colophon(colophon_file)
        with open(output_path / "colophon.html", "w", encoding="utf-8") as f:
            f.write(create_colophon_html(colophon))
        print(f"판권 페이지를 생성했습니다: {output_path / 'colophon.html'}")

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
