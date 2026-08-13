# Repro 1 — view entity: ID column without an alias

**Customer report**

> When using View Entities and selecting an ID of an entity, you don't get any error
> design time when it's isn't named with an alias. The domain model shows a dashed
> line, indicating a sort of association, so everything seems fine. However, when
> deployed, an error occurs when retrieving over that association, because it's
> missing the alias. It's weird that forgetting an alias does raise errors for any
> other column, but no error is raised when it's forgotten for assocation/ID columns.

**Verdict: does not reproduce on Mendix 11.13.0.** The missing alias on an ID column
*is* reported at design time (CE0174) and the app **cannot be deployed** — so the
runtime failure they describe is unreachable on this version. The asymmetry they
describe (error for ordinary columns, silence for ID columns) is not present: both
are errors, with different messages.

## Model used

`Repro` module, built by `01-base-model.mdl`:

- `Repro.Customer` (Name)
- `Repro.SalesOrder` (OrderNumber, OrderDate, Amount)
- `Repro.SalesOrder_Customer`: SalesOrder → Customer (reference)
- `Repro.OrderView`: view entity over SalesOrder, selecting `o.ID` to get the
  association back to `Repro.SalesOrder`

The entity is `SalesOrder`, not `Order`: `Order` is an OQL reserved word (`ORDER BY`)
and `from Repro.Order as o` fails with its own CE0174, which would muddy the result.

## Results

Design-time check is `mx check` (`~/.mxcli/mxbuild/11.13.0/modeler/mx`) — the same
consistency-check engine Studio Pro runs. Studio Pro itself is not available in this
container, so the GUI editor's own behaviour on save was not observed.

| OQL select list | `mx check` |
|---|---|
| `o.ID AS OrderView_SalesOrder` (ID aliased) | **0 errors** |
| `o.ID` (ID not aliased — the reported case) | **CE0174** "All columns of the first select query must have a correct name. **The name cannot be empty.**" |
| `o.OrderNumber` (ordinary column not aliased) | **CE0174** "… **An attribute must have a simple name or an alias.**" |

The no-alias error is build-blocking, not a warning. `./mxcli run --local` on that
model ends with:

```
"status": "Failure",
"message": "The project cannot be deployed, because it contains errors."
  [error] CE0174 "Error(s) in OQL query: All columns of the first select query must
          have a correct name. The name cannot be empty." at Entity 'Repro.OrderView'
```

Whether the association carries the default name (`Reference: "OrderView_SalesOrder"`),
an empty reference, or a null one makes no difference — CE0174 comes from the OQL text
itself. All three were tried.

The aliased version, by contrast, deploys and works. With one Customer and one
SalesOrder inserted, retrieving **over the view association** returns data:

```
$ ./mxcli oql -p ReproApp.mpr "SELECT ov.OrderNumber AS ViewNum, o.OrderNumber AS SrcNum, c.Name AS CustomerName
    FROM Repro.OrderView AS ov
    JOIN ov/Repro.OrderView_SalesOrder/Repro.SalesOrder AS o
    JOIN o/Repro.SalesOrder_Customer/Repro.Customer AS c"
| SrcNum | ViewNum | CustomerName |
| SO-1   | SO-1    | Acme BV      |
```

## The docs disagree with 11.13.0

<https://docs.mendix.com/refguide/view-entities/> states, for an ID column in the
select list:

> the alias is optional. If the alias is omitted, a default name following the
> association naming convention will be applied.

and shows `SELECT o.ID, o.OrderDate AS OrderDate` as a valid query. On 11.13.0 that
exact shape is a build-blocking CE0174. So either the documentation is ahead of (or
behind) the product, or the behaviour changed between versions.

**This is the most useful thing to take back to the customer:** ask which Mendix
version they saw it on. If their Studio Pro drew a dashed line and raised nothing,
they are on a version that accepts a model 11.13.0 rejects — and the fix on 11.13.0
is simply to alias the ID column.

## How to re-run

```bash
./mxcli exec repro/01-base-model.mdl -p ReproApp.mpr
./mxcli exec repro/03-view-id-with-alias.mdl -p ReproApp.mpr
python3 repro/patch-view-assoc.py alias      # control: expect 0 errors
~/.mxcli/mxbuild/11.13.0/modeler/mx check ReproApp.mpr

python3 repro/patch-view-assoc.py noalias    # customer's shape: expect CE0174
~/.mxcli/mxbuild/11.13.0/modeler/mx check ReproApp.mpr
./mxcli run --local -p ReproApp.mpr          # fails: cannot be deployed
```

## Why the .mpr had to be patched by hand

Neither half of the customer's model can be written with mxcli MDL — see
`FINDINGS.md` for both limitations. `patch-view-assoc.py` (with `mprlib.py`) edits the
MPR v2 units directly:

- the view entity's OQL lives in a `DomainModels$ViewEntitySourceDocument` unit as
  plain text (`Oql`);
- the association Studio Pro derives from an ID column is a normal
  `DomainModels$Association` whose `Source` is a
  `DomainModels$OqlViewAssociationSource { Reference: "<the alias>" }`, where a
  hand-written association has `Source: null`;
- view-entity attributes bind to columns the same way, via
  `DomainModels$OqlViewValue { Reference: "<the alias>" }`.

That the aliased hand-built model passes `mx check` with 0 errors **and** serves data
over the association at runtime is the evidence that this reconstruction is faithful,
not an artefact.
