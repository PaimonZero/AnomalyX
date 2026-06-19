import { useEffect, useMemo, useState, type PropsWithChildren } from "react";

import { AuthTokenContext } from "@/app/providers/auth-token-context";

const storageKeys = {
  customToken: "anomalyx.auth.customToken",
} as const;

function readStorage(key: string) {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(key);
}

export function AuthTokenProvider({ children }: PropsWithChildren) {
  const [customToken, setCustomToken] = useState(() => readStorage(storageKeys.customToken) ?? "");

  useEffect(() => {
    window.localStorage.setItem(storageKeys.customToken, customToken);
  }, [customToken]);

  const value = useMemo(
    () => ({
      token: customToken,
      customToken,
      setCustomToken,
    }),
    [customToken],
  );

  return <AuthTokenContext.Provider value={value}>{children}</AuthTokenContext.Provider>;
}
