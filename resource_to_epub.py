#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess
from pathlib import Path
from resource_to_html import convert_resource_to_html


def convert_html_to_epub(html_dir, output_file, metadata=None):
    """
    HTML 파일들을 EPUB으로 변환합니다.
    """
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup
        import re

        # EPUB 객체 생성
        book = epub.EpubBook()

        # 메타데이터 설정
        book.set_identifier(
            metadata.get("identifier", f"id-{os.path.basename(output_file)}")
            if metadata
            else f"id-{os.path.basename(output_file)}"
        )
        book.set_title(metadata.get("title", "제목 없음") if metadata else "제목 없음")
        book.set_language(metadata.get("language", "ko") if metadata else "ko")
        book.add_author(
            metadata.get("creator", "저자 미상") if metadata else "저자 미상"
        )

        if metadata and "publisher" in metadata:
            book.add_metadata("DC", "publisher", metadata["publisher"])

        if metadata and "date" in metadata:
            book.add_metadata("DC", "date", metadata["date"])

        # 스타일시트 추가
        html_path = Path(html_dir)
        css_file = html_path / "style.css"

        if css_file.exists():
            with open(css_file, "r", encoding="utf-8") as f:
                css_content = f.read()

            style = epub.EpubItem(
                uid="style",
                file_name="style.css",
                media_type="text/css",
                content=css_content,
            )
            book.add_item(style)

        # 표지 이미지 추가
        cover_file = html_path / "cover.jpg"
        if cover_file.exists():
            with open(cover_file, "rb") as f:
                cover_content = f.read()

            # 커버 이미지 추가
            cover_image = epub.EpubItem(
                uid="cover-image",
                file_name="images/cover.jpg",
                media_type="image/jpeg",
                content=cover_content,
            )
            book.add_item(cover_image)

            # 표지 설정 (메타데이터)
            book.add_metadata(
                None, "meta", "", {"name": "cover", "content": "cover-image"}
            )

            # 커버 페이지 생성 (이미지만 포함)
            cover_page_content = f"""
            <html xmlns="http://www.w3.org/1999/xhtml">
            <head>
                <title>Cover</title>
                <meta charset="utf-8" />
            </head>
            <body>
                <div style="text-align: center; padding: 0; margin: 0;">
                    <img src="images/cover.jpg" alt="Cover" style="height: 100%; max-width: 100%;" />
                </div>
            </body>
            </html>
            """

            # 커버 페이지 추가
            cover_page = epub.EpubHtml(
                uid="cover-page",
                title="Cover",
                file_name="cover.xhtml",
                content=cover_page_content,
                media_type="application/xhtml+xml",
            )
            book.add_item(cover_page)

        # HTML 파일 읽기 및 추가
        chapters = []

        # 커버 페이지가 있으면 추가
        if cover_file.exists():
            chapters.append(cover_page)

        # 제목 페이지 추가
        title_html = html_path / "title.html"
        if title_html.exists():
            with open(title_html, "r", encoding="utf-8") as f:
                title_content = f.read()

            title_page = epub.EpubHtml(
                title="제목", file_name="title.html", content=title_content
            )
            if css_file.exists():
                title_page.add_item(style)
            book.add_item(title_page)
            chapters.append(title_page)

        # 목차 페이지 추가
        toc_html = html_path / "toc.html"
        if toc_html.exists():
            with open(toc_html, "r", encoding="utf-8") as f:
                toc_content = f.read()

            toc_page = epub.EpubHtml(
                title="목차", file_name="toc.html", content=toc_content
            )
            if css_file.exists():
                toc_page.add_item(style)
            book.add_item(toc_page)
            chapters.append(toc_page)

        # 챕터 파일 추가
        chapter_files = sorted(
            [
                f
                for f in os.listdir(html_dir)
                if f.startswith("chapter_") and f.endswith(".html")
            ]
        )

        for chapter_file in chapter_files:
            chapter_path = html_path / chapter_file
            with open(chapter_path, "r", encoding="utf-8") as f:
                chapter_content = f.read()

            # 챕터 제목 추출
            chapter_title = f"Chapter {chapter_file.split('_')[1].split('.')[0]}"

            # HTML에서 제목 추출 시도
            title_match = re.search(r"<title>(.*?)</title>", chapter_content)
            if title_match:
                chapter_title = title_match.group(1)

            # ID 속성 추가
            soup = BeautifulSoup(chapter_content, "html.parser")
            headers = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            for i, header in enumerate(headers):
                if not header.get("id"):
                    header_id = f"header_{chapter_file.split('.')[0]}_{i}"
                    header["id"] = header_id

            chapter_content = str(soup)

            chapter = epub.EpubHtml(
                title=chapter_title, file_name=chapter_file, content=chapter_content
            )
            if css_file.exists():
                chapter.add_item(style)
            book.add_item(chapter)
            chapters.append(chapter)

        # 책 구조 설정
        book.toc = []

        # 목차 항목 추가
        if len(chapters) > 1:  # 제목 페이지와 목차 페이지를 제외한 챕터가 있는 경우
            for chapter in chapters[2:]:  # 제목 페이지와 목차 페이지 이후의 챕터
                # 챕터 내의 헤더 찾기
                soup = BeautifulSoup(chapter.content, "html.parser")
                h1_headers = soup.find_all("h1")

                if h1_headers:
                    # 각 h1 헤더에 대한 목차 항목 추가
                    for h1 in h1_headers:
                        h1_id = h1.get("id", "")
                        h1_text = h1.get_text()

                        # h1 목차 항목 추가
                        h1_link = epub.Link(
                            f"{chapter.file_name}#{h1_id}", h1_text, h1_id
                        )

                        # h2 헤더 찾기
                        h2_items = []
                        current_h1 = h1
                        next_h1 = h1.find_next("h1")

                        # 현재 h1과 다음 h1 사이의 모든 h2 찾기
                        current_element = current_h1.next_sibling
                        while current_element and (
                            next_h1 is None or current_element != next_h1
                        ):
                            if current_element.name == "h2":
                                h2_id = current_element.get("id", "")
                                h2_text = current_element.get_text()
                                h2_link = epub.Link(
                                    f"{chapter.file_name}#{h2_id}", h2_text, h2_id
                                )
                                h2_items.append(h2_link)
                            current_element = current_element.next_sibling

                        if h2_items:
                            book.toc.append((h1_link, h2_items))
                        else:
                            book.toc.append(h1_link)
                else:
                    # h1 헤더가 없는 경우 챕터 자체를 목차 항목으로 추가
                    book.toc.append(
                        epub.Link(chapter.file_name, chapter.title, chapter.id)
                    )

        # 스파인 설정 (책의 페이지 순서)
        if cover_file.exists():
            # 커버 페이지가 있는 경우: 커버 -> 목차 -> 내용
            book.spine = [cover_page] + chapters[1:]
        else:
            # 커버 페이지가 없는 경우: 기존 순서 유지
            book.spine = chapters

        # 네비게이션 파일 추가
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # EPUB 파일 저장
        epub.write_epub(output_file, book, {})

        print(f"EPUB 파일이 성공적으로 생성되었습니다: {output_file}")
        return output_file

    except ImportError:
        print(
            "ebooklib 또는 BeautifulSoup4 모듈을 찾을 수 없습니다. pip install ebooklib beautifulsoup4 명령으로 설치하세요."
        )
        return None
    except Exception as e:
        print(f"EPUB 파일 생성 중 오류가 발생했습니다: {e}")

        # Calibre의 ebook-convert 명령 시도
        try:
            html_path = Path(html_dir)
            title_html = html_path / "title.html"

            if not title_html.exists():
                print(f"오류: {title_html} 파일을 찾을 수 없습니다.")
                return None

            # EPUB 변환 명령 구성
            cmd = [
                "ebook-convert",
                str(title_html),
                output_file,
                "--toc-title",
                "목차",
                "--language",
                metadata.get("language", "ko") if metadata else "ko",
                "--title",
                metadata.get("title", "제목 없음") if metadata else "제목 없음",
                "--authors",
                metadata.get("creator", "저자 미상") if metadata else "저자 미상",
                "--level1-toc",
                "//h:h1",
                "--level2-toc",
                "//h:h2",
                "--level3-toc",
                "//h:h3",
                "--chapter",
                "//h:h1",
                "--chapter-mark",
                "pagebreak",
                "--page-breaks-before",
                "//h:h1",
                "--max-toc-links",
                "50",
                "--toc-filter",
                ".*",
            ]

            # 표지 이미지가 있으면 추가
            cover_file = html_path / "cover.jpg"
            if cover_file.exists():
                cmd.extend(["--cover", str(cover_file)])

            # 출판사 정보가 있으면 추가
            if metadata and "publisher" in metadata:
                cmd.extend(["--publisher", metadata["publisher"]])

            # ISBN 정보가 있으면 추가
            if metadata and "identifier" in metadata:
                cmd.extend(["--isbn", metadata["identifier"]])

            # 출판일 정보가 있으면 추가
            if metadata and "date" in metadata:
                cmd.extend(["--pubdate", metadata["date"]])

            print("EPUB 파일 생성 중...")
            subprocess.run(cmd, check=True)
            print(f"변환 완료: {html_dir} -> {output_file}")
            return output_file
        except (subprocess.SubprocessError, FileNotFoundError):
            print(
                "ebook-convert 명령을 찾을 수 없습니다. Calibre가 설치되어 있는지 확인하세요."
            )
            return None


def convert_resource_to_epub(resource_dir, output_file):
    """
    resource 폴더의 데이터를 EPUB으로 변환합니다.
    """
    # 임시 HTML 디렉토리 생성
    temp_html_dir = "temp_html"

    # resource 폴더의 데이터를 HTML로 변환
    convert_resource_to_html(resource_dir, temp_html_dir)

    # 메타데이터 읽기
    metadata_file = Path(resource_dir) / "metadata.json"
    metadata = None
    if metadata_file.exists():
        import json

        with open(metadata_file, "r", encoding="utf-8") as f:
            metadata = json.load(f)

    # HTML 파일들을 EPUB으로 변환
    result = convert_html_to_epub(temp_html_dir, output_file, metadata)

    # 임시 디렉토리 삭제하지 않음 (디버깅 용도로 유지)
    # import shutil
    # if os.path.exists(temp_html_dir):
    #     shutil.rmtree(temp_html_dir)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="resource 폴더의 데이터를 EPUB으로 변환합니다."
    )
    parser.add_argument(
        "--resource-dir",
        default="resource",
        help="리소스 디렉토리 경로 (기본값: resource)",
    )
    parser.add_argument(
        "--output-file",
        default="output.epub",
        help="출력 EPUB 파일 경로 (기본값: output.epub)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.resource_dir):
        print(f"오류: 리소스 디렉토리 '{args.resource_dir}'을 찾을 수 없습니다.")
        return 1

    convert_resource_to_epub(args.resource_dir, args.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
