#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path


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


def convert_html_to_epub(html_dir, output_file):
    """
    HTML 파일들을 EPUB으로 변환합니다.
    """
    html_path = Path(html_dir)
    title_html = html_path / "title.html"

    if not title_html.exists():
        print(f"오류: {title_html} 파일을 찾을 수 없습니다.")
        return None

    # 메타데이터 읽기
    metadata = read_metadata(html_dir)

    # EPUB 변환 명령 구성
    cmd = [
        "ebook-convert",
        str(title_html),
        output_file,
        "--toc-title",
        "목차",
        "--language",
        metadata.get("language", "ko"),
        "--title",
        metadata.get("title", "제목 없음"),
        "--authors",
        metadata.get("creator", "저자 미상"),
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
    if "publisher" in metadata:
        cmd.extend(["--publisher", metadata["publisher"]])

    # ISBN 정보가 있으면 추가
    if "identifier" in metadata:
        cmd.extend(["--isbn", metadata["identifier"]])

    # 출판일 정보가 있으면 추가
    if "date" in metadata:
        cmd.extend(["--pubdate", metadata["date"]])

    try:
        print("EPUB 파일 생성 중...")
        subprocess.run(cmd, check=True)
        print(f"변환 완료: {html_dir} -> {output_file}")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"EPUB 변환 중 오류 발생: {e}")
        return None
    except FileNotFoundError:
        print(
            "ebook-convert 명령을 찾을 수 없습니다. Calibre가 설치되어 있는지 확인하세요."
        )
        print("Calibre 설치 방법:")
        print("  macOS: brew install calibre")
        print("  Windows: https://calibre-ebook.com/download 에서 다운로드 및 설치")
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
    import re  # re 모듈 임포트 추가

    sys.exit(main())
