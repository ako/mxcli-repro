"""Read helpers for MPR v2 storage (SQLite index + mprcontents/*.mxunit BSON)."""

import hashlib
import os
import sqlite3
import uuid

import bson

MPR = os.environ.get("MPR", "ReproApp.mpr")
ROOT = os.path.dirname(os.path.abspath(MPR)) or "."


def _guid(hexstr):
    return str(uuid.UUID(bytes_le=bytes.fromhex(hexstr)))


def unit_path(unit_id):
    return os.path.join(ROOT, "mprcontents", unit_id[:2], unit_id[2:4], unit_id + ".mxunit")


def connect():
    return sqlite3.connect(MPR)


def units(con):
    rows = con.execute(
        "select hex(UnitID), hex(ContainerID), ContainmentName, ContentsHash from Unit"
    ).fetchall()
    return [
        {"id": _guid(r[0]), "container": _guid(r[1]) if r[1] else None,
         "containment": r[2], "hash": r[3]}
        for r in rows
    ]


def load(unit_id):
    with open(unit_path(unit_id), "rb") as fh:
        return bson.decode(fh.read())


def file_sha(unit_id):
    path = unit_path(unit_id)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()[:16]


def find_document(con, name, type_hint=None):
    """Return (unit_id, doc) for a document unit by its Name."""
    for u in units(con):
        if u["containment"] not in ("Documents", "ProjectDocuments"):
            continue
        try:
            doc = load(u["id"])
        except Exception:
            continue
        if doc.get("Name") == name and (type_hint is None or type_hint in str(doc.get("$Type"))):
            return u["id"], doc
    raise LookupError(f"no document named {name!r}")


def ids_in(obj, acc=None):
    """Every $ID / GUID byte-value in a unit, as hex — the element identity set."""
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("$ID", "GUID") and isinstance(v, bytes):
                acc.append(v.hex())
            else:
                ids_in(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            ids_in(v, acc)
    return acc
