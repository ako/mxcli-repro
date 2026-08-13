# FINDINGS

Durable notes from working in this repo: mxcli commands that errored, workarounds
applied, and anything that behaved differently from what the skills describe. Append
as you go — this is what the next session (and the mxcli maintainers) get to read.

**Versions in use**

- Mendix 11.13.0 (MxBuild + runtime from `cdn.mendix.com`, cached in `~/.mxcli/`)
- mxcli `nightly-20260813-4b15694f` (built 2026-08-13T04:40:49Z)
- Linux x86_64, local PostgreSQL, database `reproapp`

---

## 2026-08-13 — bootstrap

### `mxcli new` + move-to-root collides with an existing `.ai-context/`

`bootstrap-app.md` says to unpack the skills first (`mxcli init --sync-skills`, which
creates `.ai-context/skills/` at the repo root), then later create the app in a
subfolder and `mv <AppName>/* .` up to the root. But `mxcli new` writes its own
`.ai-context/` inside the app folder, and `mv` refuses to merge into a non-empty
directory:

```
mv: cannot overwrite './.ai-context': Directory not empty
```

Worked around by deleting the root `.ai-context/` before the move (`mxcli new` writes
an identical copy from the same binary, so nothing is lost). The skill's step 1 could
mention this, or the move could be a `cp -a` + `rm -rf`.

*Verified:* reproduced once, on an empty repo containing only `LICENSE`; after
`rm -rf .ai-context` the move succeeded and `.ai-context/skills/` at the root has the
same 65 files.

### Post-move SessionStart hook was correct as generated

`bootstrap-app.md` step 1 warns to check the `.mpr` named in
`.claude/bootstrap-mxcli.sh` after moving the app up. Here it was already right
(`MPR='ReproApp.mpr'`) and every path in it is relative to the repo root, so no edit
was needed. *Verified:* read the generated script after the move.

### `mxcli run` has no flag to recreate the database

`--ensure-db` provisions the database if missing, but there is no `--recreate-db` /
`--drop-db`. For a repo whose whole workflow is "reset between reproductions", a
recreate flag would be the natural companion to the `git reset --hard baseline` step.
Working around it with `dropdb`/`createdb` (documented in `README.md`).

*Verified:* `./mxcli run --help` lists only `--db-host/--db-name/--db-user/
--db-password/--ensure-db/--setup`.

### Tag pushes are blocked in the Claude Code cloud session (environment, not mxcli)

`git push origin refs/tags/baseline` fails with `error: RPC failed; HTTP 403` from the
session's git proxy, while pushing the branch itself succeeds. So the baseline is
pinned by commit SHA (`234e412`) in `README.md` rather than by a pushed tag; the local
tag exists but stays local. Not an mxcli issue — noted so the next session does not
spend time on it.

*Verified:* branch push in the same shell succeeded (`09fa266..234e412`);
`git ls-remote --tags origin` lists no `baseline`.

### Blank app boots clean on 11.13.0

`./mxcli run --local -p ReproApp.mpr` cold-built and served in about a minute, no
build errors; `GET http://localhost:8080/` returns **200**. That is the known-good
starting point every reproduction should be compared against.
