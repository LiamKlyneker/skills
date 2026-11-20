# ADR 0029 — Test data is made on demand, from recipes

- **Status**: Accepted
- **Date**: 2026-11-20
- **Context**: PRD #330
- **Amends**: ADR [0022](0022-knowledge-is-derived-accounts-are-observed.md) and ADR
  [0028](0028-setup-states-may-create-data-under-write-rules.md), on three clauses: 0022's "the pass
  never creates data", 0028's same clause for `prove-branch`, and 0028's decision that a chain is
  kept in the consumer's knowledge file. The rest of both stands: knowledge is derived from code,
  and the five write rules.

## Context

ADR 0022 and ADR 0028 kept data creation away from `prove-branch` for two reasons. An external
tester that writes the data it judges can no longer be trusted about it. A search or a chain on the
path of every run puts a project's data machinery in front of every verdict. Both reasons are
sound, and they were the right answer while the pass could only read.

The rule cost more than it protected. A developer prepared every page by hand, in three commands
per page, and the project stored a catalogue of states that someone had found in advance. On the
run behind PRD #330, one page had 27 states and 22 open questions, and 15 of those asked "which
item on staging has ...?". Most of those states are never needed by any branch. An app with no org
in its routes made `setup-states` ask for an org id (#328). An app whose items are made in a
sibling admin app had nothing for observation to walk, and the chain table was never read (#329).

The rule also protected less than it said. A flow under test already submits forms and creates
items on the target, under no write rule at all. Only the data a flow starts from was forbidden,
and that is the data the developer then made by hand.

## Decision

**`prove-branch` makes the start data of a flow itself, on demand, from recipes.** A recipe is a
small file per kind of item, in user words, that says where the item is made, the steps, and where
it is seen (`plugins/qa/skills/references/recipe-file.md`). A run resolves the data a flow starts
from in this order: a `fresh` item an earlier run made, an item a recipe makes now, a link the
developer gives, Unable to verify. Each item a run makes is listed in one made-items file
(`plugins/qa/skills/references/made-items-file.md`) and is used again until a flow changes it.

**Three guards and one mitigation answer the reason that 0022 and 0028 gave.**

1. **A separate driver makes the data, under the five write rules of ADR 0028.** The flow drivers
   and the grader do not see how the data was made. A bug in the branch under test cannot break
   the making of its own start data, because arrange drives staging and only the flows under test
   drive the preview.
2. **The grader judges what the branch's code does with the item.** The item is only the start
   point. A verdict never rests on the item existing.
3. **The receipt lists every item the run made.** The developer sees what the pass wrote.
4. **Made items are used again.** A chain of items runs only when its item is missing or used, so a
   chain is not on the path of every run.

One more fact belongs in this record: a flow under test writes to the target today. A flow stays
free to pay, delete or change an item, because a criterion can ask for it. One write rule is added
for it, and it is the only one: a name a flow types starts with `qa-setup`.

**The knowledge file stops carrying how a state is made.** Recipes replace the chain table, the
seeder hint and the "which item holds it" questions. A recipe holds the connection between two apps
at the level of the item (`Made in`, `Seen in`), not of a module.

**No recipe runs a seeder, an end-to-end command, a database query or a writing API.** A recipe is
a walk in the app's own screens. A project that forbids staging writes is never arranged: the run
asks for a link to each item it needs, once.

## Invariants that change

These written rules were true under 0022 and 0028 and stop being true. Each skill that states one
is changed by a later slice of PRD #330, not by this record.

- `prove-branch` "never asks the developer for a URL, an org id, an order number or any other id of
  a state". It asks for a link to an item at the gate, when no recipe can make it.
- The missing-account stop that "asks for no id and invites none". A missing item is made by a
  recipe or asked for as a link at the gate.
- "`accounts.md` has three writers". The file is replaced by the made-items file, which `prove-branch`
  writes and `setup-env` writes once.
- The developer is pulled in for "exactly four things". The list changes with the gate.
- Flows that start from a state are "dispatched at once". They wait for the arrange drivers, which
  run one at a time in `Needs` order.
- The driver's one-origin rule for a non-setup flow. A flow under test may cross the origins of the
  apps the adapter lists, when a sub-step names the app.

## Considered and dropped

- **Keep the rule and ask for more states in `setup-states`.** It is the catalogue that failed:
  states a branch never needs, and a file format the developer has to fit the product into.
- **Run the project's seeder.** Its machinery would sit on the path of every run, and the reason
  0022 gave for dropping it still holds. No recipe runs one.
- **Share recipes between repos through a store.** Each repo keeps its own copy. A recipe in a
  sibling repo is read, never written.
- **Delete made items at the end of a run.** A run never deletes a `qa-setup` item. A cleanup
  would need the delete permission that write rule 2 withholds, and an item left standing is what
  the next run uses again.

## Consequences

- A developer prepares a project with `/qa:setup` and `/qa:setup-env`, then runs `prove-branch`.
- A project holds only recipes that a drive proved, and the files fail soft: a recipe that fails
  costs the flows that needed it, and the next run learns it again.
- Staging fills with `qa-setup` items. The name prefix and the made-items file are how a person who
  shares the environment recognises them.
- ADR 0027's default holds: no eval case is added for this change.
