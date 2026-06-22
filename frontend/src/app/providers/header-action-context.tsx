import { createContext, useContext, type ReactNode } from "react";

export interface HeaderActionContextValue {
  setHeaderAction: (action: ReactNode) => void;
}

export const HeaderActionContext = createContext<HeaderActionContextValue | null>(null);

export function useHeaderAction() {
  const context = useContext(HeaderActionContext);
  if (!context) throw new Error("useHeaderAction must be used inside HeaderActionContext.Provider");
  return context;
}
