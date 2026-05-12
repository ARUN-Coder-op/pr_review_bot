import subprocess
import requests
import os

def get_git_diff():
    result = subprocess.run(
        ["git", "diff", "HEAD~1", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout

def review_with_ollama(diff_text):
    prompt = f"""You are a code reviewer. Review this code change and give helpful comments:

{diff_text}

Give clear, simple feedback about:
1. Any bugs or errors
2. Code quality issues
3. Suggestions to improve
"""
    response = requests.post(
        "http://host.docker.internal:11434/api/generate",
        json={
            "model": "codellama",
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    return response.json()["response"]

def post_github_comment(comment):
    token = os.environ.get("GITHUB_TOKEN")
    repo = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")

    url = f"https://api.github.com/repos/{repo}/commits/{sha}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {"body": f"## 🤖 Ollama AI Code Review\n\n{comment}"}
    response = requests.post(url, json=data, headers=headers)
    
    if response.status_code == 201:
        print("✅ Comment posted to GitHub!")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("Getting code diff...")
    diff = get_git_diff()
    
    if not diff:
        print("No changes found.")
    else:
        print("Sending to Ollama for review...")
        review = review_with_ollama(diff)
        print("Review done! Posting to GitHub...")
        post_github_comment(review)