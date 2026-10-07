import { Heading } from '@atelier/ds';

export function BoardHeading({ title }: { title: string }) {
  return <Heading level={2}>{title}</Heading>;
}
