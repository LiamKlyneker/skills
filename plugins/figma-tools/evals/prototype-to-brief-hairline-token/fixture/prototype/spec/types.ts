/**
 * The shape `spec-data.ts` is declared in. A reader that knows these types knows what an
 * Atelier prototype spec can say; nothing outside this file adds a field.
 */

export type StepId = string;

/** A designer note pinned to a step. `component` tags the element it is about. */
export interface Annotation {
  text: string;
  component?: string;
}

export interface Step {
  id: StepId;
  title: string;
  /** Path, relative to the prototype folder, of the file that renders the step. */
  codeRef: string;
  annotations: Annotation[];
  /** Path of the captured PNG, or `null` where the step was never captured. */
  screenshot: string | null;
}

export interface UseCase {
  id: string;
  title: string;
  steps: Step[];
}

export interface ComponentState {
  name: string;
  description: string;
  /** The page that renders the component with this state's props. */
  page: string;
  /** Path of the captured PNG for this state, or `null` where none was captured. */
  preview: string | null;
}

export interface NewComponent {
  name: string;
  codeRef: string;
  states: ComponentState[];
}

export interface BusinessRule {
  id: string;
  rule: string;
  observedIn: StepId[];
}

export interface TokenNote {
  /** What the prototype writes. A raw value here has no semantic equivalent. */
  prototype: string;
  role: string;
}

export interface PrototypeSpec {
  name: string;
  useCases: UseCase[];
  components: { new: NewComponent[] };
  businessLogic: BusinessRule[];
  implementationNotes: { tokens: TokenNote[] };
}
