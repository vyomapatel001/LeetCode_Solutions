import os
import requests
import subprocess
from dotenv import load_dotenv

# Load env variables
load_dotenv()
SESSION = os.getenv("LEETCODE_SESSION")
CSRF = os.getenv("CSRFTOKEN")

# Local repo path
GITHUB_REPO_PATH = "/mnt/c/Users/Lenovo/PersonalProjects/LeetCode_Solutions"
GITHUB_COMMIT_MESSAGE = "Update LeetCode solutions"

# Set up session
session = requests.Session()
session.cookies.set("LEETCODE_SESSION", SESSION)
session.cookies.set("csrftoken", CSRF)
session.headers.update({
    "x-csrftoken": CSRF,
    "referer": "https://leetcode.com",
    "user-agent": "Mozilla/5.0"
})

def get_accepted_submissions(limit=20):
    print("[*] Fetching submissions from LeetCode...")
    url = "https://leetcode.com/graphql"
    payload = {
        "operationName": "mySubmissions",
        "variables": {"offset": 0, "limit": limit},
        "query": """
        query mySubmissions($offset: Int!, $limit: Int!) {
            submissionList(offset: $offset, limit: $limit) {
                submissions {
                    id
                    title
                    titleSlug
                    statusDisplay
                    lang
                    timestamp
                }
            }
        }
        """
    }
    r = session.post(url, json=payload)
    subs = r.json()['data']['submissionList']['submissions']
    return [s for s in subs if s['statusDisplay'] == "Accepted"]

def fetch_solution_code(submission_id):
    url = f"https://leetcode.com/api/submissions/{submission_id}/"
    res = session.get(url)
    if res.status_code == 200:
        return res.json().get("code")
    return None

def save_solution(title, code, lang, submission_id):
    lang_map = {
        "python3": "py",
        "pythondata": "py",   # Pandas
        "mysql": "sql",
        "bash": "sh",
        "c": "c",
        "cpp": "cpp",
        "java": "java"
    }

    ext = lang_map.get(lang.lower(), "txt")
    safe_title = title.strip().replace(" ", "_").replace("-", "_")
    filename = f"{safe_title}_{submission_id}.{ext}"

    lang_folder = os.path.join(GITHUB_REPO_PATH, ext)
    os.makedirs(lang_folder, exist_ok=True)

    filepath = os.path.join(lang_folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    print(f"[+] Saved: {filepath}")

def git_push():
    os.chdir(GITHUB_REPO_PATH)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", GITHUB_COMMIT_MESSAGE], check=True)
    
    push = subprocess.run(["git", "push"], capture_output=True, text=True)
    
    if "no upstream branch" in push.stderr:
        print("[!] No upstream branch. Setting upstream...")
        subprocess.run(["git", "push", "--set-upstream", "origin", "automation"], check=True)
    else:
        print("[✓] Pushed to GitHub.")

def main():
    submissions = get_accepted_submissions(limit=10)
    
    for sub in submissions:
        code = fetch_solution_code(sub["id"])
        if code:
            save_solution(sub["title"], code, sub["lang"])
        else:
            print(f"[!] Skipped {sub['title']} - No code found.")

    git_push()

if __name__ == "__main__":
    main()
