import { useEffect } from "react";

export function useHotkey(key: string, handler: () => void) {
  useEffect(() => {
    const listener = (event: KeyboardEvent) => {
      const typing = event.target instanceof HTMLInputElement;
      if (!typing && event.key.toLowerCase() === key) handler();
    };
    window.addEventListener("keydown", listener);
    return () => window.removeEventListener("keydown", listener);
  }, [key, handler]);
}
