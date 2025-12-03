import os
import sys
import subprocess
import platform
import zipfile
import shutil
import requests

def get_chrome_version():
    system = platform.system()
    try:
        if system == "Windows":
            process = subprocess.run(
                r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version',
                capture_output=True, text=True, shell=True
            )
            version_line = process.stdout.strip().split()[-1]
        elif system == "Darwin":
            process = subprocess.run(
                ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
                capture_output=True, text=True
            )
            version_line = process.stdout.strip().split()[-1]
        else:
            process = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True)
            version_line = process.stdout.strip().split()[-1]
        return version_line
    except Exception as e:
        print("Không lấy được phiên bản Chrome:", e)
        sys.exit(1)

def download_chromedriver(chrome_version):
    major_version = chrome_version.split(".")[0]
    try:
        response = requests.get(f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}")
        driver_version = response.text.strip()
        print(f"ChromeDriver phiên bản phù hợp: {driver_version}")
        
        zip_url = f"https://chromedriver.storage.googleapis.com/{driver_version}/chromedriver_linux64.zip"
        zip_path = f"chromedriver_{driver_version}.zip"
        r = requests.get(zip_url, stream=True)
        with open(zip_path, "wb") as f:
            f.write(r.content)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        os.remove(zip_path)
        
        shutil.move("chromedriver", "/usr/local/bin/chromedriver")
        os.chmod("/usr/local/bin/chromedriver", 0o755)
        print("Cập nhật ChromeDriver thành công!")
    except Exception as e:
        print("Tải ChromeDriver thất bại:", e)
        sys.exit(1)

def main():
    chrome_version = get_chrome_version()
    print("Phiên bản Chrome hiện tại:", chrome_version)
    
    try:
        output = subprocess.run(["chromedriver", "--version"], capture_output=True, text=True)
        driver_version = output.stdout.strip().split()[1]
        print("Phiên bản ChromeDriver hiện tại:", driver_version)
        if chrome_version.split(".")[0] != driver_version.split(".")[0]:
            print("ChromeDriver không tương thích, cập nhật...")
            download_chromedriver(chrome_version)
        else:
            print("ChromeDriver đã tương thích, không cần update.")
    except FileNotFoundError:
        print("Chưa có ChromeDriver, tải mới...")
        download_chromedriver(chrome_version)

if __name__ == "__main__":
    main()
