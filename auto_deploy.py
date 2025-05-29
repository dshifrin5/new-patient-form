import subprocess
import time
import requests
import re

# Set this to your actual Render Static Site ID and API Key
RENDER_SERVICE_ID = "srv-d0r3fbfdiees73blq330"
RENDER_API_KEY = "rnd_PVTkldXhRNq8DwWypV9FzBihMVjd"

def start_ngrok():
    ngrok_proc = subprocess.Popen(["ngrok", "http", "5002"], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    time.sleep(5)  # Wait for ngrok to initialize
    response = requests.get("http://localhost:4040/api/tunnels")
    public_url = response.json()["tunnels"][0]["public_url"]
    print(f"[+] Ngrok URL: {public_url}")
    return ngrok_proc, public_url

def update_index_html(public_url):
    with open("index.html", "r", encoding="utf-8") as file:
        html = file.read()

    # Replace any existing ngrok or localhost URL
    updated = re.sub(
        r"https?://[a-z0-9\-]+\.ngrok-free\.app|http://localhost:5002",
        public_url,
        html
    )

    if html != updated:
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(updated)
        print("[+] index.html updated with new ngrok URL")
        return True
    else:
        print("[~] No changes needed — URL already current.")
        return False

def commit_and_push_changes():
    subprocess.run(["git", "add", "index.html"], check=True)
    subprocess.run(["git", "commit", "-m", "Auto-update ngrok URL"], check=False)
    subprocess.run(["git", "push", "--set-upstream", "origin", "main"], check=False)
    print("[+] Pushed to GitHub")

def trigger_render_deploy():
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(
        f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys",
        headers=headers
    )
    if response.status_code == 201:
        print("[🚀] Render deployment triggered successfully.")
    else:
        print(f"[!] Failed to trigger deployment: {response.text}")

if __name__ == "__main__":
    ngrok_proc, new_url = start_ngrok()
    try:
        changed = update_index_html(new_url)
        if changed:
            commit_and_push_changes()
        else:
            print("[~] Skipped commit and push.")
        trigger_render_deploy()
    finally:
        ngrok_proc.terminate()
