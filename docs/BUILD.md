# Build state: SIH26059 legacy repo

Last updated 6 Oct 2026, before the Docker sandbox reinstall. The v2 rebuild lives in `../SEAICENAV-V2`, and its progress is in that repo's own `STATE.md`.

## Where we are
- `main` on GitHub has every earlier branch merged, from PR #1 to #16. The CMEMS harvest workflow commits one new forecast file every day.
- Two PRs are open, and both are mergeable with no conflicts:
  - **#17, research briefs:** iceberg drift physics, ice hazards, the competitor audit and operational services. Its merge conflict was fixed on 5 Oct.
  - **#18, materials:** the loose files from `~/sih`, meaning the prompt pack, the master prompt, the deck PDF and the images, plus this file and two backlog lines.
- **Next step:** merge #17 and #18 with merge commits, not squash, so every commit counts on your profile.

## Sharing with Claude for deep research
GitHub cannot share a private repo through a link. A secret-gist research pack was blocked by Claude's permission checker. The private route is to merge #17 and #18, connect GitHub in Claude's settings, and add this repo to the research chat.

## Open checks
- The main checkout at `~/sih/SIH26059-antarctic-navigation` was not checked for uncommitted edits. It is also more than 120 commits behind GitHub, so check `git status` there before pulling.

## Worktrees
| Worktree | Branch | State |
|---|---|---|
| main checkout | `main` | Behind GitHub, see above |
| `.claude/worktrees/foamy-seeking-allen` | `materials` | Pushed. It holds `isih/data`, 423 MB |
| `.claude/worktrees/research-briefs` | `worktree-research-briefs` | The local branch is behind GitHub, where it is at `fc8c672` |
| `.claude/worktrees/v3-compliance` | `v3-compliance` | Merged |

Do not delete the `foamy-seeking-allen` worktree. The `isih/data` folder in v3-compliance is a link into it, as the BLOCKER line in `docs/backlog.md` explains.

## Kept local on purpose
- `docs/DIAGRAM_PROMPTS.md`, `_quarantine/`, `isih/data`, and `.venv-demo`, which is your WSL venv.

## After the sandbox reinstall
1. Run `bash /home/jiteesh/sandbox-backup/restore.sh` once in the new sandbox, then restart Claude. `/home/jiteesh/sandbox-backup/README.md` has the details.
2. The ISIH demo venv comes back with the restore. From this worktree, start the demo inside the sandbox with:
   ```
   /home/agent/.venvs/isih-demo/bin/uvicorn isih.demo.app:app --host 0.0.0.0 --port 8000
   ```
   Then publish the port on the host with `sbx ports <name> --publish 8000:8000/tcp`.
3. To run the demo directly on WSL instead, use `.venv-demo/bin/uvicorn isih.demo.app:app --port 8000`.
