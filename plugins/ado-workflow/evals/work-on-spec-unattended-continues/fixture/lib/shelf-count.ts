export interface Shelf {
  id: string;
  archived: boolean;
}

export function countShelves(shelves: Shelf[]): number {
  return shelves.length;
}
