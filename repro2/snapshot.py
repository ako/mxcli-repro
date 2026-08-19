#!/usr/bin/env python3
"""Snapshot the model's units, or compare two snapshots.

  python3 repro2/snapshot.py save  <label>          write a snapshot
  python3 repro2/snapshot.py diff  <labelA> <labelB> compare two snapshots

A snapshot records, per unit: the ContentsHash the .mpr index carries, a sha of the
.mxunit file on disk, and — for the nanoflow and javascript action under test — the
set of element $ID/GUIDs inside it. That last part is what decides whether a rewrite
is cosmetic or whether every element got a new identity, which is what Studio Pro's
version-control view keys on.
"""

import json
import os
import sys

sys.path.insert(0, "repro2")
import mprlib

DIR = "/tmp/claude-0/-home-user-mxcli-repro/f197c8e3-a078-59d8-8a57-d4f4e061119d/scratchpad"
WATCH = ("ONL_AIAdvisor", "JS_LoadAiAdvisor", "SUB_HomeScan_AiAdvisorSettings")


def save(label):
    con = mprlib.connect()
    snap = {"units": {}, "watch": {}}
    for u in mprlib.units(con):
        snap["units"][u["id"]] = {
            "containment": u["containment"],
            "hash": u["hash"],
            "file": mprlib.file_sha(u["id"]),
        }
    for name in WATCH:
        try:
            uid, doc = mprlib.find_document(con, name)
        except LookupError:
            continue
        snap["watch"][name] = {"unit": uid, "ids": sorted(mprlib.ids_in(doc))}
        with open(f"{DIR}/{label}-{name}.json", "w") as fh:
            json.dump(json.loads(json.dumps(doc, default=lambda b: b.hex())), fh, indent=1)
    with open(f"{DIR}/{label}.json", "w") as fh:
        json.dump(snap, fh, indent=1)
    print(f"snapshot {label}: {len(snap['units'])} units, watching {list(snap['watch'])}")


def diff(a, b):
    A = json.load(open(f"{DIR}/{a}.json"))
    B = json.load(open(f"{DIR}/{b}.json"))
    changed = [u for u in B["units"] if u in A["units"] and A["units"][u]["file"] != B["units"][u]["file"]]
    added = [u for u in B["units"] if u not in A["units"]]
    removed = [u for u in A["units"] if u not in B["units"]]

    print(f"=== units: {len(changed)} changed, {len(added)} added, {len(removed)} removed")
    for u in changed:
        print(f"    changed {u} ({B['units'][u]['containment']})")

    print("\n=== watched documents")
    for name in WATCH:
        wa, wb = A["watch"].get(name), B["watch"].get(name)
        if not wa or not wb:
            continue
        ia, ib = set(wa["ids"]), set(wb["ids"])
        touched = wb["unit"] in changed
        if not touched:
            print(f"  {name}: byte-identical")
            continue
        kept, fresh, gone = ia & ib, ib - ia, ia - ib
        print(f"  {name}: REWRITTEN — {len(ia)} element ids before, {len(ib)} after; "
              f"{len(kept)} kept, {len(fresh)} new, {len(gone)} dropped")
        if ib and not kept:
            print("      every element identity changed → whole document reads as changed")


if __name__ == "__main__":
    os.makedirs(DIR, exist_ok=True)
    if sys.argv[1] == "save":
        save(sys.argv[2])
    else:
        diff(sys.argv[2], sys.argv[3])
