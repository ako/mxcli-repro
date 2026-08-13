# ReproApp — a Mendix reproduction sandbox

A scratch Mendix app used to reproduce Mendix customer problems on **11.13.0**,
developed with [mxcli](https://github.com/mendixlabs/mxcli).

## What it is for

In the user's words:

> This app will be used to create reproductions of mendix customer problems on
> 11.13.0. I want to paste a user description, then have to try to reproduce the
> problem. Sometimes it may include security, sometimes not. Commit after creating
> the new mendix app, so we can reset this project after every reproduction.

So the working loop is: paste a problem description → build the smallest model,
pages, microflows and (when relevant) security setup that shows the problem →
confirm the behaviour → **reset back to the clean baseline** and start over on the
next case.

## What it keeps track of

Nothing, deliberately. The baseline is a blank app so that each reproduction starts
from stock 11.13.0 behaviour with nothing inherited from the previous case. Entities,
pages and microflows are added per reproduction and thrown away with the reset.

## Who logs in

The stock `Administrator` role from the blank template. Security is **off** in the
baseline; reproductions that need it turn it on and add roles as the case requires —
that way a security-flavoured repro is explicit about what it enabled, and a
non-security repro is not muddied by it.

## Setup used

| | |
|---|---|
| App | `ReproApp.mpr` at the repo root |
| Mendix version | 11.13.0 |
| Theme | `none` (stock Atlas — a repro should look like a customer's stock app) |
| mxcli | nightly (`.claude/bootstrap-mxcli.sh` refetches it; pin with `MXCLI_TAG`) |
| Database | local PostgreSQL, database `reproapp` |

## Resetting between reproductions

The clean app is commit **`234e412`** ("Provision blank Mendix 11.13.0 app ReproApp as
the reproduction baseline"). To throw a reproduction away:

```bash
git reset --hard 234e412 && git clean -fd    # back to the blank app
./mxcli run --local --setup --ensure-db -p ReproApp.mpr
```

A local tag `baseline` points at that commit for convenience, so `git reset --hard
baseline` works in this working copy. The tag is **not** on the remote — this session's
git proxy rejects tag pushes with HTTP 403 — so in a fresh clone use the SHA, or
re-create the tag with `git tag baseline 234e412`.

`git clean -fd` removes any files a reproduction added; it leaves git-ignored files
such as the `mxcli` binary and the MxBuild caches alone, which is what you want.

That resets the *model*, not the *data*. If a reproduction left rows behind that
would pollute the next one, drop and recreate the database as well:

```bash
dropdb -h 127.0.0.1 -U mendix reproapp && createdb -h 127.0.0.1 -U mendix -O mendix reproapp
./mxcli run --local --setup --ensure-db -p ReproApp.mpr
```

To keep a reproduction instead of discarding it, commit it on its own branch off
`baseline` before resetting.

## Working on a reproduction

```bash
./mxcli run --local -p ReproApp.mpr --watch --screenshot   # warm dev loop
./mxcli exec change.mdl -p ReproApp.mpr                    # edit the model
```

The app serves at http://localhost:8080/. See `AGENTS.md` for the mxcli command
reference and `.ai-context/skills/` for the MDL guides (`mdl-entities.md`,
`create-page.md`, `write-microflows.md`, `manage-security.md`, `run-local.md`).

`FINDINGS.md` collects anything surprising or broken hit along the way — that is
durable context for the next session and the most useful thing to report back to
mxcli.
