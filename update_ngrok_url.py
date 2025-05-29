import requests
import time
import subprocess
import re
import os

def get_ngrok_url():
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels")
        tunnels = response.json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("[ERROR] Could not get ngrok URL:", e)
    return None

def update_index_html(new_url, filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content, count = re.subn(
        r"fetch\('(https?://.*?)/submit'",
        f"fetch('{new_url}/submit'",
        content
    )

    if count > 0:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ index.html updated with new ngrok URL")
        return True
    else:
        print("⚠️ No fetch(...) URL replaced in index.html")
        return False

def git_commit_push():
    try:
        subprocess.run(["git", "add", "index.html"], check=True)
        subprocess.run(["git", "commit", "-m", "Update ngrok URL"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("🚀 Git push complete")
    except subprocess.CalledProcessError as e:
        print("[ERROR] Git operation failed:", e)

if __name__ == "__main__":
    print("🔄 Waiting for ngrok to be ready...")
    ngrok_url = None
    for _ in range(10):
        ngrok_url = get_ngrok_url()
        if ngrok_url:
            break
        time.sleep(1)

    if not ngrok_url:
        print("❌ ngrok URL not found. Is ngrok running?")
        exit(1)

    print(f"🌐 ngrok URL: {ngrok_url}")

    index_path = os.path.join(os.getcwd(), "index.html")
    if update_index_html(ngrok_url, index_path):
        git_commit_push()
    else:
        print("Nothing changed. Aborting push.")
