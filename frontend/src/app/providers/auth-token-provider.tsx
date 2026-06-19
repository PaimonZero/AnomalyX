import { useEffect, useMemo, useState, type PropsWithChildren } from "react";

import { AuthTokenContext } from "@/app/providers/auth-token-context";
import { env } from "@/shared/config/env";

const storageKeys = {
  customToken: "anomalyx.auth.customToken",
  useEnvToken: "anomalyx.auth.useEnvToken",
} as const;

function readStorage(key: string) {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem(key);
}

export function AuthTokenProvider({ children }: PropsWithChildren) {
  const [customToken, setCustomToken] = useState(() => readStorage(storageKeys.customToken) ?? "");
  const [useEnvToken, setUseEnvToken] = useState(() => readStorage(storageKeys.useEnvToken) !== "false");

  useEffect(() => {
    window.localStorage.setItem(storageKeys.customToken, customToken);
  }, [customToken]);

  useEffect(() => {
    window.localStorage.setItem(storageKeys.useEnvToken, String(useEnvToken));
  }, [useEnvToken]);

  const value = useMemo(
    () => ({
      token: useEnvToken ? env.apiToken : customToken,
      customToken,
      useEnvToken,
      envTokenConfigured: Boolean(env.apiToken),
      setCustomToken,
      setUseEnvToken,
    }),
    [customToken, useEnvToken],
  );

  return <AuthTokenContext.Provider value={value}>{children}</AuthTokenContext.Provider>;
}
