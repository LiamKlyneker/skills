export type ChipProps = {
  name: string;
  shelved?: boolean;
};

export function Chip({ name, shelved = false }: ChipProps) {
  return (
    <span className="inline-flex items-center rounded-[--radius-tile] border-solid border-[length:--space-hairline] border-[--color-edge] bg-[--color-surface]">
      <span className={`type-label ${shelved ? 'text-[--color-ink-muted]' : 'text-[--color-ink]'}`}>
        {name}
      </span>
    </span>
  );
}
