from src.pipeline.url_extractor import extract_urls


def test_extract_http_url():
    urls = extract_urls("확인: http://bit.ly/3xFake")
    assert len(urls) == 1
    assert urls[0]["original_url"] == "http://bit.ly/3xFake"
    assert urls[0]["is_shortened"] is True


def test_extract_https_url():
    urls = extract_urls("바로가기: https://www.naver.com/sale")
    assert len(urls) == 1
    assert urls[0]["original_url"] == "https://www.naver.com/sale"
    assert urls[0]["is_shortened"] is False


def test_extract_multiple_urls():
    msg = "링크1: http://bit.ly/abc 링크2: https://google.com"
    urls = extract_urls(msg)
    assert len(urls) == 2


def test_extract_no_urls():
    urls = extract_urls("엄마 나 폰 바꿨어 이 번호로 연락줘")
    assert len(urls) == 0


def test_max_url_limit():
    urls_text = " ".join([f"http://example{i}.com" for i in range(20)])
    urls = extract_urls(urls_text)
    assert len(urls) <= 10


def test_deduplicate_urls():
    msg = "http://bit.ly/abc http://bit.ly/abc"
    urls = extract_urls(msg)
    assert len(urls) == 1


def test_known_shortener_detection():
    shorteners = ["bit.ly", "tinyurl.com", "t.co", "han.gl", "me2.do", "vo.la"]
    for s in shorteners:
        urls = extract_urls(f"http://{s}/test")
        assert urls[0]["is_shortened"] is True, f"{s} should be detected as shortener"
