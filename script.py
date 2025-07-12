import os
import requests
import subprocess
from datetime import datetime
from bs4 import BeautifulSoup

LEETCODE_USERNAME = "https://leetcode.com/u/vyomap_001/"
GITHUB_REPO_PATH = "/mnt/c/Users/Lenovo/PersonalProjects/LeetCode_Solutions"
GITHUB_COMMIT_MESSAGE = "Update LeetCode solutions"
LANGUAGE = "python3"  # or "cpp", "java", etc.

def get_leetcode_solutions(username):
    print("[*] Fetching problems from LeetCode...")

    headers = {
        "Content-Type": "application/json",
    }

    query = """
    query userProfile($username: String!) {
        allQuestionsCount {
            difficulty
            count
        }
        matchedUser(username: $username) {
            submitStats {
                acSubmissionNum {
                    difficulty
                    count
                    submissions
                }
            }
        }
    }
    """

    url = "https://leetcode.com/graphql"
    res = requests.post(url, json={"query": query, "variables": {"username": username}}, headers=headers)
    
    if res.status_code != 200:
        print("Failed to fetch data from LeetCode.")
        return []

    # Now let's simulate scraping accepted solutions page (since there's no direct API).
    return scrape_solutions(username)


def scrape_solutions(username):
    print("[*] Scraping accepted solutions...")
    # This part only works if you're authenticated. Consider using a session cookie for your account.
    session = requests.Session()
    base_url = f"https://leetcode.com/vyomap_001/submissions/"

    solutions = []

    page = 1
    while True:
        res = session.get(base_url + f"{page}/")
        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.find_all("tr", {"class": "ant-table-row"})
        if not rows:
            break

        for row in rows:
            columns = row.find_all("td")
            if len(columns) < 4 or "Accepted" not in columns[2].text:
                continue

            problem = columns[1].text.strip()
            lang = columns[4].text.strip().lower()

            # Save name and language
            solutions.append((problem, lang))
        
        page += 1

    return solutions


def save_solution(problem_title, code, lang):
    filename = problem_title.replace(" ", "_") + "." + lang
    filepath = os.path.join(GITHUB_REPO_PATH, filename)

    with open(filepath, "w") as f:
        f.write(code)
    print(f"[+] Saved: {filename}")


def push_to_github():
    os.chdir(GITHUB_REPO_PATH)
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", GITHUB_COMMIT_MESSAGE])
    subprocess.run(["git", "push"])
    print("[✓] Pushed to GitHub.")


def main():
    solutions = get_leetcode_solutions(LEETCODE_USERNAME)

    for title, lang in solutions:
        # Skip if not the desired language
        if LANGUAGE not in lang.lower():
            continue

        # Here you need to fetch actual solution code (auth required)
        code = f"# Code for {title}\nprint('Hello World')\n"  # Replace with real code fetch
        save_solution(title, code, "py")  # adjust extension

    push_to_github()


if __name__ == "__main__":
    main()
