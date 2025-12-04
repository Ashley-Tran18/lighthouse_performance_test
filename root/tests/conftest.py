import os
import subprocess
from datetime import datetime
import pytest

@pytest.fixture
def run_lighthouse(request):
    """
    Fixture chạy Lighthouse CLI cho 1 URL.
    Tạo report JSON + HTML trong thư mục lighthouse_reports.
    """

    def _run(url, report_dir="lighthouse_reports"):
        os.makedirs(report_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{timestamp}_{request.node.name}"

        json_path = os.path.join(report_dir, f"{base_name}.json")
        html_path = os.path.join(report_dir, f"{base_name}.html")

        # Lệnh chạy Lighthouse CLI
        cmd = [
            "lighthouse",
            url,
            "--quiet",
            "--chrome-flags='--headless'",
            f"--output=json",
            f"--output-path={json_path}",
            f"--output=html",
            f"--output-path={html_path}"
        ]

        # Chạy subprocess
        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Lighthouse failed:\n{result.stderr}")

        return json_path, html_path

    return _run
