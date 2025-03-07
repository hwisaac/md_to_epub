#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PIL import Image, ImageDraw, ImageFont


def create_cover(
    title,
    output_file="cover.jpg",
    width=1600,
    height=2560,
    background_color=(240, 240, 245),
):
    """
    EPUB 표지 이미지를 생성합니다.

    매개변수:
    - title: 책 제목
    - output_file: 출력 이미지 파일 경로
    - width: 이미지 너비
    - height: 이미지 높이
    - background_color: 배경색 (RGB)
    """
    # 이미지 생성
    img = Image.new("RGB", (width, height), color=background_color)
    draw = ImageDraw.Draw(img)

    # 폰트 설정 (시스템에 설치된 폰트 사용)
    try:
        # macOS 기본 폰트
        title_font = ImageFont.truetype("AppleGothic.ttf", 120)
    except IOError:
        try:
            # 윈도우 기본 폰트
            title_font = ImageFont.truetype("malgun.ttf", 120)
        except IOError:
            # 폰트를 찾을 수 없는 경우 기본 폰트 사용
            title_font = ImageFont.load_default()

    # 텍스트 위치 계산
    title_lines = []
    current_line = ""

    # 제목을 여러 줄로 나누기
    words = title.split()
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if title_font.getlength(test_line) < width * 0.8:
            current_line = test_line
        else:
            title_lines.append(current_line)
            current_line = word

    if current_line:
        title_lines.append(current_line)

    # 텍스트 그리기
    text_color = (50, 50, 100)  # 어두운 파란색

    # 제목 위치 계산
    total_text_height = len(title_lines) * 150  # 줄 간격 포함
    y_position = (height - total_text_height) // 2

    # 제목 그리기
    for line in title_lines:
        text_width = title_font.getlength(line)
        x_position = (width - text_width) // 2
        draw.text((x_position, y_position), line, font=title_font, fill=text_color)
        y_position += 150

    # 테두리 그리기
    border_color = (100, 100, 150)
    border_width = 10
    draw.rectangle(
        [
            (border_width // 2, border_width // 2),
            (width - border_width // 2, height - border_width // 2),
        ],
        outline=border_color,
        width=border_width,
    )

    # 이미지 저장
    img.save(output_file, quality=95)
    print(f"표지 이미지 생성 완료: {output_file}")
    return output_file


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        title = sys.argv[1]
    else:
        # 입력 파일에서 첫 번째 줄을 제목으로 사용
        if os.path.exists("input.txt"):
            with open("input.txt", "r", encoding="utf-8") as f:
                title = f.readline().strip()
        else:
            title = "EPUB 책"

    create_cover(title)
