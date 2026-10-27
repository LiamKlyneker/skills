type Shelf = { id: string; name: string };

export function ShelvesScreen({ shelves }: { shelves: Shelf[] }) {
  return (
    <section>
      <h1>Shelves ({shelves.length})</h1>
      <ul>
        {shelves.map((shelf) => (
          <li key={shelf.id}>{shelf.name}</li>
        ))}
      </ul>
    </section>
  );
}
