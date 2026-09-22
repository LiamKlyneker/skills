// The prototype's chip, as the designers drew it. Not built on the design system:
// the border, the corner and the type tier are hand-written here.
export type ChipProps = {
  name: string;
  shelved?: boolean;
};

export function Chip({ name, shelved = false }: ChipProps) {
  return (
    <span
      style={{ padding: '10px' }}
      className="inline-flex items-center rounded-[--radius-tile] border-solid border-[length:--space-hairline] border-[--color-edge] bg-[--color-surface]"
    >
      <span className={`type-label ${shelved ? 'text-[--color-ink-muted]' : 'text-[--color-ink]'}`}>
        {name}
      </span>
    </span>
  );
}
