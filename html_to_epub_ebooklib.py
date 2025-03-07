#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import re
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from ebooklib import epub


def read_metadata(html_dir):
    """
    메타데이터 정보를 가져옵니다.
    먼저 resource/metadata.json 파일을 확인하고, 없으면 title.html에서 정보를 추출합니다.
    """
    # resource/metadata.json 파일 확인
    resource_metadata_path = Path("resource") / "metadata.json"
    if resource_metadata_path.exists():
        with open(resource_metadata_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # title.html에서 정보 추출
    title_html_path = Path(html_dir) / "title.html"
    if title_html_path.exists():
        metadata = {}
        with open(title_html_path, "r", encoding="utf-8") as f:
            content = f.read()

            # 제목 추출
            title_match = re.search(r'<h1 class="title">(.*?)</h1>', content)
            if title_match:
                metadata["title"] = title_match.group(1)
            else:
                metadata["title"] = "제목 없음"

            # 저자 추출
            author_match = re.search(r'<p class="author">(.*?)</p>', content)
            if author_match:
                metadata["creator"] = author_match.group(1)
            else:
                metadata["creator"] = "저자 미상"

            # 출판사 추출
            publisher_match = re.search(r'<p class="publisher">(.*?)</p>', content)
            if publisher_match:
                metadata["publisher"] = publisher_match.group(1)

            # 언어 추출
            lang_match = re.search(r'lang="(.*?)"', content)
            if lang_match:
                metadata["language"] = lang_match.group(1)
            else:
                metadata["language"] = "ko"

            return metadata

    # 기본 메타데이터 반환
    return {"title": "제목 없음", "creator": "저자 미상", "language": "ko"}


def read_html_file(file_path):
    """
    HTML 파일을 읽어 내용을 반환합니다.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def extract_title_from_html(html_content):
    """
    HTML 내용에서 제목을 추출합니다.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.text
    return "제목 없음"


def extract_body_from_html(html_content):
    """
    HTML 내용에서 body 부분을 추출합니다.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    body = soup.find("body")
    if body:
        return str(body)
    return html_content


def add_ids_to_headers(html_content):
    """
    HTML 내용의 헤더 요소에 ID를 추가합니다.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    # 헤더 요소 찾기
    headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

    # 각 헤더에 ID 추가
    for i, header in enumerate(headers):
        header_text = header.get_text().strip()
        header_id = f"header_{i}_{re.sub(r'[^a-zA-Z0-9가-힣]', '_', header_text)}"
        header["id"] = header_id

    return str(soup)


def convert_html_to_epub(html_dir, output_file):
    """
    HTML 파일들을 EPUB으로 변환합니다.
    """
    html_path = Path(html_dir)

    # 필요한 파일 확인
    title_html = html_path / "title.html"
    toc_html = html_path / "toc.html"
    css_file = html_path / "style.css"
    cover_file = html_path / "cover.jpg"

    if not title_html.exists():
        print(f"오류: {title_html} 파일을 찾을 수 없습니다.")
        return None

    # 메타데이터 읽기
    metadata = read_metadata(html_dir)

    # EPUB 객체 생성
    book = epub.EpubBook()

    # 메타데이터 설정
    book.set_title(metadata.get("title", "제목 없음"))
    book.set_language(metadata.get("language", "ko"))
    book.add_author(metadata.get("creator", "저자 미상"))

    if "publisher" in metadata:
        book.add_metadata("DC", "publisher", metadata["publisher"])

    if "identifier" in metadata:
        book.set_identifier(metadata["identifier"])

    if "date" in metadata:
        book.add_metadata("DC", "date", metadata["date"])

    # 표지 이미지 추가
    if cover_file.exists():
        with open(cover_file, "rb") as f:
            book.set_cover("cover.jpg", f.read())

    # CSS 스타일 추가
    if css_file.exists():
        css_content = read_html_file(css_file)
        nav_css = epub.EpubItem(
            uid="style",
            file_name="style/style.css",
            media_type="text/css",
            content=css_content,
        )
        book.add_item(nav_css)

    # 제목 페이지 추가
    title_content = read_html_file(title_html)
    title_page = epub.EpubHtml(
        title="제목 페이지",
        file_name="title.xhtml",
        lang=metadata.get("language", "ko"),
        content=extract_body_from_html(title_content),
    )
    title_page.add_item(nav_css)
    book.add_item(title_page)

    # 목차 페이지 추가
    if toc_html.exists():
        toc_content = read_html_file(toc_html)
        toc_page = epub.EpubHtml(
            title="목차",
            file_name="toc.xhtml",
            lang=metadata.get("language", "ko"),
            content=extract_body_from_html(toc_content),
        )
        toc_page.add_item(nav_css)
        book.add_item(toc_page)

    # 챕터 파일 추가
    chapters = []
    chapter_items = []
    chapter_files = sorted(
        [f for f in html_path.glob("chapter_*.html")],
        key=lambda x: int(re.search(r"chapter_(\d+)\.html", x.name).group(1)),
    )

    for chapter_file in chapter_files:
        chapter_content = read_html_file(chapter_file)
        chapter_title = extract_title_from_html(chapter_content)

        # 헤더에 ID 추가
        processed_content = add_ids_to_headers(extract_body_from_html(chapter_content))

        chapter = epub.EpubHtml(
            title=chapter_title,
            file_name=f"{chapter_file.name.replace('.html', '.xhtml')}",
            lang=metadata.get("language", "ko"),
            content=processed_content,
        )
        chapter.add_item(nav_css)
        book.add_item(chapter)
        chapter_items.append(chapter)

        # 챕터 내 헤더 찾기
        soup = BeautifulSoup(processed_content, "html.parser")
        headers = soup.find_all(["h1", "h2", "h3"])

        # 챕터와 헤더를 목차에 추가
        if headers:
            chapter_with_sections = [chapter]
            for header in headers:
                if header.get("id"):
                    section = epub.Link(
                        f"{chapter_file.name.replace('.html', '.xhtml')}#{header['id']}",
                        header.get_text(),
                        header["id"],
                    )
                    chapter_with_sections.append(section)
            chapters.append(tuple(chapter_with_sections))
        else:
            chapters.append(chapter)

    # 책 구조 설정
    book.toc = chapters
    book.spine = [title_page, toc_page] + chapter_items

    # EPUB 네비게이션 파일 추가
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # EPUB 파일 생성
    try:
        print("EPUB 파일 생성 중...")
        epub.write_epub(output_file, book, {})
        print(f"변환 완료: {html_dir} -> {output_file}")
        return output_file
    except Exception as e:
        print(f"EPUB 변환 중 오류 발생: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description="HTML 파일들을 EPUB으로 변환합니다.")
    parser.add_argument(
        "--html-dir",
        default="output_html",
        help="HTML 디렉토리 경로 (기본값: output_html)",
    )
    parser.add_argument(
        "--output-file",
        default="output.epub",
        help="출력 EPUB 파일 경로 (기본값: output.epub)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.html_dir):
        print(f"오류: HTML 디렉토리 '{args.html_dir}'을 찾을 수 없습니다.")
        return 1

    convert_html_to_epub(args.html_dir, args.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
