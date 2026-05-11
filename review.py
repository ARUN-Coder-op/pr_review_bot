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
        "http://localhost:11434/api/generate",
        json={
            "model": "codellama",
            "prompt": prompt,
            "stream": False
        }
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
    data = {"body": comment}
    requests.post(url, json=data, headers=headers)
    print("Comment posted to GitHub!")

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