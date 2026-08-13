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

### mxcli rejects an un-aliased ID column in a view entity (MDL030), which Mendix allows

`mxcli check`/`exec` refuse any view-entity select column without an alias:

```
✗ select column 1 has no as alias: 'o.ID' [MDL030]
  → All select columns in a view entity must have an explicit alias
```

For ordinary columns that matches Mendix. For **ID columns** it does not: the Mendix
docs say the alias is optional there and a default association name is applied
(<https://docs.mendix.com/refguide/view-entities/>). The blanket rule means a model
that a customer *can* build in Studio Pro cannot be expressed in MDL — which is
exactly the model a reproduction needs. Suggest exempting `.ID` columns from MDL030,
or downgrading it to a warning.

(Separately: on 11.13.0 `mx check` *also* rejects the un-aliased ID column — CE0174,
"The name cannot be empty" — so on this version mxcli and mxbuild agree in outcome,
just not for a documented reason. See `repro/NOTES.md`.)

*Verified:* `./mxcli exec repro/02-view-id-without-alias.mdl` errors with MDL030;
`mx check` on the same shape (written by patching the .mpr) errors with CE0174.

### No MDL syntax for a view entity's association; CREATE ASSOCIATION writes an invalid one

Selecting an ID column in a view entity gives the view an association to the source
entity (the dashed line in the domain model). MDL cannot create it:

```sql
CREATE ASSOCIATION Repro.OrderView_SalesOrder FROM Repro.OrderView TO Repro.SalesOrder
  TYPE Reference OWNER Default;
```

succeeds in mxcli but produces `mx check` errors CE6771 ("It is not possible to create
associations to/from View Entities") and CE6770 ("View Entity is out of sync with the
OQL Query"). The difference is the association's `Source`: mxcli writes `null`, while
Studio Pro writes `DomainModels$OqlViewAssociationSource { Reference: "<column alias>" }`.

So a view entity created by mxcli with an ID column in its query is **always**
inconsistent — the OQL references an association that does not exist (CE1613, "The
selected association … no longer exists"). Worth supporting, e.g.
`CREATE VIEW ENTITY … ASSOCIATION Name -> Module.Entity FROM COLUMN alias`.

*Verified:* built both shapes; the hand-patched `OqlViewAssociationSource` version
passes `mx check` with 0 errors and serves data over the association at runtime, so
the missing piece really is just that source object. `repro/mprlib.py` and
`repro/patch-view-assoc.py` show the BSON.

### `Order` is an OQL reserved word — an entity named `Order` breaks view queries

`from Repro.Order as o` inside a view entity fails `mx check` with CE0174 ("The 'Order'
part is incomplete or incorrect … The 'AS' part is incomplete or incorrect. You could
use here: BY."). `mxcli check` passes it. Quoting (`Repro."Order"`) or a different
entity name is the fix; `mxcli syntax domain-model.keywords` documents quoting but
does not list `Order`, and the MDL check does not catch it.

*Verified:* renamed the entity to `SalesOrder` and the same query checks clean.

### Blank app boots clean on 11.13.0

`./mxcli run --local -p ReproApp.mpr` cold-built and served in about a minute, no
build errors; `GET http://localhost:8080/` returns **200**. That is the known-good
starting point every reproduction should be compared against.
