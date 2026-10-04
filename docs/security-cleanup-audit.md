# Current-tree security cleanup audit

Audit date: 2026-10-05. Values from personal documents are intentionally omitted.

## Scope and outcome

Removed all 49 previously tracked runtime uploads: 29 confirmed personal-document files and 20 generated integration-test artifacts (including intentionally corrupt inputs). Also removed 26 untracked, byte-identical personal-document copies from the local upload directory.

The five existing synthetic PNGs in `demo_samples/images/` replace the public sample catalog. Each carries the demo disclaimer. Runtime uploads are ignored by Git and excluded from Docker build contexts; they cannot be listed or analyzed via the public sample endpoints.

The core analysis pipeline and deployment configuration are unchanged. Regression tests cover upload isolation, exact filename allowlisting, missing samples, and traversal attempts.

## Historical exposure - not remediated by this commit

All 29 personal-document paths below were introduced by commit `854b14880299cf0458c18c77db44c5a9fd7659b2` (2026-09-18). That is also the last content-changing commit before this cleanup for each path. They remain present in the pre-cleanup tip `f5fb17e18e5d5404851e0bd01966a73cf87b2585`.

Fetched remote refs confirmed that all 29 paths were present in `origin/main`, `origin/feature/proofly-ai-backend`, and `origin/codex-proofly-demo-assets` (`fafe7c0dc924e5c2ad15121808017d49a67e4c01`). The repository is public. Exposure is confirmed, not merely inferred. A normal cleanup commit leaves the documents reachable through history, and the other two branch tips still contain them until separately remediated.

All 17 fetched reachable commit trees were inspected. No additional historical path names with identical sensitive Git blobs were found. GitHub caches, pull-request refs, forks, and third-party clones are outside this local audit.

### Confirmed personal-document paths

- `backend/uploads/03fc7936917e_test_student.jpg`
- `backend/uploads/09cf0c5e3e90_test_student.jpg`
- `backend/uploads/1.jpg`
- `backend/uploads/10 result.jpg`
- `backend/uploads/14e4828a632e_10 result.jpg`
- `backend/uploads/17b209c2a6ef_screenshot.png`
- `backend/uploads/2.jpg`
- `backend/uploads/31ddec1fa334_1.jpg`
- `backend/uploads/34e53fc501d8_screenshot.png`
- `backend/uploads/362f2c1f6598_Screenshot 2026-08-13 135707.png`
- `backend/uploads/3ca57d07fd30_document.pdf`
- `backend/uploads/548cd1dd1282_test_student.jpg`
- `backend/uploads/57b041ab58ea_document.pdf`
- `backend/uploads/6266ca5c6e33_test.webp`
- `backend/uploads/7237f6753e0a_screenshot.png`
- `backend/uploads/75e7ae0df6b3_raj bank.jpg`
- `backend/uploads/IMG-20241007-WA0102.jpg`
- `backend/uploads/RAJ 12.pdf`
- `backend/uploads/Screenshot 2026-08-13 135707.png`
- `backend/uploads/aa8c65e70fc7_document.pdf`
- `backend/uploads/adhar raj.jpg`
- `backend/uploads/b3b306a61245_test_student.jpg`
- `backend/uploads/bc0442608701_10 result.jpg`
- `backend/uploads/c0c759bc0dad_screenshot.png`
- `backend/uploads/d575c5045759_screenshot.png`
- `backend/uploads/f0c57f82e6c8_document.pdf`
- `backend/uploads/id.jpg`
- `backend/uploads/raj bank.jpg`
- `backend/uploads/test.jpg`

### Additional local duplicate paths removed

- `backend/uploads/029f0c255931_test_student.jpg`
- `backend/uploads/14a45a4f8d4b_document.pdf`
- `backend/uploads/19a24f94ccbd_document.pdf`
- `backend/uploads/1d06d16c4d7e_raj bank.jpg`
- `backend/uploads/1d8edd699e1d_document.pdf`
- `backend/uploads/2330a705d845_screenshot.png`
- `backend/uploads/270752fb4201_screenshot.png`
- `backend/uploads/28edd97e015a_screenshot.png`
- `backend/uploads/392dec08275d_screenshot.png`
- `backend/uploads/3a556e9a758b_test_student.jpg`
- `backend/uploads/3e6547f4a49e_screenshot.png`
- `backend/uploads/41612dbd0956_document.pdf`
- `backend/uploads/5ae81126f917_document.pdf`
- `backend/uploads/69327b90592b_document.pdf`
- `backend/uploads/7215ac6997f9_test_student.jpg`
- `backend/uploads/7dc454ff15fd_test_student.jpg`
- `backend/uploads/8da7d0b00c04_test_student.jpg`
- `backend/uploads/94a846c72b91_screenshot.png`
- `backend/uploads/acd711876873_document.pdf`
- `backend/uploads/b2c6da022854_screenshot.png`
- `backend/uploads/c32096a8a471_test_student.jpg`
- `backend/uploads/dd0473d66e31_test_student.jpg`
- `backend/uploads/e2d67660a0a3_document.pdf`
- `backend/uploads/f302c0bc189c_screenshot.png`
- `backend/uploads/f5f6773f53a4_test_student.jpg`
- `backend/uploads/f81c46530e14_raj bank.jpg`

## Retained material

Retained all five fictional demo images and their text/metadata, QA scripts, generated scratch-test fixtures whose source is `backend/test_forgery_model.py`, application code, tests, model/evaluation artifacts, and deployment files. No unrelated repository-presentation cleanup is included.

## Validation before commit

- Frontend production build: passed.
- Investor safety and public sample privacy tests: 12 passed.
- Intelligence tests: 18 passed.
- Core Proofly tests: 10 passed.
- Synthetic demo asset QA: passed, zero failures.
- HTTP integration tests, including five public demos and synthetic JPEG/PNG/PDF uploads: 25 passed.
- Credential-pattern scan: no matches in current tracked files or 181 unique historical blobs across 17 commits. No tracked environment files found. This heuristic scan is not a proof that every possible secret is absent.
- No known sensitive document hashes remain in current tracked files. Untracked local caches are excluded from Git and Docker; this is not a full workstation or deployed-storage erasure audit.
- Windows Application Control blocked the optional Torch DLL. Tests passed using the existing fallback; deep-learning execution on this workstation was not verified.
- Sandbox-only temporary-folder/build-tool restrictions required test execution outside the sandbox; the production code was not changed to bypass them.

## Follow-up requiring separate approval

A coordinated sensitive-data history rewrite is recommended. No history rewrite, force push, repository deletion, or credential rotation was performed. Deleting current files alone does not erase previous disclosure. Review all branches and tags, GitHub cached views and pull-request refs, deployment images, forks, and existing clones before treating historical exposure as resolved.
