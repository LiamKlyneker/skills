type Shelf = { id: string; name: string; archivedAt: string | null };

const PURGE_AFTER_DAYS = 90;

function daysSince(iso: string): number {
  return (Date.now() - Date.parse(iso)) / 86_400_000;
}

export function ShelvesScreen({
  shelves,
  isOwner,
  onArchive,
  onPurge,
}: {
  shelves: Shelf[];
  isOwner: boolean;
  onArchive: (id: string) => void;
  onPurge: (id: string) => void;
}) {
  const active = shelves.filter((shelf) => shelf.archivedAt === null);
  const archived = shelves.filter((shelf) => shelf.archivedAt !== null);
  return (
    <section>
      <h1>Shelves ({active.length})</h1>
      <ul>
        {active.map((shelf) => (
          <li key={shelf.id}>
            {shelf.name}
            {isOwner && <button onClick={() => onArchive(shelf.id)}>Archive</button>}
          </li>
        ))}
      </ul>
      <details>
        <summary>Archived</summary>
        <ul>
          {archived.map((shelf) => (
            <li key={shelf.id}>
              {shelf.name}
              {daysSince(shelf.archivedAt!) > PURGE_AFTER_DAYS && (
                <button onClick={() => onPurge(shelf.id)}>Purge</button>
              )}
            </li>
          ))}
        </ul>
      </details>
    </section>
  );
}
