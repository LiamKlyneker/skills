import { useState } from "react";
import { useCreateShelf } from "../../../lib/hooks/useShelves";

export function NewShelfDrawer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [name, setName] = useState("");
  const create = useCreateShelf();

  if (!open) return null;

  return (
    <aside aria-label="New shelf">
      <label>
        Shelf name
        <input value={name} onChange={(event) => setName(event.target.value)} />
      </label>
      <button
        disabled={name.trim().length === 0}
        onClick={() => create.mutate(name, { onSuccess: onClose })}
      >
        Create
      </button>
      <button onClick={onClose}>Cancel</button>
    </aside>
  );
}
