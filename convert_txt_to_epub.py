#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import os
import shutil
import subprocess
from datetime import datetime
from create_cover import create_cover
from txt_to_html_for_epub import convert_txt_to_html_for_epub


def convert_txt_to_epub(input_file, output_file, author="변환 스크립트", title=None):
    """
    텍스트 파일을 EPUB 파일로 변환합니다.

    매개변수:
    - input_file: 입력 텍스트 파일 경로
    - output_file: 출력 EPUB 파일 경로
    - author: 책 저자
    - title: 책 제목 (None인 경우 텍스트 파일의 첫 번째 줄을 사용)
    """
    # 제목이 지정되지 않은 경우 텍스트 파일의 첫 번째 줄을 사용
    if title is None:
        with open(input_file, "r", encoding="utf-8") as f:
            title = f.readline().strip()

    # 임시 디렉토리 생성
    temp_dir = "temp_epub_html"

    # 표지 이미지 생성
    print("표지 이미지 생성 중...")
    cover_file = create_cover(title)

    # HTML 파일 생성
    print("HTML 파일 생성 중...")
    convert_txt_to_html_for_epub(input_file, temp_dir, author)

    # EPUB 파일 생성
    print("EPUB 파일 생성 중...")
    cmd = [
        "ebook-convert",
        os.path.join(temp_dir, "title.html"),
        output_file,
        "--cover",
        cover_file,
        "--toc-title",
        "목차",
        "--authors",
        author,
        "--language",
        "ko",
        "--title",
        title,
        "--level1-toc",
        "//h:h1",
        "--level2-toc",
        "//h:h2",
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"변환 완료: {input_file} -> {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"EPUB 변환 중 오류 발생: {e}")
        return None
    except FileNotFoundError:
        print(
            "ebook-convert 명령을 찾을 수 없습니다. Calibre가 설치되어 있는지 확인하세요."
        )
        return None

    # 임시 디렉토리 삭제
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

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
    parser.add_argument("--title", help="책 제목 (기본값: 텍스트 파일의 첫 번째 줄)")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"오류: 입력 파일 '{args.input_file}'을 찾을 수 없습니다.")
        return 1

    convert_txt_to_epub(
        args.input_file, args.output_file, author=args.author, title=args.title
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
