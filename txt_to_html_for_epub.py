#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import os
import shutil
from datetime import datetime


def split_content_into_chapters(lines):
    """
    텍스트 내용을 챕터로 분할합니다.
    """
    chapters = []
    current_chapter = []
    current_title = None

    # 첫 번째 줄은 책 제목으로 처리
    book_title = lines[0].strip() if lines else "변환된 책"
    lines = lines[1:]

    for line in lines:
        line = line.strip()

        # 빈 줄은 건너뜁니다
        if not line:
            if current_chapter:
                current_chapter.append("")  # 빈 줄 유지
            continue

        # 헤딩 처리 (# 스타일)
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if (
            heading_match and len(heading_match.group(1)) <= 2
        ):  # # 또는 ## 인 경우 새 챕터로 처리
            # 이전 챕터 저장
            if current_chapter:
                chapters.append((current_title, current_chapter))

            # 새 챕터 시작
            current_title = heading_match.group(2).strip()
            current_chapter = []
        else:
            current_chapter.append(line)

    # 마지막 챕터 저장
    if current_chapter:
        chapters.append((current_title, current_chapter))

    return book_title, chapters


def create_chapter_html(title, content, chapter_num):
    """
    챕터 내용을 HTML로 변환합니다.
    """
    html = "<!DOCTYPE html>\n"
    html += '<html lang="ko">\n'
    html += "<head>\n"
    html += f'  <title>{title if title else f"Chapter {chapter_num}"}</title>\n'
    html += '  <meta charset="utf-8" />\n'
    html += '  <link rel="stylesheet" type="text/css" href="style.css" />\n'
    html += "</head>\n"
    html += "<body>\n"

    if title:
        html += f"  <h1>{title}</h1>\n"

    for line in content:
        line = line.strip()

        # 빈 줄은 <br /> 태그로 처리
        if not line:
            html += "  <br />\n"
            continue

        # 헤딩 처리 (# 스타일)
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            heading_level = len(heading_match.group(1))  # #의 개수
            heading_text = heading_match.group(2).strip()
            html += f"  <h{heading_level}>{heading_text}</h{heading_level}>\n"
        else:
            # 일반 텍스트는 <p> 태그로 처리
            html += f"  <p>{line}</p>\n"

    html += "</body>\n"
    html += "</html>"

    return html


def create_toc_html(book_title, chapters):
    """
    목차 HTML 파일을 생성합니다.
    """
    html = "<!DOCTYPE html>\n"
    html += '<html lang="ko">\n'
    html += "<head>\n"
    html += f"  <title>목차 - {book_title}</title>\n"
    html += '  <meta charset="utf-8" />\n'
    html += '  <link rel="stylesheet" type="text/css" href="style.css" />\n'
    html += "</head>\n"
    html += "<body>\n"
    html += "  <h1>목차</h1>\n"
    html += '  <nav class="toc">\n'
    html += "    <ol>\n"

    for i, (title, _) in enumerate(chapters):
        chapter_title = title if title else f"Chapter {i+1}"
        html += f'      <li><a href="chapter_{i+1}.html">{chapter_title}</a></li>\n'

    html += "    </ol>\n"
    html += "  </nav>\n"
    html += "</body>\n"
    html += "</html>"

    return html


def create_title_page(book_title, author="변환 스크립트"):
    """
    제목 페이지 HTML을 생성합니다.
    """
    html = "<!DOCTYPE html>\n"
    html += '<html lang="ko">\n'
    html += "<head>\n"
    html += f"  <title>{book_title}</title>\n"
    html += '  <meta charset="utf-8" />\n'
    html += '  <link rel="stylesheet" type="text/css" href="style.css" />\n'
    html += "</head>\n"
    html += '<body class="title-page">\n'
    html += f"  <h1>{book_title}</h1>\n"
    html += f'  <p class="author">저자: {author}</p>\n'
    html += f'  <p class="date">생성일: {datetime.now().strftime("%Y-%m-%d")}</p>\n'
    html += "</body>\n"
    html += "</html>"

    return html


def create_css():
    """
    스타일시트를 생성합니다.
    """
    css = """
body {
    font-family: sans-serif;
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
"""
    return css


def convert_txt_to_html_for_epub(input_file, output_dir, author="변환 스크립트"):
    """
    텍스트 파일을 EPUB 변환을 위한 HTML 파일들로 변환합니다.

    변환 규칙:
    - # 으로 시작하는 줄은 <h1> 태그로 변환
    - ## 으로 시작하는 줄은 <h2> 태그로 변환
    - ### 으로 시작하는 줄은 <h3> 태그로 변환 (이하 동일)
    - 모든 줄은 <p> 태그로 변환
    - 빈 줄은 <br /> 태그로 변환
    """
    # 텍스트 파일 읽기
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 내용을 챕터로 분할
    book_title, chapters = split_content_into_chapters(lines)

    # 출력 디렉토리 생성
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # CSS 파일 생성
    with open(os.path.join(output_dir, "style.css"), "w", encoding="utf-8") as f:
        f.write(create_css())

    # 제목 페이지 생성
    with open(os.path.join(output_dir, "title.html"), "w", encoding="utf-8") as f:
        f.write(create_title_page(book_title, author))

    # 목차 페이지 생성
    with open(os.path.join(output_dir, "toc.html"), "w", encoding="utf-8") as f:
        f.write(create_toc_html(book_title, chapters))

    # 각 챕터 HTML 파일 생성
    for i, (title, content) in enumerate(chapters):
        chapter_filename = f"chapter_{i+1}.html"
        chapter_content = create_chapter_html(title, content, i + 1)

        with open(
            os.path.join(output_dir, chapter_filename), "w", encoding="utf-8"
        ) as f:
            f.write(chapter_content)

    # 표지 이미지 복사 (있는 경우)
    if os.path.exists("cover.jpg"):
        shutil.copy("cover.jpg", os.path.join(output_dir, "cover.jpg"))

    print(f"변환 완료: {input_file} -> {output_dir}/")
    print(f"총 {len(chapters)}개의 챕터가 생성되었습니다.")
    print(f"이제 다음 명령으로 EPUB 파일을 생성할 수 있습니다:")
    print(
        f"ebook-convert {output_dir}/title.html output.epub --cover {output_dir}/cover.jpg --toc-title 목차"
    )

    return output_dir


def main():
    parser = argparse.ArgumentParser(
        description="텍스트 파일을 EPUB 변환을 위한 HTML 파일들로 변환합니다."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input.txt",
        help="입력 텍스트 파일 경로 (기본값: input.txt)",
    )
    parser.add_argument(
        "output_dir",
        nargs="?",
        default="epub_html",
        help="출력 디렉토리 경로 (기본값: epub_html)",
    )
    parser.add_argument(
        "--author", default="변환 스크립트", help="책 저자 (기본값: 변환 스크립트)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"오류: 입력 파일 '{args.input_file}'을 찾을 수 없습니다.")
        return 1

    convert_txt_to_html_for_epub(args.input_file, args.output_dir, author=args.author)
    return 0


if __name__ == "__main__":
    sys.exit(main())
