export type Session = { userId: string; teamId: string; role: "owner" | "editor" | "member" };

export function useSession(): Session | null {
  const raw = typeof window === "undefined" ? null : window.sessionStorage.getItem("session");
  return raw ? (JSON.parse(raw) as Session) : null;
}
