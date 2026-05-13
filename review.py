import os
import subprocess
import requests

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"


def get_diff():
    print("Getting code diff...")

    try:
        diff = subprocess.check_output(
            ["git", "diff", "--stat"],
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        print(diff)

        return diff[:300]

    except Exception as e:
        print("Error:", e)
        return "No diff"


def review_with_ollama(diff):
    print("Sending to Ollama for review...")

    prompt = f"Review this briefly:\n{diff}"

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "tinyllama",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    return response.json()["response"]


def post_github_comment(comment):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    pr_number = os.environ.get("PR_NUMBER")

    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }

    data = {
        "body": f"## AI Review\n\n{comment}"
    }

    response = requests.post(url, json=data, headers=headers)

    print(response.status_code)
    print("Comment posted successfully")


if __name__ == "__main__":
    diff = get_diff()

    review = review_with_ollama(diff)

    print("Review generated!")

    post_github_comment(review)