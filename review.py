import subprocess
import requests
import os
pr_number = os.environ.get("PR_NUMBER")
import sys

def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD"],
        capture_output=True
    )
    return result.stdout.decode("utf-8", errors="ignore")

def review_with_ollama(diff_text):
    prompt = f"Review this code change briefly:\n\n{diff_text}\n\nGive short feedback on bugs and improvements."
    
    response = requests.post(
        "http://127.0.0.1:11434/api/generate",
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": 600
            }
        },
        timeout=300
    )
    return response.json()["response"]

def post_github_comment(comment):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")
    pr_number = os.environ.get("PR_NUMBER")

if pr_number:
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
else:
    print("No PR number found")
    exit()
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": f"## 🤖 Ollama AI Code Review\n\n{comment}"}
    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Comment posted to GitHub!")
    else:
        print(f"Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Getting code diff...")
    diff = get_git_diff()
    print(f"Diff length: {len(diff)} characters")

    if not diff:
        print("No changes found.")
        sys.exit(0)
    else:
        print("Sending to Ollama for review...")
        review = review_with_ollama(diff)
        print("Review done! Posting to GitHub...")
        post_github_comment(review)