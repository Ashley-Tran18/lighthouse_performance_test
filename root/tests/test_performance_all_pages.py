# tests/test_lighthouse_with_allure.py
import os
import json
import subprocess
import pytest
import allure
from allure_commons.types import AttachmentType
from urllib.parse import quote_plus
from pathlib import Path
from glob import glob
from datetime import datetime
import re

# Threshold
PERFORMANCE_THRESHOLD = 0.80   # 90% → fails if <90
ACCESSIBILITY_THRESHOLD = 0.80
BEST_PRACTICES_THRESHOLD = 0.80
SEO_THRESHOLD = 0.80


def run_lighthouse(url: str, report_dir: str = "lighthouse_reports"):
    """Run Lighthouse and return paths to JSON + HTML reports"""
    os.makedirs(report_dir, exist_ok=True)

    # Create a safe filename
    safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_").rstrip("_")
    base_path = Path(report_dir) / safe_name

    json_path = base_path.with_suffix(".json")
    html_path = base_path.with_suffix(".report.html")

    print(f"Running Lighthouse on {url}...")

    # Common flags (excluding --output and --output-path)
    common_cmd = [
        "lighthouse", url,
        "--chrome-flags=--headless --no-sandbox --disable-gpu --disable-dev-shm-usage",
        "--quiet",
        "--emulated-form-factor=mobile",
        "--only-categories=performance,accessibility,best-practices,seo",
        "--skip-autolaunch",
    ]

    # Run 1: JSON output
    json_cmd = common_cmd + [
        "--output=json",
        "--output-path", str(json_path)
    ]
    result_json = subprocess.run(json_cmd, capture_output=True, text=True)
    if result_json.returncode != 0:
        print("Lighthouse JSON STDERR:")
        print(result_json.stderr)
        raise RuntimeError(f"Lighthouse JSON failed for {url}:\n{result_json.stderr}")
    print("Lighthouse JSON STDOUT:", result_json.stdout)  # For debugging

    # Run 2: HTML output
    html_cmd = common_cmd + [
        "--output=html",
        "--output-path", str(html_path)
    ]
    result_html = subprocess.run(html_cmd, capture_output=True, text=True)
    if result_html.returncode != 0:
        print("Lighthouse HTML STDERR:")
        print(result_html.stderr)
        raise RuntimeError(f"Lighthouse HTML failed for {url}:\n{result_html.stderr}")

    # Fallback: If files still missing, look for timestamped defaults in CWD
    if not json_path.exists():
        fallback_candidates = glob("*.report.json")  # Matches any .report.json
        if fallback_candidates:
            latest_fallback = max(fallback_candidates, key=os.path.getctime)
            Path(latest_fallback).rename(json_path)
            print(f"Moved fallback JSON: {latest_fallback} -> {json_path}")
        else:
            raise FileNotFoundError(f"JSON report not generated: {json_path}\nNo fallback .report.json found in CWD")

    if not html_path.exists():
        fallback_candidates = glob("*.report.html")  # Matches any .report.html
        if fallback_candidates:
            latest_fallback = max(fallback_candidates, key=os.path.getctime)
            Path(latest_fallback).rename(html_path)
            print(f"Moved fallback HTML: {latest_fallback} -> {html_path}")
        else:
            raise FileNotFoundError(f"HTML report not generated: {html_path}\nNo fallback .report.html found in CWD")

    print(f"Reports generated: JSON={json_path}, HTML={html_path}")
    return json_path, html_path
   

# @pytest.mark.parametrize("url", [
#     "https://www.paveddigital.com/",
#     "https://www.paveddigital.com/why-us",
#     # Add more pages
# ])
# @allure.epic("Performance")
# @allure.feature("Lighthouse Audit")
# def test_lighthouse_performance(url):
#     with allure.step(f"Audit performance: {url}"):
#         json_path, html_path = run_lighthouse(url)

#         with open(json_path, "r", encoding="utf-8") as f:
#             report = json.load(f)

#         # Extract scores
#         perf_score = report["categories"]["performance"]["score"]
#         accessibility_score = report["categories"]["accessibility"]["score"]
#         best_practices_score = report["categories"]["best-practices"]["score"]
#         seo_score = report["categories"]["seo"]["score"]

#         # Attach full interactive HTML report (clickable in Allure!)
#         with open(html_path, "rb") as f:
#             allure.attach(
#                 f.read(),
#                 name=f"Lighthouse Report - {url.split('//')[1]}",
#                 attachment_type=AttachmentType.HTML,
#                 extension="html"
#             )

#         # Attach JSON (optional)
#         with open(json_path, "r", encoding="utf-8") as f:
#             allure.attach(f.read(), name="report.json", attachment_type=AttachmentType.JSON)

#         # Attach filmstrip screenshots (if available)
#         if "timeline" in report["audits"]:
#             screenshots = report["audits"]["screenshot-thumbnails"]["details"]["items"]
#             for i, item in enumerate(screenshots[:6]):  # First 6 frames
#                 import base64
#                 img_data = base64.b64decode(item["data"].split(",")[1])
#                 allure.attach(
#                     img_data,
#                     name=f"Frame {i+1} - {item['timing']}ms",
#                     attachment_type=AttachmentType.PNG
#                 )

#         # Add summary
#         allure.dynamic.description(f"""
#         **Lighthouse Results**  
#         • Performance: **{perf_score*100:.1f}%**  
#         • Accessibility: **{accessibility_score*100:.1f}%**  
#         • Best Practices: **{best_practices_score*100:.1f}%**  
#         • SEO: **{seo_score*100:.1f}%**  
#         """)

#         # Fail test if performance too low
#         if perf_score < PERFORMANCE_THRESHOLD:
#             allure.dynamic.severity(allure.severity_level.CRITICAL)
#             raise AssertionError(
#                 f"Performance score {perf_score*100:.1f}% < {PERFORMANCE_THRESHOLD*100}% threshold!\n"
#                 f"→ Open the attached HTML report to see LCP, CLS, unused JS, etc."
#             )
#         else:
#             allure.dynamic.severity(allure.severity_level.NORMAL)

# @pytest.mark.parametrize(
#     "url, page_name",
#     [
#         ("https://www.paveddigital.com/", "Homepage"),
#         ("https://www.paveddigital.com/why-us", "Why Us"),
#         ("https://www.paveddigital.com/what-we-do", "What we do"),
#         ("https://www.paveddigital.com/join-us", "Join us"),
#         ("https://www.paveddigital.com/contact-us", "Contact us"),
#         # ...
#     ],
#     ids=lambda x: x[1] if isinstance(x, tuple) else None  # Clean test names
# )
# @allure.title("Lighthouse Audit: {page_name}")
# @allure.epic("Performance")
# @allure.feature("Lighthouse Audit")
# def test_lighthouse_performance(url, page_name):
#     with allure.step(f"Audit performance: {page_name} → {url}"):
#         json_path, html_path = run_lighthouse(url, report_dir="lighthouse_reports")

#         with open(json_path, "r", encoding="utf-8") as f:
#             report = json.load(f)

#         perf_score = report["categories"]["performance"]["score"]
#         accessibility_score = report["categories"]["accessibility"]["score"]
#         best_practices_score = report["categories"]["best-practices"]["score"]
#         seo_score = report["categories"]["seo"]["score"]

#         # Better attachment names using page_name
#         safe_page_name = page_name.replace(" ", "_").lower()
#         with open(html_path, "rb") as f:
#             allure.attach(
#                 f.read(),
#                 name=f"Lighthouse Report - {page_name}",
#                 attachment_type=AttachmentType.HTML,
#                 extension="html"
#             )

#         allure.dynamic.description(f"""
#         **Lighthouse Results - {page_name}**  
#         URL: {url}  
#         • Performance: **{perf_score*100:.1f}%**  
#         • Accessibility: **{accessibility_score*100:.1f}%**  
#         • Best Practices: **{best_practices_score*100:.1f}%**  
#         • SEO: **{seo_score*100:.1f}%**  
#         """)

#         if perf_score < PERFORMANCE_THRESHOLD:
#             allure.dynamic.severity(allure.severity_level.CRITICAL)
#             raise AssertionError(
#                 f"Performance score {perf_score*100:.1f}% is below {PERFORMANCE_THRESHOLD*100}% threshold on {page_name}!"
#             )

# ──────────────────────────────────────────────────────────────
# Parametrized test with clean names + Allure dynamic titles
# ──────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "url, page_name",
    [
        ("https://www.paveddigital.com/", "homepage"),
        ("https://www.paveddigital.com/why-us", "why_us"),
        ("https://www.paveddigital.com/what-we-do", "what_we_do"),
        ("https://www.paveddigital.com/join-us", "join_us"),
        ("https://www.paveddigital.com/contact-us", "contact_us"),
    ],
    ids=lambda x: x[1] if isinstance(x, tuple) else None,
    # ids=["homepage", "why_us", "what_we_do", "join_us", "contact_us"]

)
@allure.epic("Performance & Quality")
@allure.feature("Lighthouse Audits")
@allure.title("Lighthouse Audit → {page_name}")

def test_lighthouse_audit(url, request, page_name):
    """
    Full Lighthouse audit with thresholds and rich Allure reporting.
    `run_lighthouse` fixture should return (json_path, html_path)
    """

    # timestamp hiện tại
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # sanitize tên file từ request.node.name
    safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", request.node.name)
    base_name = f"{timestamp_str}_{safe_name}"

    # safe_name = quote_plus(url)


    with allure.step(f"Running Lighthouse audit for {page_name} → {url}"):
        json_path, html_path = run_lighthouse(url, report_dir="lighthouse_reports")

        with open(json_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        # Extract scores (score is 0–1, convert to %)
        scores = {
            "Performance": report["categories"]["performance"]["score"] * 100,
            "Accessibility": report["categories"]["accessibility"]["score"] * 100,
            "Best Practices": report["categories"]["best-practices"]["score"] * 100,
            "SEO": report["categories"]["seo"]["score"] * 100,
        }

        # Attach full HTML report (clickable in Allure!)
        with open(html_path, "rb") as f:
            allure.attach(
                f.read(),
                name=f"Lighthouse Report - {page_name}",
                attachment_type=AttachmentType.HTML,
                extension="html",
            )

        # Dynamic Allure description with nice formatting
        allure.dynamic.description(f"""
        **Lighthouse Audit Results — {page_name}**  
        **URL:** {url}

        | Category          | Score   | Status       |
        |-------------------|---------|--------------|
        | Performance       | {scores['Performance']:.1f}% | {'Good' if scores['Performance'] >= 90 else 'Fail'} |
        | Accessibility     | {scores['Accessibility']:.1f}% | {'Good' if scores['Accessibility'] >= 90 else 'Warning'} |
        | Best Practices    | {scores['Best Practices']:.1f}% | {'Good' if scores['Best Practices'] >= 90 else 'Warning'} |
        | SEO               | {scores['SEO']:.1f}% | {'Good' if scores['SEO'] >= 90 else 'Warning'} |

        Double-click the attachment above to open the full interactive Lighthouse report.
        """)

        # Fail the test if any critical threshold is not met
        failures = []

        if scores["Performance"] < PERFORMANCE_THRESHOLD * 100:
            failures.append(f"Performance: {scores['Performance']:.1f}% < {PERFORMANCE_THRESHOLD*100}%")

        if scores["Accessibility"] < ACCESSIBILITY_THRESHOLD * 100:
            failures.append(f"Accessibility: {scores['Accessibility']:.1f}% < {ACCESSIBILITY_THRESHOLD*100}%")

        if failures:
            allure.dynamic.severity(allure.severity_level.CRITICAL)
            raise AssertionError(
                f"Lighthouse audit failed for **{page_name}**:\n" + "\n".join(f"  • {f}" for f in failures)
            )
        else:
            allure.dynamic.severity(allure.severity_level.NORMAL)


if __name__ == "__main__":
    pytest.main(["-v", "--alluredir=allure-results"])