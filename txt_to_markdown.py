#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import argparse
import os


def convert_txt_to_markdown(input_file, output_file):
    """
    일반 텍스트 파일을 마크다운 형식으로 변환합니다.

    변환 규칙:
    - 첫 번째 줄은 # 제목 형식으로 변환
    - 짧은 줄(20자 미만)은 ## 제목 형식으로 변환
    - 더 짧은 줄(10자 미만)은 ### 제목 형식으로 변환
    - 빈 줄은 그대로 유지
    - 나머지 줄은 그대로 유지
    """
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    markdown_lines = []

    # 첫 번째 줄은 책 제목으로 처리
    if lines:
        title = lines[0].strip()
        markdown_lines.append(f"# {title}")
        markdown_lines.append("")  # 빈 줄 추가
        lines = lines[1:]

    for line in lines:
        line = line.strip()

        # 빈 줄은 그대로 유지
        if not line:
            markdown_lines.append("")
            continue

        # 짧은 줄은 제목으로 처리
        if len(line) < 10:
            markdown_lines.append(f"### {line}")
            markdown_lines.append("")  # 빈 줄 추가
        elif len(line) < 20:
            markdown_lines.append(f"## {line}")
            markdown_lines.append("")  # 빈 줄 추가
        else:
            markdown_lines.append(line)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    print(f"변환 완료: {input_file} -> {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="텍스트 파일을 마크다운 형식으로 변환합니다."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="input.txt",
        help="입력 텍스트 파일 경로 (기본값: input.txt)",
    )
    parser.add_argument(
        "output_file",
        nargs="?",
        default="output_markdown.txt",
        help="출력 마크다운 파일 경로 (기본값: output_markdown.txt)",
    )

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"오류: 입력 파일 '{args.input_file}'을 찾을 수 없습니다.")
        return 1

    convert_txt_to_markdown(args.input_file, args.output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())
