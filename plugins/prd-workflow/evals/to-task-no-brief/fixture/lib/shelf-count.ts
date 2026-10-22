export type Shelf = {
  id: string;
  name: string;
  archived: boolean;
};

export function countShelves(shelves: Shelf[]): number {
  return shelves.length;
}
