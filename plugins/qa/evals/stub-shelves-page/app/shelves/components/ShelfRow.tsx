import { useArchiveShelf, usePurgeShelf, useRestoreShelf } from "../../../lib/hooks/useShelves";
import type { Shelf } from "../../../lib/api";

const PURGE_AFTER_DAYS = 90;

function daysSince(iso: string | null): number {
  if (!iso) return 0;
  return Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000);
}

export function ShelfRow({ shelf, archived = false }: { shelf: Shelf; archived?: boolean }) {
  const archive = useArchiveShelf();
  const restore = useRestoreShelf();
  const purge = usePurgeShelf();
  const archivedFor = daysSince(shelf.archived_at);

  return (
    <li>
      <a href={`/shelves/${shelf.id}`}>{shelf.name}</a>
      <span>{shelf.book_count} books</span>

      {!archived && shelf.permissions.can_archive && (
        <button onClick={() => archive.mutate(shelf.id)}>Archive</button>
      )}

      {archived && shelf.permissions.can_archive && (
        <button onClick={() => restore.mutate(shelf.id)}>Restore</button>
      )}

      {archived && archivedFor > PURGE_AFTER_DAYS && shelf.permissions.can_purge && (
        <button onClick={() => purge.mutate(shelf.id)}>Purge</button>
      )}
    </li>
  );
}
