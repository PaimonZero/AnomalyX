import { createContext, useContext } from "react";

export interface AuthTokenContextValue {
  token: string;
  customToken: string;
  setCustomToken: (token: string) => void;
}

export const AuthTokenContext = createContext<AuthTokenContextValue | null>(null);

export function useAuthToken() {
  const context = useContext(AuthTokenContext);
  if (!context) throw new Error("useAuthToken must be used inside AuthTokenProvider");
  return context;
}
