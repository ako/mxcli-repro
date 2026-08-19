# Ticket 2 — "Studio Pro shows the entire nanoflow as changed"

**Customer report.** Studio Pro's version-control view shows the whole nanoflow as
changed even when only one parameter of a JavaScript action call changed, which makes
the changes display useless. `CREATE OR MODIFY` should be idempotent so documents
already in sync are not touched.

**Verdict: confirmed, and it is worse than nanoflows.** Any change to a nanoflow *or*
microflow rewrites the entire document with fresh element identities. The "already in
sync" half of the complaint is, however, already satisfied — a no-op re-run genuinely
writes nothing.

Versions: Mendix 11.13.0, mxcli `nightly-20260814-fa886b81`, MPR v2.

## What was measured

`repro2/snapshot.py` records every unit's `ContentsHash`, a sha of its `.mxunit` file,
and the set of `$ID`/`GUID` values inside the documents under test. Studio Pro's
version control keys on those element identities, so "how many survived a write" is
the number that decides whether a diff is readable.

The customer's script is `repro2/01-aiadvisorsessionresume.mdl`, applied verbatim.
`repro2/00-scaffolding.mdl` only supplies the modules, entities and `SUB_` microflow it
references — none of that is the subject of the ticket.

## Results

| run | action | units changed | element ids in the nanoflow |
|---|---|---|---|
| 1→2 | re-apply the **identical** script | **0** | byte-identical, file mtime untouched |
| 2→3 | change **one** parameter (`toggleButtonColor`) | 1 | **1 kept, 36 new, 36 dropped** (of 37) |
| 3→4 | revert that parameter | 1 | 1 kept, 36 new, 36 dropped |
| 5→6 | change one literal in the **microflow** | 1 | **1 kept, 21 new, 21 dropped** (of 22) |

### 1. Already-in-sync documents are genuinely not touched

Re-running the customer's script against a model that already matches it changes
nothing: 0 units differ and the `.mxunit` mtime is unchanged to the nanosecond.

```
mtime before: 2026-08-19 09:12:32.492620585 +0000
mtime after:  2026-08-19 09:12:32.492620585 +0000
```

But the command still prints

```
Modified javascript action: MxCore.JS_LoadAiAdvisor
Replaced nanoflow: HomeScan.ONL_AIAdvisor
```

so the output claims two writes that did not happen. The idempotency is real; only the
reporting is wrong. Anyone diagnosing this from console output alone would conclude
mxcli is rewriting on every run — it is not.

### 2. One changed parameter regenerates every element identity

The true delta between run 1 and run 3, with `$ID`/`GUID`/`*Pointer` fields stripped,
is exactly **two lines** — one argument value:

```
-        "Argument": "$TextHelper/Text3"
+        "Argument": "$Brand/Name"
```

Yet 36 of the nanoflow's 37 element identities are new. The single survivor is the
document's own id. Every activity, parameter mapping and flow connector gets a fresh
GUID, and each `OriginPointer`/`DestinationPointer` is rewritten to match — which is
precisely why Studio Pro paints the whole nanoflow as changed.

### 3. The identities are regenerated, not derived from content

Applying the change and then reverting it produces a model that is **semantically
identical** to where it started — `run1 == run4` once identity and pointer fields are
stripped — but with another 36 fresh GUIDs. So the ids are minted per write rather
than derived from the document's content.

This is what makes the damage cumulative: a round-trip that changes nothing still
leaves every element looking modified in version control.

### 4. Not specific to nanoflows

The same one-literal change to `SUB_HomeScan_AiAdvisorSettings` (a microflow) rewrote
21 of its 22 element ids. `CREATE OR MODIFY` on either document type is
drop-and-recreate, not a merge — the "Replaced …" wording in the output is accurate
about what it does when it does write.

## What a fix would need

Preserve element identities across a rewrite: match existing elements to incoming ones
(by position in the flow, or by name where there is one) and reuse their `$ID`/`GUID`
instead of minting new ones, so that only genuinely changed elements show up as
changed. Failing that, `CREATE OR MODIFY` cannot be used on a version-controlled
project without destroying the diff.

Secondary: stop printing "Modified"/"Replaced" for writes that were skipped.

## Reproducing

```bash
./mxcli exec repro2/00-scaffolding.mdl -p ReproApp.mpr
./mxcli exec repro2/01-aiadvisorsessionresume.mdl -p ReproApp.mpr
python3 repro2/snapshot.py save before
./mxcli exec repro2/02-one-param-changed.mdl -p ReproApp.mpr
python3 repro2/snapshot.py save after
python3 repro2/snapshot.py diff before after
```
