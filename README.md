# TXT to EPUB 변환기

이 프로젝트는 텍스트 파일을 HTML 또는 EPUB 파일로 변환하는 도구입니다.

## 기능

- 텍스트 파일을 HTML로 변환
- 텍스트 파일을 EPUB으로 변환
- 텍스트 파일을 마크다운 형식으로 변환
- 자동 목차 생성
- 자동 표지 이미지 생성
- 마크다운 스타일의 헤딩 지원

## 요구사항

- Python 3.6 이상
- Pillow 라이브러리 (표지 이미지 생성용)
- Calibre (EPUB 변환용)

## 설치

```bash
# 필요한 Python 라이브러리 설치
pip install pillow

# Calibre 설치 (macOS)
brew install calibre

# Calibre 설치 (Windows)
# https://calibre-ebook.com/download 에서 다운로드 및 설치
```

## 사용법

### 텍스트 파일을 HTML로 변환

```bash
python txt_to_html.py [입력파일.txt] [출력파일.html]
```

옵션:
- `--no-toc`: 목차를 생성하지 않습니다.
- `--css`: 외부 CSS 파일 경로를 지정합니다.

### 텍스트 파일을 EPUB으로 변환

```bash
python convert_txt_to_epub.py [입력파일.txt] [출력파일.epub]
```

옵션:
- `--author`: 책 저자를 지정합니다. (기본값: "변환 스크립트")
- `--title`: 책 제목을 지정합니다. (기본값: 텍스트 파일의 첫 번째 줄)

### 텍스트 파일을 마크다운 형식으로 변환

```bash
python txt_to_markdown.py [입력파일.txt] [출력파일.md]
```

변환 규칙:
- 첫 번째 줄은 `# 제목` 형식으로 변환 (책 제목)
- 짧은 줄(20자 미만)은 `## 제목` 형식으로 변환 (챕터 제목)
- 더 짧은 줄(10자 미만)은 `### 제목` 형식으로 변환 (소제목)
- 빈 줄은 그대로 유지
- 나머지 줄은 그대로 유지

### 일반 텍스트를 마크다운 형식으로 변환 후 EPUB 생성

일반 텍스트 파일을 마크다운 형식으로 변환한 후 EPUB으로 생성하는 방법:

1. 텍스트 파일을 마크다운 형식으로 변환:
   ```bash
   python txt_to_markdown.py input.txt input_markdown.txt
   ```

2. 변환된 마크다운 파일을 EPUB으로 변환:
   ```bash
   python convert_txt_to_epub.py input_markdown.txt output.epub --author "저자명" --title "책제목"
   ```

3. 한 번에 처리하는 방법:
   ```bash
   python txt_to_markdown.py input.txt input_markdown.txt && python convert_txt_to_epub.py input_markdown.txt output.epub --author "안데르센" --title "안데르센 동화집"
   ```

## 변환 규칙

- `# 제목` 형식의 줄은 `<h1>` 태그로 변환됩니다.
- `## 제목` 형식의 줄은 `<h2>` 태그로 변환됩니다.
- `### 제목` 형식의 줄은 `<h3>` 태그로 변환됩니다. (이하 동일)
- 모든 일반 텍스트 줄은 `<p>` 태그로 변환됩니다.
- 빈 줄은 `<br />` 태그로 변환됩니다.
- EPUB 변환 시 `# 제목`과 `## 제목` 형식의 줄은 새로운 챕터의 시작으로 처리됩니다.

## 파일 설명

- `txt_to_html.py`: 텍스트 파일을 HTML로 변환합니다.
- `txt_to_markdown.py`: 텍스트 파일을 마크다운 형식으로 변환합니다.
- `txt_to_html_for_epub.py`: EPUB 변환을 위한 HTML 파일들을 생성합니다.
- `create_cover.py`: EPUB 표지 이미지를 생성합니다.
- `convert_txt_to_epub.py`: 텍스트 파일을 EPUB으로 변환하는 통합 스크립트입니다.

## 예제

```bash
# 기본 HTML 변환
python txt_to_html.py input.txt output.html

# 목차 없이 HTML 변환
python txt_to_html.py input.txt output.html --no-toc

# 텍스트 파일을 마크다운으로 변환
python txt_to_markdown.py input.txt input_markdown.txt

# EPUB 변환
python convert_txt_to_epub.py input.txt output.epub --author "안데르센" --title "안데르센 동화집"

# 마크다운 형식의 파일을 EPUB으로 변환
python convert_txt_to_epub.py input_markdown.txt output.epub --author "안데르센" --title "안데르센 동화집"

# 텍스트 파일을 마크다운으로 변환 후 EPUB 생성 (한 번에)
python txt_to_markdown.py input.txt input_markdown.txt && python convert_txt_to_epub.py input_markdown.txt output.epub --author "안데르센" --title "안데르센 동화집"
```

## 입력 파일 예시

```
# 책 제목

## 첫 번째 장

이것은 첫 번째 장의 내용입니다.
이 줄은 같은 문단으로 처리됩니다.

이것은 새로운 문단입니다.

### 소제목

소제목 아래의 내용입니다.

# 두 번째 장

이것은 두 번째 장의 내용입니다.
```

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

