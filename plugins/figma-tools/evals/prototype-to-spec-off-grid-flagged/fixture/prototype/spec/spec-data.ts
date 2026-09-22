import type { PrototypeSpec } from './types.ts';

export const spec: PrototypeSpec = {
  name: 'Plate chip',

  useCases: [
    {
      id: 'uc1',
      title: 'Read a plate name off the board',
      steps: [
        {
          id: 'uc1-s1',
          title: 'A plate chip on the board',
          codeRef: 'components/chip.tsx',
          annotations: [
            {
              text: 'The chip is a bordered box on the raised surface, with the plate name inside it. The border is the board hairline; the corner is the tile radius.',
              component: 'chip',
            },
            {
              text: 'The box carries the same padding on all four sides. It was set by eye in the prototype and is written in the component inline style.',
              component: 'chip',
            },
          ],
          screenshot: null,
        },
      ],
    },
  ],

  components: {
    new: [
      {
        name: 'Chip',
        codeRef: 'components/chip.tsx',
        states: [
          {
            name: 'plain',
            description: 'One chip carrying a plate name. The only state there is.',
            page: 'spec/component-states/chip/plain/page.tsx',
            preview: null,
          },
        ],
      },
    ],
  },

  businessLogic: [
    {
      id: 'bl1',
      rule: 'The chip is inert: it takes no press, no hover and no focus ring.',
      observedIn: ['uc1-s1'],
    },
    {
      id: 'bl2',
      rule: 'A shelved plate sets the name in the muted ink; every other plate sets it in the default ink. Nothing else about the chip changes.',
      observedIn: ['uc1-s1'],
    },
  ],

  implementationNotes: {
    tokens: [
      { prototype: '--color-surface', role: 'the chip box fill' },
      { prototype: '--color-edge', role: 'the chip border' },
      { prototype: '--color-ink', role: 'the plate name' },
      { prototype: '--color-ink-muted', role: 'the plate name, shelved' },
      { prototype: '--radius-tile', role: 'the chip corner' },
      { prototype: '--space-hairline', role: 'the chip border width' },
      {
        prototype: 'the inline padding in components/chip.tsx',
        role: 'the space between the chip border and the plate name — a raw value, written in the inline style and backed by no token',
      },
    ],
  },
};
