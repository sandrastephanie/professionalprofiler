#!/usr/bin/env python3
"""
Writes backend/resources/github-activity.md: Sandra's pushes on GitHub over the
last 30 days, as a CV record the chat can answer from.

Run by .github/workflows/github-activity.yml once a week, or by hand:

    GH_TOKEN=... python3 scripts/github-activity.py

What it says, and what it leaves out, is a decision rather than a default:

- Pushes are counted. Repositories are never described.
- A public repository is named, because its name is public already.
- A private repository is only counted. Its name stays out of this file, which
  lives in a public repository.

Standard library only, so the workflow needs no install step.

The numbers come from each repository's activity list, over GitHub's "month"
window, cut to the last 30 days. Without GH_TOKEN, or with a token that cannot
read every private repository, the private count is missing or partial, and
the record says it was not counted rather than implying it is zero.

The token needs to list her repositories and read their activity: a
fine-grained token with access to all repositories and Contents: read-only.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

USER = os.environ.get("GH_USER", "sandrastephanie")
TOKEN = os.environ.get("GH_TOKEN", "")
DAYS = 30
PUSH_TYPES = {"push", "force_push", "branch_creation"}
OUT = Path(__file__).resolve().parent.parent / "backend" / "resources" / "github-activity.md"


def api(path):
    """One GET against the GitHub API, as JSON."""
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-activity-record",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=30) as res:
        return json.load(res)


def fetch_repos():
    """Her own repositories: all of them with a token, the public ones without."""
    path = "/user/repos?affiliation=owner" if TOKEN else f"/users/{USER}/repos?type=owner"
    repos = []
    for page in range(1, 6):
        batch = api(f"{path}&per_page=100&page={page}")
        repos.extend(batch)
        if len(batch) < 100:
            break
    return repos


def fetch_pushes(repos):
    """Her pushes in the last month, asked of each repository in turn.

    Not the events feed, which was the first attempt: it gives a fine-grained
    token the public events only, without an error, and the record then said
    there had been no private pushes. A repository's own activity list is
    covered by a permission that can be granted and checked (Contents, read).

    A private repository the token may not read is skipped and counted as
    unreadable, so the record can say the count is partial.
    """
    pushes, unreadable = [], 0
    for repo in repos:
        try:
            # `month` is GitHub's own window for this endpoint; 100 pushes to
            # one repository in a month is far above what is expected here.
            items = api(
                f"/repos/{repo['full_name']}/activity"
                "?time_period=month&per_page=100"
            )
        except urllib.error.HTTPError as err:
            if err.code in (403, 404) and repo["private"]:
                unreadable += 1
                continue
            raise
        for item in items:
            # GitHub files the first push of a new branch, and a force push,
            # under their own types; both are pushes. A merged pull request is
            # a button on the website, not a push, and is left out.
            if item.get("activity_type") not in PUSH_TYPES:
                continue
            # The workflow's own commits are the bot's, not hers.
            if (item.get("actor") or {}).get("login") != USER:
                continue
            at = datetime.fromisoformat(item["timestamp"].replace("Z", "+00:00"))
            pushes.append((at, repo["name"], not repo["private"]))
    return pushes, unreadable


def day(date):
    """`2 November 2026`, without the platform-specific %-d."""
    return f"{date.day} {date.strftime('%B %Y')}"


def times(n, word="push"):
    return f"{n} {word}" if n == 1 else f"{n} {word}es"


def main():
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=DAYS)

    repos = fetch_repos()
    private_listed = sum(1 for r in repos if r["private"])
    found, unreadable = fetch_pushes(repos)
    pushes = [p for p in found if p[0] >= since]

    public = [p for p in pushes if p[2]]
    private = [p for p in pushes if not p[2]]
    private_repos = {name for _, name, _ in private}
    public_by_repo = Counter(name for _, name, _ in public)
    last_public = {}
    for at, name, _ in public:
        last_public[name] = max(at, last_public.get(name, at))
    active_days = {at.date() for at, _, _ in pushes}
    repo_count = len(public_by_repo) + len(private_repos)
    # Counted in full only if every private repository listed could be read.
    private_counted = private_listed > 0 and unreadable == 0

    # Log what was seen, names of private repositories excluded: this output is
    # readable by anyone who opens the workflow run.
    print(
        f"{len(pushes)} pushes in {DAYS} days: {len(public)} public in "
        f"{len(public_by_repo)} repos, {len(private)} private in {len(private_repos)} repos. "
        f"Token: {'yes' if TOKEN else 'no'}. "
        f"Private repos listed: {private_listed}, unreadable: {unreadable}."
    )

    # The headline only covers what was counted, so it names the public scope
    # when the private pushes are missing.
    scope = "" if private_counted else "public "
    if pushes:
        headline = (
            f"{times(len(pushes))} to {repo_count} {scope}"
            f"{'repository' if repo_count == 1 else 'repositories'} on {len(active_days)} "
            f"different {'day' if len(active_days) == 1 else 'days'} in the last {DAYS} days"
        )
    else:
        headline = f"no {scope}pushes in the last {DAYS} days"

    lines = [
        "---",
        "title: GitHub activity",
        "type: activity",
        "tags: [github, activity, building, coding, side-projects, how-i-spend-my-time]",
        f'summary: "What I have pushed to GitHub lately - {headline}. Counted automatically, updated {day(now)}."',
        "---",
        "",
        "## What this is",
        f"A count of my pushes on GitHub (github.com/{USER}), made automatically once a week. "
        f"It covers the last {DAYS} days and was last updated on {day(now)}. "
        "It shows how much I'm building and how often, not what each repository is.",
        "",
        f"## The last {DAYS} days",
        f"- {headline[0].upper()}{headline[1:]}.",
    ]
    if pushes:
        lines.append(f"- Most recent push: {day(max(at for at, _, _ in pushes))}.")

    lines += ["", "## Public repositories"]
    if public_by_repo:
        for name, n in sorted(public_by_repo.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {name}: {times(n)}, the latest on {day(last_public[name])}")
    else:
        lines.append(f"- No pushes to public repositories in the last {DAYS} days.")

    lines += ["", "## Private repositories"]
    if not private_counted:
        lines.append("- Not counted in this update. Most of my work is in private repositories.")
    elif private:
        lines.append(
            f"- {times(len(private))} to {len(private_repos)} private "
            f"{'repository' if len(private_repos) == 1 else 'repositories'}. "
            "I keep these private until I'm happy with them, so they are counted but not named."
        )
    else:
        lines.append(f"- No pushes to private repositories in the last {DAYS} days.")

    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as err:
        # Fail loudly: a workflow that writes an empty record on a bad token
        # would quietly tell hirers she has stopped building.
        sys.exit(f"GitHub answered {err.code} for {err.url}")
