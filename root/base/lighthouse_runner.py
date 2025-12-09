# base/LighthouseRunner
import os
import json
import subprocess
from pathlib import Path
from glob import glob

class LighthouseRunner:
    @staticmethod
    def run(url: str, mode: str, report_dir: str):
        os.makedirs(report_dir, exist_ok=True)

        safe_name = (
            url.replace("https://", "")
            .replace("http://", "")
            .replace("/", "_")
            .rstrip("_")
        )

        json_path = Path(report_dir) / f"{safe_name}_{mode}.json"
        html_path = Path(report_dir) / f"{safe_name}_{mode}.html"

        # Base command
        base_cmd = [
            "lighthouse", url,
            "--only-categories=performance,accessibility,best-practices,seo",
            "--chrome-flags=--headless --no-sandbox --disable-gpu --disable-dev-shm-usage",
            "--quiet",
            "--output=json",
            "--output=html",
            f"--output-path={json_path.with_suffix('')}",  # lighthouse will add .report.json/.report.html
        ]

        if mode == "desktop":
            base_cmd += [
                "--preset=desktop",                   # this already sets desktop form factor + screen
                "--throttling.cpuSlowdownMultiplier=1",   # THIS DISABLES CPU THROTTLING
                "--throttling.requestLatencyMs=0",
                "--throttling.downloadThroughputKbps=0",
                "--throttling.uploadThroughputKbps=0",
            ]
        else:
            # mobile keeps default throttling (as intended)
            base_cmd += [
                "--emulated-form-factor=mobile",
            ]

        # Run once – both outputs at the same time
        subprocess.run(base_cmd, check=True)

        # Lighthouse always creates:  <stem>.report.json  and  <stem>.report.html
        final_json = json_path.with_suffix(".report.json")
        final_html = html_path.with_suffix(".report.html")

        if final_json.exists():
            final_json.rename(json_path)
        if final_html.exists():
            final_html.rename(html_path)

        return json_path, html_path


    @staticmethod
    def parse_scores(report_json_path:str):
        with open(report_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        categories = data["categories"]

        return {
        "Performance":       categories["performance"]["score"] * 100,
        "Accessibility":     categories["accessibility"]["score"] * 100,
        "BestPractices":     categories.get("best-practices", {}).get("score", 0) * 100,
        "SEO":               categories["seo"]["score"] * 100,
    }
        # return {
        #     "Performance": data["categories"]["performance"]["score"] * 100,
        #     "Accessibility": data["categories"]["accessibility"]["score"] * 100,
        #     "Best Practices": data["categories"]["best-practices"]["score"] * 100,
        #     "SEO": data["categories"]["seo"]["score"] * 100,
        # }

       
