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

The numbers come from GitHub's events API, which keeps roughly the last 30
days and at most 300 events. That is the window this record claims, and no
more. Without GH_TOKEN, or with a token that cannot see private repositories,
only public pushes are counted, and the record says so rather than implying
the private number is zero.
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
OUT = Path(__file__).resolve().parent.parent / "backend" / "resources" / "github-activity.md"


def fetch_events():
    """Every event the API still has for USER, newest first."""
    # Authenticated as the user, this endpoint includes private events; the
    # /public variant is the honest fallback when there is no token.
    path = f"/users/{USER}/events" if TOKEN else f"/users/{USER}/events/public"
    events = []
    for page in (1, 2, 3):
        req = urllib.request.Request(
            f"https://api.github.com{path}?per_page=100&page={page}",
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "github-activity-record",
                **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                batch = json.load(res)
        except urllib.error.HTTPError as err:
            # Pages past the end answer 422 rather than an empty list.
            if err.code == 422 and page > 1:
                break
            raise
        if not batch:
            break
        events.extend(batch)
    return events


def day(date):
    """`2 November 2026`, without the platform-specific %-d."""
    return f"{date.day} {date.strftime('%B %Y')}"


def times(n, word="push"):
    return f"{n} {word}" if n == 1 else f"{n} {word}es"


def main():
    now = datetime.now(timezone.utc)
    since = now - timedelta(days=DAYS)

    pushes = []
    for event in fetch_events():
        if event.get("type") != "PushEvent":
            continue
        # The workflow's own commits are the bot's, not hers.
        if event.get("actor", {}).get("login") != USER:
            continue
        at = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if at < since:
            continue
        pushes.append((at, event["repo"]["name"].split("/", 1)[-1], bool(event.get("public"))))

    public = [p for p in pushes if p[2]]
    private = [p for p in pushes if not p[2]]
    private_repos = {name for _, name, _ in private}
    public_by_repo = Counter(name for _, name, _ in public)
    last_public = {}
    for at, name, _ in public:
        last_public[name] = max(at, last_public.get(name, at))
    active_days = {at.date() for at, _, _ in pushes}
    repo_count = len(public_by_repo) + len(private_repos)

    # Log what was seen, names of private repositories excluded: this output is
    # readable by anyone who opens the workflow run.
    print(
        f"{len(pushes)} pushes in {DAYS} days: {len(public)} public in "
        f"{len(public_by_repo)} repos, {len(private)} private in {len(private_repos)} repos. "
        f"Token: {'yes' if TOKEN else 'no'}."
    )

    if pushes:
        headline = (
            f"{times(len(pushes))} to {repo_count} "
            f"{'repository' if repo_count == 1 else 'repositories'} on {len(active_days)} "
            f"different {'day' if len(active_days) == 1 else 'days'} in the last {DAYS} days"
        )
    else:
        headline = f"no pushes in the last {DAYS} days"

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
    ]

    if pushes:
        lines.append(f"- {headline[0].upper()}{headline[1:]}.")
        lines.append(f"- Most recent push: {day(max(at for at, _, _ in pushes))}.")
    else:
        lines.append(f"- No pushes in the last {DAYS} days.")

    lines += ["", "## Public repositories"]
    if public_by_repo:
        for name, n in sorted(public_by_repo.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- {name}: {times(n)}, the latest on {day(last_public[name])}")
    else:
        lines.append(f"- No pushes to public repositories in the last {DAYS} days.")

    lines += ["", "## Private repositories"]
    if not TOKEN:
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
