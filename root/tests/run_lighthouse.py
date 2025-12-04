import subprocess
import json
from pathlib import Path

def audit_url(url: str, output_dir: str = "reports"):
    Path(output_dir).mkdir(exist_ok=True)
    
    report_path = Path(output_dir) / f"{url.replace('https://', '').replace('/', '_')}.report.json"
    
    cmd = [
        "lighthouse",
        url,
        "--only-categories=performance",      # remove this line if you want all categories
        "--chrome-flags=--headless --no-sandbox --disable-gpu",
        "--output=json",
        f"--output-path={report_path}",
        "--quiet"
    ]
    
    print(f"Running Lighthouse on {url} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("Error:", result.stderr)
        return None
    
    with open(report_path) as f:
        data = json.load(f)
    
    score = data["categories"]["performance"]["score"] * 100
    print(f"Performance score: {score:.1f}/100")
    print(f"Full report → {report_path}")
    
    return data

# Example usage
if __name__ == "__main__":
    urls = [
        "https://example.com",
        # add more URLs here
    ]
    
    for url in urls:
        audit_url(url)