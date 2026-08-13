#!/usr/bin/env python3
"""Put the view-entity association into the model the way Studio Pro does.

mxcli cannot write either half of this shape:

  * `CREATE VIEW ENTITY ... SELECT o.ID ...` (no alias) is rejected by MDL030,
    even though the Mendix docs say the alias on an ID column is optional;
  * `CREATE ASSOCIATION ... FROM <view entity>` produces a plain association
    (`Source: null`), which mx check rejects with CE6771 — Studio Pro instead
    writes an association whose `Source` is a `DomainModels$OqlViewAssociationSource`.

So this script edits the MPR v2 units directly. Two modes:

  alias    OQL column `o.ID AS OrderView_SalesOrder` + association referencing
           that alias. The control — what mxcli lets you write.
  noalias  OQL column bare `o.ID` + the association Studio Pro derives from it
           (default name, per the docs). The customer's case.

Usage: python3 repro/patch-view-assoc.py alias|noalias
"""

import sys
import uuid

sys.path.insert(0, "repro")
import mprlib

ASSOC_NAME = "OrderView_SalesOrder"
VIEW_ENTITY = "OrderView"
TARGET_ENTITY = "SalesOrder"

OQL_ALIAS = (
    "SELECT\n"
    "    o.ID AS OrderView_SalesOrder,\n"
    "    o.OrderNumber AS OrderNumber,\n"
    "    o.Amount AS Amount\n"
    "  FROM Repro.SalesOrder AS o"
)

OQL_NOALIAS = (
    "SELECT\n"
    "    o.ID,\n"
    "    o.OrderNumber AS OrderNumber,\n"
    "    o.Amount AS Amount\n"
    "  FROM Repro.SalesOrder AS o"
)


def new_id():
    return uuid.uuid4().bytes_le


def delete_behavior():
    return {
        "$ID": new_id(),
        "$Type": "DomainModels$DeleteBehavior",
        "ParentDeleteBehavior": "DeleteMeButKeepReferences",
        "ChildDeleteBehavior": "DeleteMeButKeepReferences",
        "ChildErrorMessage": None,
        "ParentErrorMessage": None,
    }


def view_association(parent_guid, child_guid, reference):
    """An association whose values come from an OQL column, as Studio Pro writes it."""
    ident = new_id()
    return {
        "$ID": ident,
        "$Type": "DomainModels$Association",
        "Name": ASSOC_NAME,
        "Type": "Reference",
        "Owner": "Default",
        "StorageFormat": "Column",
        "DeleteBehavior": delete_behavior(),
        "ParentPointer": parent_guid,
        "Documentation": "",
        "ExportLevel": "Hidden",
        "ChildPointer": child_guid,
        "ParentConnection": "0;50",
        "ChildConnection": "100;50",
        "GUID": ident,
        "Source": {
            "$ID": new_id(),
            "$Type": "DomainModels$OqlViewAssociationSource",
            "Reference": reference,
        },
    }


def main(mode):
    if mode not in ("alias", "noalias"):
        raise SystemExit(__doc__)

    con = mprlib.connect()
    dm_id, dm = mprlib.find_domain_model(con, "Repro")

    entities = {e["Name"]: e for e in dm["Entities"] if isinstance(e, dict)}
    parent = entities[VIEW_ENTITY]["GUID"]
    child = entities[TARGET_ENTITY]["GUID"]

    # Reference is the OQL column alias. With no alias there is nothing to point
    # at, which is the whole question this reproduction asks — keep the
    # association (the dashed line the customer sees) and leave it unreferenced.
    reference = ASSOC_NAME if mode == "alias" else ""

    dm["Associations"] = [x for x in dm["Associations"] if not isinstance(x, dict) or x.get("Name") != ASSOC_NAME]
    dm["Associations"].append(view_association(parent, child, reference))
    mprlib.save(con, dm_id, dm)
    print(f"domain model {dm_id}: association {ASSOC_NAME} -> Reference={reference!r}")

    # And the OQL text itself.
    oql = OQL_ALIAS if mode == "alias" else OQL_NOALIAS
    for u in mprlib.units(con):
        if u["containment"] != "Documents":
            continue
        doc = mprlib.load(u["id"])
        if doc.get("$Type") == "DomainModels$ViewEntitySourceDocument" and doc.get("Name") == VIEW_ENTITY:
            doc["Oql"] = oql
            mprlib.save(con, u["id"], doc)
            print(f"view source {u['id']}: OQL set to the {mode} variant")
            break
    else:
        raise LookupError(f"no ViewEntitySourceDocument named {VIEW_ENTITY}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
