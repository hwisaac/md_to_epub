# EPUB 변환 도구

## 프로젝트 설명
이 프로젝트는 마크다운(.md) 파일을 EPUB 형식으로 변환하는 도구입니다. 리소스 디렉토리에 있는 콘텐츠, 메타데이터, 스타일시트를 사용하여 EPUB 파일을 생성합니다.

## 사용 방법

### 리소스 디렉토리 구조
```
resource/
  ├── content.md     # 책 내용 (마크다운 형식)
  ├── metadata.json  # 책 메타데이터
  ├── colophon.json  # 판권 정보 (선택 사항)
  ├── cover.jpg      # 표지 이미지 (선택 사항)
  └── style.css      # 스타일시트 (선택 사항)
```

### 폰트 적용
웹 폰트를 적용하려면 `fonts` 폴더에 폰트 파일을 넣으세요. 지원되는 폰트 형식:
- WOFF2 (.woff2)
- WOFF (.woff)
- TrueType (.ttf)
- OpenType (.otf)

예시:
```
fonts/
  └── PretendardVariable.woff2  # 가변 웹폰트
```

### 마크다운에서 HTML로 변환
```bash
python resource_to_html.py --resource-dir resource --output-dir output_html
```

### 마크다운에서 EPUB으로 변환
```bash
python resource_to_epub.py --resource-dir resource --output-file output.epub
```

### 판권 페이지 추가
판권 페이지를 추가하려면 `resource` 폴더에 `colophon.json` 파일을 생성하세요. 판권 페이지는 심플한 구조로 표시됩니다.

예시:
```json
{
  "title": "책 제목",
  "first_published": "2024-12-30",
  "author": "저자 이름",
  "translator": "번역자 이름",
  "publisher": {
    "name": "출판사 이름",
    "editor": "편집자 이름"
  },
  "publication_registration": {
    "date": "2009-09-11",
    "number": "제313-2009-200호"
  },
  "address": {
    "street": "출판사 주소"
  },
  "contact": {
    "email": "연락처 이메일",
    "fax": "팩스 번호"
  },
  "isbn": "ISBN 번호",
  "copyright_notice": "저작권 고지",
  "price": "가격"
}
```

판권 페이지는 EPUB의 마지막에 추가되며, 다음과 같은 형식으로 표시됩니다:
```
책 제목
초판 발행 2024-12-30
저자 이름
번역자 이름
발행인 편집자 이름
발행처 출판사 이름
출판등록 2009-09-11 제313-2009-200호
주소 출판사 주소
문의 연락처 이메일 팩스 팩스 번호
ISBN(이펍) ISBN 번호
저작권 고지
정가 가격
```

판권 페이지는 목차 이전에 배치됩니다. EPUB의 페이지 순서는 다음과 같습니다:
1. 표지 이미지
2. 제목 페이지
3. 판권 페이지
4. 목차
5. 본문 내용

## 기능
- 마크다운 형식의 콘텐츠를 HTML로 변환
- HTML을 EPUB으로 변환
- 목차 자동 생성
- 챕터 분할 지원
- 커스텀 스타일시트 지원
- 웹폰트 지원 (WOFF2, WOFF, TTF, OTF)
- 표지 이미지 지원
- 판권 페이지 지원
- 메타데이터 설정 (제목, 저자, 언어 등)

## 요구 사항
- Python 3.6 이상
- ebooklib
- beautifulsoup4

## 설치
```bash
pip install -r requirements.txt
```

## 폴더 구조
```
.
├── resource/                # 리소스 디렉토리
│   ├── content.md           # 책 내용 (마크다운 형식)
│   ├── metadata.json        # 책 메타데이터
│   ├── colophon.json        # 판권 정보
│   ├── cover.jpg            # 표지 이미지
│   └── style.css            # 스타일시트
├── fonts/                   # 폰트 디렉토리
│   └── PretendardVariable.woff2  # 웹폰트 파일
├── resource_to_html.py      # 마크다운을 HTML로 변환하는 스크립트
├── resource_to_epub.py      # 리소스 디렉토리에서 EPUB 생성하는 스크립트
├── html_to_epub_ebooklib.py # HTML을 EPUB으로 변환하는 스크립트 (ebooklib 사용)
└── requirements.txt         # 필요한 패키지 목록
```


resource/metadata.json 예시

```json
{
  "title": "제목",
  "creator": "작가",
  "publisher": "출판사명",
  "identifier": "979-11-1234-432-6",
  "date": "2025-03-13",
  "language": "ko"
}
```

## 문제 해결

### 목차(TOC) 링크 문제
EPUB 파일에서 목차 링크가 작동하지 않는 문제가 있었습니다. 이 문제는 다음과 같은 원인으로 발생했습니다:

1. **ID 속성 누락**: HTML 파일의 헤더 요소에 ID 속성이 없어 링크 대상을 찾을 수 없었습니다.
2. **TOC 구조 문제**: EPUB TOC 구조가 챕터 파일만 가리키고 챕터 내의 헤더를 참조하지 않았습니다.
3. **파일 확장자 불일치**: HTML 파일과 EPUB 내부 파일의 확장자가 달라 링크가 깨졌습니다.

이 문제는 `resource_to_epub.py` 스크립트에서 다음과 같이 해결했습니다:

1. BeautifulSoup을 사용하여 헤더 요소에 자동으로 ID 속성을 추가합니다.
2. 챕터 내의 헤더를 찾아 TOC에 추가합니다.
3. 파일 확장자를 일관되게 유지합니다.

### 마크다운 헤딩 변환 문제
마크다운의 헤딩(`# 제목`)이 HTML의 `<h1>`, `<h2>` 등으로 올바르게 변환되지 않는 문제가 있었습니다. 이 문제는 `resource_to_html.py` 파일의 `process_markdown_content` 함수를 수정하여 해결했습니다.

### 수평선 변환 문제
마크다운의 수평선(`---`, `___`, `***`)이 HTML의 `<hr />` 태그로 올바르게 변환되지 않는 문제가 있었습니다. 이 문제는 마크다운 처리 함수에 수평선 처리 코드를 추가하여 해결했습니다.

## 업데이트 내역
- 2023-03-07: 판권 페이지 위치를 목차 이전으로 변경
- 2023-03-07: 판권 페이지 디자인을 심플한 구조로 변경
- 2023-03-07: 판권 페이지 지원 추가
- 2023-03-07: 웹폰트(Pretendard) 지원 추가
- 2023-03-07: 마크다운 헤딩 태그가 HTML에 올바르게 포함되도록 수정
- 2023-03-07: EPUB spine에서 nav 항목 제거
- 2023-03-07: 페이지 구성 개선 (1페이지: 커버 이미지만, 2페이지: 목차)
- 2023-03-07: txt 파일 관련 코드 제거, resource 디렉토리의 데이터만 사용하도록 변경
- 2023-03-07: 커스텀 스타일시트 지원 추가
- 2023-03-07: ebooklib을 사용한 EPUB 생성 기능 추가
- 2023-03-07: 마크다운 헤딩 및 수평선 변환 문제 해결

