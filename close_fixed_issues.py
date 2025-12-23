#!/usr/bin/env python3
"""Close GitHub issues that have been fixed in the codebase."""

import subprocess
import json
import re
import os

def run_gh(cmd):
    """Run gh command and return parsed JSON."""
    result = subprocess.run(cmd.split(), capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

def check_context_manager():
    """Check if context manager support exists."""
    client_path = "houdiniswap/client.py"
    if os.path.exists(client_path):
        with open(client_path, 'r') as f:
            content = f.read()
            return '__enter__' in content and '__exit__' in content
    return False

def main():
    print("Checking for fixed issues...\n")
    
    # Get all open issues
    open_issues = run_gh("gh issue list --state open --json number,title,body")
    
    issues_to_close = []
    
    for issue in open_issues:
        issue_num = issue['number']
        title = issue['title']
        body = issue.get('body', '')
        
        # Check for context manager (issue #59, audit #51)
        if 'CONTEXT MANAGER' in title or 'audit report issue #51' in body:
            if check_context_manager():
                issues_to_close.append((issue_num, title, "Context manager support (__enter__/__exit__) has been implemented"))
                print(f"Found fixed issue: #{issue_num} - {title}")
    
    if issues_to_close:
        print(f"\nFound {len(issues_to_close)} issue(s) that should be closed:\n")
        for issue_num, title, reason in issues_to_close:
            print(f"  Issue #{issue_num}: {title}")
            print(f"    Reason: {reason}\n")
        
        # Close the issues
        for issue_num, title, reason in issues_to_close:
            try:
                comment = f"Closing: {reason}. Verified in codebase."
                subprocess.run(
                    ['gh', 'issue', 'close', str(issue_num), '--comment', comment],
                    check=True
                )
                print(f"[OK] Closed issue #{issue_num}: {title}")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Failed to close issue #{issue_num}: {e}")
    else:
        print("No issues found that need to be closed.")

if __name__ == '__main__':
    main()

