import os
import subprocess
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def get_diff():
    print("Getting code diff...")

    try:
        diff = subprocess.check_output(
            ["git", "diff", "HEAD~1", "HEAD"],
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        print(f"Diff length: {len(diff)} characters")
        return diff[:4000]

    except Exception as e:
        print("Error getting diff:", e)
        return "No diff found"


def review_with_ollama(diff):
    print("Sending to Ollama for review...")

    prompt = f"""
You are an AI code reviewer.

Review this code diff and provide:
- Bugs
- Improvements
- Security issues
- Code quality suggestions

Code Diff:
{diff}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        },
        timeout=600
    )

    result = response.json()

    return result.get("response", "No review generated")


def post_github_comment(comment):
    print("Posting comment to GitHub...")

    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")

    if not pr_number:
        print("No PR number found")
        return

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "body": f"## 🤖 Ollama AI Code Review\n\n{comment}"
    }

    response = requests.post(url, json=data, headers=headers)

    if response.status_code == 201:
        print("Comment posted successfully!")
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    diff = get_diff()

    review = review_with_ollama(diff)

    print("Review generated successfully!")

    post_github_comment(review)