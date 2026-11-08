export type ChipProps = {
  name: string;
  shelved?: boolean;
};

export function Chip({ name, shelved = false }: ChipProps) {
  return (
    <span
      style={{ borderWidth: '1px' }}
      className="inline-flex items-center p-[--space-step] rounded-[--radius-tile] border-solid border-[--color-edge] bg-[--color-surface]"
    >
      <span className={`type-label ${shelved ? 'text-[--color-ink-muted]' : 'text-[--color-ink]'}`}>
        {name}
      </span>
    </span>
  );
}
