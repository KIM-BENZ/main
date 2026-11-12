# 제원표 PDF → 웹용 제원표 변환 도구

`models.html`의 "한눈에 보기" 표 데이터(`specs-data.js`)를 만드는 스크립트입니다.

1. `python3 parse.py <페이지 번호들> > all.json` — PDF 표의 병합 칸을 읽어 트림·제원·옵션 추출 (PDF 경로는 parse.py 안에서 지정)
2. `python3 norm.py` — 제원 칸을 트림별로 정리 → norm.json
3. `python3 gen.py` — models.html의 차종 목록(models.json)과 맞춰 `specs-data.js` 생성

원본: 2026-10-20 제원표 PDF (MY25 A 35·A 45 제외). 페이지 이미지는 `specs/pNN.jpg`.
