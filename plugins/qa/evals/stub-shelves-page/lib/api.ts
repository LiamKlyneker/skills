export type Shelf = {
  id: string;
  name: string;
  book_count: number;
  archived_at: string | null;
  permissions: { can_archive: boolean; can_purge: boolean };
};

export type Loan = { id: string; shelf_id: string; days_overdue: number };

export type ShelvesResponse = {
  viewer: { can_create_shelf: boolean };
  shelves: Shelf[];
  loans: Loan[];
};

async function request(method: string, path: string, body?: unknown) {
  const response = await fetch(path, {
    method,
    headers: { "content-type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`${method} ${path} answered ${response.status}`);
  return response.status === 204 ? null : response.json();
}

export const api = {
  get: (path: string) => request("GET", path),
  post: (path: string, body?: unknown) => request("POST", path, body),
  delete: (path: string) => request("DELETE", path),
};
