"""Read/write helpers for MPR v2 storage (SQLite index + mprcontents/*.mxunit BSON).

Used by the view-entity reproduction to write model shapes that mxcli's MDL
front-end refuses (a bare `o.ID` OQL column, and the OqlViewAssociationSource
that Studio Pro creates for it).
"""

import base64
import hashlib
import os
import sqlite3
import uuid

import bson

MPR = os.environ.get("MPR", "ReproApp.mpr")
ROOT = os.path.dirname(os.path.abspath(MPR)) or "."


def _guid(hexstr):
    """MPR stores GUIDs as .NET little-endian blobs; file names use the UUID form."""
    return str(uuid.UUID(bytes_le=bytes.fromhex(hexstr)))


def unit_path(unit_id):
    return os.path.join(ROOT, "mprcontents", unit_id[:2], unit_id[2:4], unit_id + ".mxunit")


def units(con):
    rows = con.execute(
        "select hex(UnitID), hex(ContainerID), ContainmentName, ContentsHash from Unit"
    ).fetchall()
    return [
        {
            "id": _guid(r[0]),
            "container": _guid(r[1]) if r[1] else None,
            "containment": r[2],
            "hash": r[3],
        }
        for r in rows
    ]


def load(unit_id):
    with open(unit_path(unit_id), "rb") as fh:
        return bson.decode(fh.read())


def save(con, unit_id, doc):
    """Write the unit back and refresh its ContentsHash (base64 sha256 of the BSON)."""
    raw = bson.encode(doc)
    with open(unit_path(unit_id), "wb") as fh:
        fh.write(raw)
    digest = base64.b64encode(hashlib.sha256(raw).digest()).decode()
    con.execute(
        "update Unit set ContentsHash = ? where UnitID = ?",
        (digest, uuid.UUID(unit_id).bytes_le),
    )
    con.commit()
    return digest


def find_domain_model(con, module_name):
    """Return (unit_id, doc) for a module's domain model."""
    all_units = units(con)
    by_id = {u["id"]: u for u in all_units}
    for u in all_units:
        if u["containment"] != "DomainModel":
            continue
        mod = by_id.get(u["container"])
        if not mod:
            continue
        if load(mod["id"]).get("Name") == module_name:
            return u["id"], load(u["id"])
    raise LookupError(f"no domain model for module {module_name!r}")


def connect():
    return sqlite3.connect(MPR)
