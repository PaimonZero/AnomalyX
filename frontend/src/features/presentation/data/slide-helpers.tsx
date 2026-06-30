import type { ElementType, ReactNode } from "react";

export function bilingual(vi: ReactNode, en: ReactNode) {
  return { vi, en } as const;
}

export function IconBullet({ icon: Icon, text }: { icon: ElementType; text: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
      <Icon size={20} style={{ color: "var(--accent-primary)", flexShrink: 0 }} />
      <span>{text}</span>
    </div>
  );
}

export function Tag({ children }: { children: ReactNode }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "3px 10px",
        borderRadius: 6,
        background: "var(--accent-primary-muted)",
        color: "var(--accent-primary)",
        fontSize: "0.8rem",
        fontWeight: 600,
      }}
    >
      {children}
    </span>
  );
}
