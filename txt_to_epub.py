#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import os
import uuid
from datetime import datetime
from ebooklib import epub


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

        # 헤딩 감지 규칙
        is_heading = False

        # 1. 짧은 줄은 소제목으로 처리 (20자 미만)
        if len(line) < 20:
            is_heading = True

        # 2. 숫자로 시작하는 줄은 챕터 제목으로 처리
        if re.match(r"^\d+\.", line):
            is_heading = True

        # 3. 특수 문자로 시작하는 줄은 소제목으로 처리
        if line.startswith("*") or line.startswith("#"):
            is_heading = True
            line = line[1:].strip()  # 특수 문자 제거

        # 새로운 챕터 시작
        if is_heading and len(current_chapter) > 0:
            # 이전 챕터 저장
            chapters.append((current_title, current_chapter))
            current_chapter = []
            current_title = line
        elif is_heading and current_title is None:
            current_title = line
        else:
            current_chapter.append(line)

    # 마지막 챕터 저장
    if current_chapter:
        chapters.append((current_title, current_chapter))

    return book_title, chapters


def create_chapter_html(title, content):
    """
    챕터 내용을 HTML로 변환합니다.
    """
    html = '<?xml version="1.0" encoding="utf-8"?>\n'
    html += "<!DOCTYPE html>\n"
    html += '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">\n'
    html += "<head>\n"
    html += f'  <title>{title if title else "Chapter"}</title>\n'
    html += '  <meta charset="utf-8" />\n'
    html += "</head>\n"
    html += "<body>\n"

    if title:
        html += f"  <h1>{title}</h1>\n"

    current_paragraph = []

    for line in content:
        if not line:
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                html += f"  <p>{paragraph_text}</p>\n"
                current_paragraph = []
            continue

        # 짧은 줄은 소제목으로 처리 (20자 미만)
        if len(line) < 20 and not line.startswith(" "):
            # 이전 문단이 있으면 먼저 처리
            if current_paragraph:
                paragraph_text = " ".join(current_paragraph)
                html += f"  <p>{paragraph_text}</p>\n"
                current_paragraph = []

            html += f"  <h2>{line}</h2>\n"
        else:
            current_paragraph.append(line)

    # 마지막 문단 처리
    if current_paragraph:
        paragraph_text = " ".join(current_paragraph)
        html += f"  <p>{paragraph_text}</p>\n"

    html += "</body>\n"
    html += "</html>"

    return html


def convert_txt_to_epub(input_file, output_file, author="변환 스크립트"):
    """
    텍스트 파일을 EPUB 파일로 변환합니다.
    """
    # 텍스트 파일 읽기
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 내용을 챕터로 분할
    book_title, chapters = split_content_into_chapters(lines)

    # EPUB 파일 생성
    book = epub.EpubBook()

    # 메타데이터 설정
    book.set_identifier(str(uuid.uuid4()))
    book.set_title(book_title)
    book.set_language("ko")
    book.add_author(author)

    # 표지 이미지 추가
    if os.path.exists("cover.jpg"):
        with open("cover.jpg", "rb") as f:
            book.set_cover("cover.jpg", f.read())

    # CSS 스타일 추가
    style = """
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
        color: #555;
    }
    p {
        text-indent: 1em;
        margin-top: 0.5em;
        margin-bottom: 0.5em;
    }
    """

    css = epub.EpubItem(
        uid="style_default",
        file_name="style/default.css",
        media_type="text/css",
        content=style,
    )
    book.add_item(css)

    # 챕터 추가
    chapters_epub = []
    toc = []
    spine = ["nav"]

    # 첫 페이지 추가 (제목 페이지)
    intro = epub.EpubHtml(title=book_title, file_name="intro.xhtml", lang="ko")
    intro.content = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{book_title}</title>
  <meta charset="utf-8" />
  <link rel="stylesheet" type="text/css" href="style/default.css" />
</head>
<body>
  <h1>{book_title}</h1>
  <p style="text-align: center; margin-top: 3em;">변환된 EPUB 도서</p>
  <p style="text-align: center;">저자: {author}</p>
  <p style="text-align: center; margin-top: 5em;">생성일: {datetime.now().strftime('%Y-%m-%d')}</p>
</body>
</html>"""

    book.add_item(intro)
    chapters_epub.append(intro)
    spine.append(intro)

    # 각 챕터 추가
    for i, (title, content) in enumerate(chapters):
        chapter_title = title if title else f"Chapter {i+1}"
        chapter_filename = f"chapter_{i+1}.xhtml"

        # 챕터 HTML 생성
        chapter_content = create_chapter_html(chapter_title, content)

        # EPUB 챕터 생성
        chapter = epub.EpubHtml(
            title=chapter_title, file_name=chapter_filename, lang="ko"
        )
        chapter.content = chapter_content
        chapter.add_item(css)

        # 책에 챕터 추가
        book.add_item(chapter)
        chapters_epub.append(chapter)
        toc.append(epub.Link(chapter_filename, chapter_title, f"chapter_{i+1}"))
        spine.append(chapter)

    # 목차 추가
    book.toc = toc

    # 기본 NCX 및 Nav 파일 추가
    book.add_item(epub.EpubNcx())
    nav = epub.EpubNav()
    nav.add_item(css)
    book.add_item(nav)

    # 책의 스파인 정의
    book.spine = spine

    # EPUB 파일 저장
    epub.write_epub(output_file, book, {})

    print(f"변환 완료: {input_file} -> {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(description="텍스트 파일을 EPUB으로 변환합니다.")
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input.txt",
        help="입력 텍스트 파일 경로 (기본값: input.txt)",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="output.epub",
        help="출력 EPUB 파일 경로 (기본값: output.epub)",
    )
    parser.add_argument(
        "--author", default="변환 스크립트", help="책 저자 (기본값: 변환 스크립트)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"오류: 입력 파일 '{args.input_file}'을 찾을 수 없습니다.")
        return 1

    convert_txt_to_epub(args.input_file, args.output_file, author=args.author)
    return 0


if __name__ == "__main__":
    sys.exit(main())
