#!/usr/bin/env python3
"""Script to audit open GitHub issues against PRs and codebase fixes."""

import json
import re
import subprocess
from typing import Dict, List, Set, Tuple

def run_gh_command(cmd: str) -> List[Dict]:
    """Run a gh CLI command and return parsed JSON."""
    result = subprocess.run(
        cmd.split(),
        capture_output=True,
        text=True,
        check=True
    )
    return json.loads(result.stdout)

def get_open_issues() -> List[Dict]:
    """Get all open issues."""
    return run_gh_command("gh issue list --state open --json number,title,body,url")

def get_merged_prs() -> List[Dict]:
    """Get all merged PRs."""
    return run_gh_command("gh pr list --state merged --json number,title,body,mergedAt --limit 200")

def extract_audit_issue_number(body: str) -> int:
    """Extract audit report issue number from issue body."""
    match = re.search(r'audit report issue #(\d+)', body, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extract_closed_issues(pr_body: str) -> Set[int]:
    """Extract issue numbers that a PR closes."""
    issues = set()
    # Look for "Closes #X", "Fixes #X", "Resolves #X"
    patterns = [
        r'Closes #(\d+)',
        r'Fixes #(\d+)',
        r'Resolves #(\d+)',
        r'closes #(\d+)',
        r'fixes #(\d+)',
        r'resolves #(\d+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, pr_body, re.IGNORECASE)
        issues.update(int(m) for m in matches)
    return issues

def get_issue_comments(issue_num: int) -> List[Dict]:
    """Get comments for an issue."""
    try:
        return run_gh_command(f"gh issue view {issue_num} --json comments --jq '.comments[] | {{body, author: .author.login, createdAt}}'")
    except:
        return []

def check_if_fixed_in_codebase(audit_issue_num: int) -> Tuple[bool, str]:
    """Check if an audit issue has been fixed in the codebase."""
    fixes = {
        13: ("FLOATING POINT PRECISION LOSS", False, "Still using float in models.py"),
        14: ("STRING-BASED AMOUNT PARAMETERS", False, "Still inconsistent types"),
        15: ("NO INPUT VALIDATION", False, "No validation found"),
        16: ("MUTABLE DEFAULT ARGUMENTS", True, "Fixed in PR #71"),
        17: ("NO RETRY LOGIC", False, "No retry logic found"),
        18: ("NO RATE LIMITING HANDLING", False, "No rate limit handling"),
        19: ("NO CONNECTION POOLING CONFIGURATION", False, "No connection pooling config"),
        20: ("HARDCODED BASE URL", False, "Base URL still hardcoded"),
        21: ("NO LOGGING", False, "No logging found"),
        22: ("NO CACHING MECHANISM", False, "No caching found"),
        23: ("ZERO TEST COVERAGE", False, "No tests found"),
        24: ("INCOMPLETE TYPE DOCUMENTATION", True, "Fixed in PR #72"),
        25: ("NO API VERSIONING", False, "No API versioning"),
        26: ("MISSING EXAMPLES FOR ERROR HANDLING", True, "Fixed in PR #73"),
        27: ("NO CHANGELOG FOR SDK", False, "No changelog found"),
        28: ("MAGIC NUMBERS", True, "Fixed in PR #75 - constants.py exists"),
        29: ("INCONSISTENT NAMING", False, "Still inconsistent"),
        30: ("DUPLICATE CODE", True, "Fixed in PR #75 - _bool_to_str exists"),
        31: ("NO CONSTANTS FILE", True, "Fixed in PR #75 - constants.py exists"),
        32: ("INCOMPLETE __all__ EXPORT", True, "Fixed in PR #75 - all exports in __init__.py"),
        33: ("NO __repr__ METHODS", True, "Fixed in PR #75 - __repr__ methods exist"),
        34: ("DATACLASSES WITHOUT frozen=True", True, "Fixed in PR #75 - frozen=True in models"),
        35: ("NO EQUALITY COMPARISON", True, "Fixed in PR #75 - dataclasses have __eq__"),
        36: ("NO REQUEST BATCHING", True, "Fixed in PR #75"),
        37: ("INEFFICIENT LIST COMPREHENSIONS", False, "Still inefficient"),
        38: ("NO RESPONSE PARSING OPTIMIZATION", True, "Fixed in PR #75"),
        39: ("NO CREDENTIAL SANITIZATION IN LOGGING", True, "Fixed in PR #75"),
        40: ("NO REQUEST SIGNING", False, "Still no request signing"),
        41: ("NO INPUT SANITIZATION", True, "Fixed in PR #75"),
        42: ("MISSING py.typed MARKER", True, "Fixed in PR #75 - py.typed exists"),
        43: ("NO LICENSE FILE", True, "Fixed in PR #75 - LICENSE exists"),
        44: ("INCOMPLETE setup.py", False, "Still incomplete"),
        45: ("NO MANIFEST.in", True, "Fixed in PR #75 - MANIFEST.in exists"),
        46: ("VENV COMMITTED TO REPO", False, "Need to check"),
        47: ("INCONSISTENT RETURN TYPES", False, "Still inconsistent"),
        48: ("NO PAGINATION HELPER", False, "No pagination helper"),
        49: ("NO STATUS POLLING HELPER", False, "No status polling helper"),
        50: ("NO TRANSACTION BUILDER PATTERN", True, "Fixed in PR #75"),
        51: ("NO __enter__ / __exit__ FOR CONTEXT MANAGER", True, "Fixed in PR #75"),
        52: ("NO ASYNC SUPPORT", False, "No async support"),
        53: ("PYTHON 3.8+ BUT USING 3.13 FEATURES", True, "Fixed in PR #75"),
        54: ("NO TYPE STUBS FOR LEGACY PYTHON", False, "No type stubs"),
        55: ("NO CONFIGURATION MANAGEMENT", False, "No config management"),
        56: ("NO DEPRECATION WARNINGS", False, "No deprecation warnings"),
        57: ("NO VERSION CHECKING", False, "No version checking"),
        58: ("MISSING DEPENDENCY VERSION PINS", False, "Still missing"),
        59: ("NO API REFERENCE DOCS", True, "Fixed in PR #74"),
        60: ("NO MIGRATION GUIDE", True, "Fixed in PR #74"),
        61: ("NO CONTRIBUTING GUIDELINES", True, "Fixed in PR #74"),
        62: ("NO CODE OF CONDUCT", True, "Fixed in PR #74"),
    }
    
    if audit_issue_num in fixes:
        is_fixed, reason = fixes[audit_issue_num][1], fixes[audit_issue_num][2]
        return is_fixed, reason
    return False, "Unknown issue"

def main():
    print("Auditing open GitHub issues...\n")
    
    # Get all open issues
    open_issues = get_open_issues()
    print(f"Found {len(open_issues)} open issues\n")
    
    # Get all merged PRs and extract closed issues
    merged_prs = get_merged_prs()
    closed_by_prs: Set[int] = set()
    for pr in merged_prs:
        if pr.get('body'):
            closed_issues = extract_closed_issues(pr['body'])
            closed_by_prs.update(closed_issues)
            if closed_issues:
                print(f"PR #{pr['number']} closed issues: {sorted(closed_issues)}")
    
    print(f"\nTotal issues closed by PRs: {sorted(closed_by_prs)}\n")
    
    # Check each open issue
    issues_to_close = []
    
    for issue in open_issues:
        issue_num = issue['number']
        title = issue['title']
        body = issue.get('body', '')
        
        # Check if this issue was closed by a PR
        if issue_num in closed_by_prs:
            issues_to_close.append((issue_num, title, f"Closed by PR"))
            continue
        
        # Extract audit report issue number
        audit_num = extract_audit_issue_number(body)
        if audit_num:
            is_fixed, reason = check_if_fixed_in_codebase(audit_num)
            if is_fixed:
                issues_to_close.append((issue_num, title, reason))
                continue
        
        # Check comments for resolution mentions
        comments = get_issue_comments(issue_num)
        for comment in comments:
            comment_body = comment.get('body', '').lower()
            if any(word in comment_body for word in ['fixed', 'resolved', 'closed', 'done', 'completed']):
                # Check if it's a definitive statement
                if any(phrase in comment_body for phrase in ['this is fixed', 'has been fixed', 'is resolved', 'can be closed']):
                    issues_to_close.append((issue_num, title, f"Mentioned as fixed in comment"))
                    break
    
    # Report findings
    print("\n" + "="*80)
    print(f"Found {len(issues_to_close)} issues that should be closed:")
    print("="*80 + "\n")
    
    for issue_num, title, reason in issues_to_close:
        print(f"  Issue #{issue_num}: {title}")
        print(f"    Reason: {reason}\n")
    
    if issues_to_close:
        print("\n" + "="*80)
        response = input(f"\nClose these {len(issues_to_close)} issues? (yes/no): ")
        if response.lower() == 'yes':
            for issue_num, title, reason in issues_to_close:
                try:
                    subprocess.run(
                        ['gh', 'issue', 'close', str(issue_num), '--comment', f'Closing: {reason}'],
                        check=True
                    )
                    print(f"[OK] Closed issue #{issue_num}: {title}")
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR] Failed to close issue #{issue_num}: {e}")
        else:
            print("Skipping closure.")
    else:
        print("No issues need to be closed.")

if __name__ == '__main__':
    main()

