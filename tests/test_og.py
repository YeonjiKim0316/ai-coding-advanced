"""링크 미리보기(OG 태그) 테스트."""

import re
from pathlib import Path

STATIC = Path(__file__).resolve().parent.parent / "static"


def test_index_has_four_og_tags():
    # Given: 첫 화면 파일
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    # When: og 태그 이름을 모은다
    names = set(re.findall(r'<meta property="(og:[a-z]+)"', html))
    # Then: 네 개가 모두 있다
    assert names == {"og:title", "og:description", "og:image", "og:url"}


def test_og_image_file_exists_and_is_served(make_client):
    # Given: og:image 가 가리키는 파일 이름
    html = (STATIC / "index.html").read_text(encoding="utf-8")
    name = re.search(r'og:image" content="[^"]*/([^/"]+)"', html).group(1)
    # When: 서버에서 그 파일을 요청한다
    r = make_client(0.5).get(f"/{name}")
    # Then: 200 이고 PNG 이다
    assert r.status_code == 200 and r.content[:8] == b"\x89PNG\r\n\x1a\n"

# © 2026 김연지. All rights reserved. 수강생 개인 학습용 · 무단 강의·복제·배포·수정 금지 (LICENSE.md)
