import os
import subprocess
import datetime
import streamlit as st

def auto_git_push(workspace_dir: str):
    """
    Streamlit Cloud or local env helper to automatically stage, commit, 
    and push newly evolved organisms (*.py and *.md files) back to GitHub main branch.
    """
    # 1. Retrieve GITHUB_TOKEN from Streamlit Secrets or Environment Variables
    token = None
    try:
        if hasattr(st, "secrets") and "GITHUB_TOKEN" in st.secrets:
            token = st.secrets["GITHUB_TOKEN"]
    except Exception:
        pass
        
    if not token:
        token = os.environ.get("GITHUB_TOKEN")
        
    # 2. Configure Git bot identity
    try:
        subprocess.run(["git", "config", "--global", "user.name", "13 Apostles Bot"], capture_output=True)
        subprocess.run(["git", "config", "--global", "user.email", "bot@13apostles.internal"], capture_output=True)
        
        # Stage newly created files
        subprocess.run(["git", "add", "."], capture_output=True, cwd=workspace_dir)
        
        # Check if there are actual diffs to commit
        status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, cwd=workspace_dir)
        if not status.stdout.strip():
            print("[Auto-Git] No changes to push.")
            return True
            
        # Commit the modifications
        commit_msg = f"chore: Auto-commit newly evolved organisms [web run {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]"
        subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, cwd=workspace_dir)
        
        # 3. Push to GitHub
        if token:
            # Inject token securely to bypass password prompts in headless cloud
            remote_url = f"https://{token}@github.com/eljja/13apostles.git"
            res = subprocess.run(["git", "push", "-f", remote_url, "HEAD:main"], capture_output=True, text=True, cwd=workspace_dir)
            if res.returncode == 0:
                print("[Auto-Git] Successfully pushed newly evolved organisms to GitHub main branch!")
                return True
            else:
                print(f"[Auto-Git] Push failed: {res.stderr}")
                return False
        else:
            # Fallback to local default push in development env
            res = subprocess.run(["git", "push", "-f", "13apostles", "HEAD:main"], capture_output=True, text=True, cwd=workspace_dir)
            return res.returncode == 0
            
    except Exception as e:
        print(f"[Auto-Git] Exception during auto-commit: {str(e)}")
        return False
