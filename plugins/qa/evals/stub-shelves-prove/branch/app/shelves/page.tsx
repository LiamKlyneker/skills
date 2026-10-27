import { useState } from "react";
import { redirect } from "next/navigation";
import { useSession } from "../../lib/session";
import { useShelves } from "../../lib/hooks/useShelves";
import { useHotkey } from "../../lib/hotkeys";
import { flags } from "../../lib/flags";
import { ShelfRow } from "./components/ShelfRow";
import { NewShelfDrawer } from "./components/NewShelfDrawer";

const OVERDUE_AFTER_DAYS = 14;

export default function ShelvesPage() {
  const session = useSession();
  const { data, isLoading, isError } = useShelves(session?.teamId);
  const [drawerOpen, setDrawerOpen] = useState(false);

  useHotkey("n", () => {
    if (data?.viewer.can_create_shelf) setDrawerOpen(true);
  });

  if (!session) redirect("/sign-in?next=/shelves");
  if (isLoading) return <p>Loading shelves…</p>;
  if (isError) return <p role="alert">We couldn't load your shelves. Try again in a minute.</p>;

  const active = data.shelves.filter((shelf) => !shelf.archived_at);
  const archived = data.shelves.filter((shelf) => shelf.archived_at);
  const overdue = data.loans.filter((loan) => loan.days_overdue > OVERDUE_AFTER_DAYS);

  return (
    <main>
      <header>
        <h1>Shelves ({active.length})</h1>
        {data.viewer.can_create_shelf && (
          <button onClick={() => setDrawerOpen(true)}>New shelf</button>
        )}
        {session.role === "owner" && <a href="/shelves/share">Share shelves</a>}
      </header>

      {overdue.length > 0 && (
        <div role="status">{overdue.length} overdue loans — more than two weeks late</div>
      )}

      {active.length === 0 ? (
        <p>No shelves yet.</p>
      ) : (
        <ul>
          {active.map((shelf) => (
            <ShelfRow key={shelf.id} shelf={shelf} />
          ))}
        </ul>
      )}

      {flags.archivedSection && archived.length > 0 && (
        <section>
          <h2>Archived</h2>
          <ul>
            {archived.map((shelf) => (
              <ShelfRow key={shelf.id} shelf={shelf} archived />
            ))}
          </ul>
        </section>
      )}

      <NewShelfDrawer open={drawerOpen} onClose={() => setDrawerOpen(false)} />
    </main>
  );
}
