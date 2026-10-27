# Shelves

Route: /shelves
Purpose: A team member sees the team's shelves, opens one, and archives, restores or purges a shelf.
Derived at: 0c1d2e3 · 2026-09-30
Environment: none

## What the user sees

| Section | Role | Shows when | State | Origin |
|---|---|---|---|---|
| Sign-in page in place of the shelves | Anyone signed out | the visitor is not signed in; after signing in they return to the shelves | any | code |
| "Loading shelves…" | Any team member | the team's shelves have not arrived yet | any | code |
| "We couldn't load your shelves" message | Any team member | the app could not fetch the team's shelves | any | code |
| Page title with the number of shelves | Any team member | the shelves have loaded; the number leaves out archived shelves | S1, S2 | code |
| Overdue loans banner with the number of overdue loans | Any team member | at least one loan is more than 14 days overdue | S3 | code |
| "No shelves yet." | Any team member | the team has no shelf that is not archived | S2 | code |
| Shelf list | Any team member | the team has at least one shelf that is not archived | S1 | code |
| Each shelf's name and number of books | Any team member | on every shelf in the list and in the Archived section | S1 | code |
| Archived section | Any team member | the team has at least one archived shelf | S4 | code |
| New shelf drawer with a name box | A member who may create shelves | the member pressed New shelf or the N key | S1, S2 | code |

## What the user can do

| Action | Role | Allowed when | Result the user sees | Origin |
|---|---|---|---|---|
| Open a shelf from its name | Any team member | always | the shelf's own page opens | code |
| New shelf button | A member who may create shelves | the app says the member may create a shelf [Q2] | the New shelf drawer opens | code |
| Press N | A member who may create shelves | the app says the member may create a shelf [Q2], and the cursor is not in a text box | the New shelf drawer opens | code |
| Share shelves link | Team owner | the member is the team's owner | the sharing page opens | code |
| Archive a shelf | A member who may archive that shelf | the app says the member may archive this shelf [Q1] | the shelf moves to the Archived section and the title's number drops by one | code |
| Restore an archived shelf | A member who may archive that shelf | the app says the member may archive this shelf [Q1] | the shelf moves back to the shelf list | code |
| Purge an archived shelf | A member who may purge that shelf | the shelf was archived more than 90 days ago and the app says it may be purged [Q3] | the shelf disappears for good | code |
| Create, in the New shelf drawer | A member who may create shelves | a name is typed | the drawer closes and the new shelf appears in the list | code |
| Cancel, in the New shelf drawer | A member who may create shelves | always | the drawer closes and nothing is saved | code |

## States

| Id | State, in user terms | Env | Known account | Seeder (for a human) | Origin |
|---|---|---|---|---|---|
| S1 | The team has at least one shelf that is not archived | both | none known | `seed:shelf` | code |
| S2 | The team has no shelf, or only archived ones | both | none known | none known | code |
| S3 | A loan on one of the team's shelves, recorded in the library's lending desk app, is more than 14 days overdue | both | none known | `seed:overdue-loan` | code |
| S4 | The team has an archived shelf | both | none known | `seed:archived-shelf` | code |
| S5 | The team has a shelf archived more than 90 days ago | both | none known | `seed:archived-shelf` | code |

## Open questions

| Id | Question | Blocks | Answer | Origin |
|---|---|---|---|---|
| Q1 | Who may archive or restore a shelf? The page only asks the app yes or no. | S1, S4 | — | — |
| Q2 | Who may create a shelf? The page only asks the app yes or no. | S1, S2 | — | — |
| Q3 | Who may purge a shelf archived more than 90 days ago? The page only asks the app yes or no. | S5 | — | — |
| Q4 | Which team on staging has a shelf archived more than 90 days ago? | S5 | — | — |
| Q5 | Which team on staging has a loan more than 14 days overdue? Loans are recorded in the lending desk app, never on this page. | S3 | — | — |
