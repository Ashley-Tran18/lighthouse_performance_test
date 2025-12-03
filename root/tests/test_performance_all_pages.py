# root/tests/test.py
import json
import subprocess
import os

# Ngưỡng performance (80%)
PERFORMANCE_THRESHOLD = 0.80

def run_lighthouse_audit(url: str, output_path: str):
    """Chạy Lighthouse qua CLI, kết nối với Chrome đang mở"""
    print(f"   Running Lighthouse audit for {url}...")
    
    result = subprocess.run([
        "lighthouse", url,
        "--port=9222",
        "--output=json",
        f"--output-path={output_path}",
        "--quiet",
        "--chrome-flags=--headless --no-sandbox --disable-gpu"
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"   Lighthouse failed: {result.stderr}")
        raise RuntimeError(f"Lighthouse audit failed for {url}")


def check_performance(url: str):
    """Kiểm tra performance của một trang"""
    try:
        # Tạo tên file report an toàn
        safe_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
        report_path = f"lighthouse-report-{safe_name}.json"

        run_lighthouse_audit(url, report_path)

        if not os.path.exists(report_path):
            raise FileNotFoundError(f"Report not generated: {report_path}")

        with open(report_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        score = report["categories"]["performance"]["score"]
        print(f"   Performance Score: {score*100:.1f}%")

        if score < PERFORMANCE_THRESHOLD:
            raise AssertionError(
                f"Performance score {score*100:.1f}% < threshold {PERFORMANCE_THRESHOLD*100:.0f}%"
            )
        else:
            print(f"   PASSED (≥ {PERFORMANCE_THRESHOLD*100:.0f}%)")

    except Exception as e:
        print(f"   FAILED: {e}")
        raise  # Để pytest bắt lỗi

# ====================== DANH SÁCH TRANG CẦN TEST ======================
PAGES_TO_TEST = [
    "https://www.paveddigital.com/",
    "https://www.paveddigital.com/why-us",
    # Thêm trang khác ở đây nếu cần
]

# ====================== CHẠY TEST (có thể dùng pytest hoặc python trực tiếp) ======================
from base.base_test import BaseTest
class TestPerformance(BaseTest):
    def test_performance_all_pages(self):
        """Hàm test chính – pytest sẽ tự chạy hàm này"""
        for url in PAGES_TO_TEST:
            check_performance(url)


    if __name__ == "__main__":
        # Nếu chạy trực tiếp: python root/tests/test.py
        print("Bắt đầu kiểm tra Performance với Lighthouse + Selenium".center(80, "="))
        test_performance_all_pages()
        print("HOÀN TẤT! Tất cả trang đã được kiểm tra.".center(80, "="))