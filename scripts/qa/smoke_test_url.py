"""Basic public HTTPS smoke test; stdlib only, no assumed app routes.

Usage: python scripts/qa/smoke_test_url.py https://PUBLIC_URL [/supplied/path ...]
Reads at most 64 KiB per response. Does not submit forms or authenticate.
"""
import argparse
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def validate_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an HTTPS URL with a hostname and no embedded credentials")
    if parsed.fragment:
        raise ValueError("URL fragments are not supported")
    return parsed


class HTTPSRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Public HTTPS homepage URL")
    parser.add_argument("paths", nargs="*", help="Optional explicit paths starting with / on the same origin")
    parser.add_argument("--timeout", type=float, default=15, help="Per-request socket timeout in seconds (default: 15)")
    args = parser.parse_args(argv)
    try:
        base = validate_url(args.url)
        if not 0 < args.timeout <= 120:
            raise ValueError("Timeout must be between 0 and 120 seconds")
        urls = [args.url]
        for path in args.paths:
            part = urllib.parse.urlsplit(path)
            if not path.startswith("/") or path.startswith("//") or part.scheme or part.netloc or part.fragment or "\\" in path:
                raise ValueError("Extra paths must start with a single / and contain no host or fragment")
            urls.append(urllib.parse.urlunsplit(("https", base.netloc, part.path, part.query, "")))
    except ValueError as error:
        print(f"FAIL: {error}")
        return 1
    opener = urllib.request.build_opener(HTTPSRedirects())
    failures = 0
    for url in dict.fromkeys(urls):
        start = time.perf_counter()
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Proofly-Demo-QA/1.0"})
            with opener.open(request, timeout=args.timeout) as response:
                body = response.read(65536)
                final_url = response.geturl()
                validate_url(final_url)
                ok = 200 <= response.status < 300 and bool(body.strip())
                elapsed = time.perf_counter() - start
                print(f"{'PASS' if ok else 'FAIL'} {url} | HTTP {response.status} | {len(body)} bytes read | {elapsed:.3f}s | final: {final_url}")
                failures += not ok
        except (urllib.error.URLError, OSError, ValueError) as error:
            failures += 1
            print(f"FAIL {url} | {time.perf_counter() - start:.3f}s | {error}")
    print(f"\n{'FAIL' if failures else 'PASS'}: URL smoke test ({failures} failures)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
