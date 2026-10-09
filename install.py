#!/usr/bin/env python3
"""Install the game-dev skill set listed in skills.json.

    python install.py                 # user scope: ~/.claude/skills
    python install.py --dest PATH     # e.g. a project's .claude/skills
    python install.py --only roblox-brain,godot-agent-skills
    python install.py --force         # overwrite skills that already exist
    python install.py --no-plugins    # skip `claude plugin install`

Each source repo is cloned at its pinned sha into a temp dir, and only the listed
skill folders are copied (whole folder, so references/ and scripts/ come along).
Hooks are never installed -- see README for why.
"""
import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True, stdout=subprocess.DEVNULL)


def fetch(repo, sha, into):
    run(["git", "init", "-q", into])
    run(["git", "remote", "add", "origin", repo], cwd=into)
    run(["git", "fetch", "-q", "--depth", "1", "origin", sha], cwd=into)
    run(["git", "checkout", "-q", "FETCH_HEAD"], cwd=into)


def fix_frontmatter(skill_md):
    """Rewrite a plain one-line description that YAML can't parse (an inner ': ')
    as a folded block scalar. Upstream blender-staged-scene-construction needs this,
    otherwise Claude Code falls back to the H1 and the skill never triggers."""
    lines = open(skill_md, encoding="utf-8").read().split("\n")
    for i, line in enumerate(lines):
        if i > 0 and line.strip() == "---":
            return False
        if line.startswith("description:"):
            value = line[len("description:"):].strip()
            if value[:1] in ("'", '"', ">", "|") or ": " not in value:
                return False
            lines[i] = "description: >-\n  " + value
            open(skill_md, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
            return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dest", default=os.path.join(os.path.expanduser("~"), ".claude", "skills"))
    ap.add_argument("--only", default="", help="comma-separated source ids")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--no-plugins", action="store_true")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(HERE, "skills.json"), encoding="utf-8"))
    only = {s for s in args.only.split(",") if s}
    os.makedirs(args.dest, exist_ok=True)
    installed, skipped = [], []

    for src in manifest["sources"]:
        if only and src["id"] not in only:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            print(f"fetching {src['id']} @ {src['sha'][:7]}")
            fetch(src["repo"], src["sha"], tmp)
            for pattern in src["skills"]:
                dirs = [d for d in glob.glob(os.path.join(tmp, pattern))
                        if os.path.isfile(os.path.join(d, "SKILL.md"))]
                if not dirs:
                    sys.exit(f"  {pattern}: no SKILL.md found -- upstream layout changed?")
                for d in dirs:
                    name = os.path.basename(d)
                    target = os.path.join(args.dest, name)
                    if os.path.exists(target):
                        if not args.force:
                            skipped.append(name)
                            continue
                        shutil.rmtree(target)
                    shutil.copytree(d, target)
                    if fix_frontmatter(os.path.join(target, "SKILL.md")):
                        print(f"  repaired frontmatter: {name}")
                    installed.append(name)

    print(f"\ninstalled {len(installed)} skills into {args.dest}")
    if skipped:
        print(f"skipped {len(skipped)} that already exist (use --force): {', '.join(skipped)}")

    if not args.no_plugins and not only:
        for p in manifest.get("plugins", []):
            print(f"installing plugin {p['id']}")
            try:
                subprocess.run(["claude", "plugin", "install", p["id"]], check=True)
            except (OSError, subprocess.CalledProcessError) as e:
                print(f"  could not install {p['id']} ({e}); run: claude plugin install {p['id']}")


if __name__ == "__main__":
    main()
