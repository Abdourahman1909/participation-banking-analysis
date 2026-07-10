/** Shared component vocabulary (DESIGN.md). Same shapes on every view:
 *  radius 8px inputs/chips, 10px panels, 12px table; hairline OR shadow,
 *  never both; semantic color always paired with icon or text. */

import type { ReactNode, ButtonHTMLAttributes, SelectHTMLAttributes } from "react";

export function BrandMark({ size = 26 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <rect
        x="7"
        y="7"
        width="18"
        height="18"
        rx="3.5"
        transform="rotate(45 16 16)"
        className="fill-brand"
      />
    </svg>
  );
}

export function Button({
  variant = "secondary",
  className = "",
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary";
}) {
  const base =
    "pressable inline-flex items-center gap-2 rounded-(--radius-input) px-3.5 py-2 text-sm font-semibold disabled:opacity-45 disabled:cursor-not-allowed cursor-pointer";
  const look =
    variant === "primary"
      ? "bg-brand text-white [@media(hover:hover)]:hover:bg-brand-hover"
      : "bg-surface text-ink border border-line [@media(hover:hover)]:hover:bg-surface-2";
  return <button className={`${base} ${look} ${className}`} {...props} />;
}

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={`pressable cursor-pointer rounded-(--radius-input) border border-line bg-surface px-3 py-2 text-sm font-medium text-ink outline-none focus-visible:border-line-strong focus-visible:ring-2 focus-visible:ring-brand-tint ${props.className ?? ""}`}
    />
  );
}

/** Neutral pill for campaign types (neutrality is a brand principle). */
export function Chip({ children }: { children: ReactNode }) {
  return (
    <span className="inline-block whitespace-nowrap rounded-full bg-surface-2 px-2.5 py-1 text-[0.7rem] font-semibold uppercase tracking-[0.02em] text-ink-muted">
      {children}
    </span>
  );
}

const BADGE_TONES = {
  info: "text-info border-info/30 bg-info/5",
  success: "text-success border-success/30 bg-success/5",
  warning: "text-warning-ink border-warning/40 bg-warning/10",
  danger: "text-danger border-danger/30 bg-danger/5",
} as const;

/** Always icon + text — color is never the only signal (PRODUCT.md). */
export function Badge({
  tone,
  icon,
  children,
}: {
  tone: keyof typeof BADGE_TONES;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-semibold ${BADGE_TONES[tone]}`}
    >
      {icon}
      {children}
    </span>
  );
}

/** Inline teaching note for preview/empty states — never a blank panel. */
export function Note({
  badge,
  title,
  children,
}: {
  badge: ReactNode;
  title: string;
  children: ReactNode;
}) {
  return (
    <div className="rounded-(--radius-panel) border border-line bg-surface px-4 py-3.5">
      <div className="flex flex-wrap items-center gap-2.5">
        {badge}
        <span className="text-sm font-semibold">{title}</span>
      </div>
      <p className="mt-1.5 max-w-[72ch] text-sm leading-relaxed text-ink-muted">
        {children}
      </p>
    </div>
  );
}
