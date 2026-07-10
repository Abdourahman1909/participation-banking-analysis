import { useCallback, useEffect, useRef, useState } from "react";
import {
  AlertTriangle,
  ArrowDownToLine,
  CheckCircle2,
  Cpu,
  Database,
  Flag,
  Layers,
  Play,
  ShieldAlert,
  Terminal,
  XCircle,
} from "lucide-react";
import { Badge, Button } from "../ui/primitives";
import {
  fetchPipelineStatus,
  fetchRuns,
  startRun,
  subscribeRunEvents,
} from "../lib/api";
import { STEP_LABELS, formatDate, formatTime } from "../lib/labels";
import type { PipelineStatus, RunEvent, RunInfo, Step } from "../lib/types";

const STEPS: Step[] = ["collection", "extraction", "validation"];

export default function MonitorView() {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [runs, setRuns] = useState<RunInfo[]>([]);
  const [events, setEvents] = useState<RunEvent[]>([]);
  const [viewedRun, setViewedRun] = useState<number | null>(null);
  const [liveStep, setLiveStep] = useState<Step | null>(null);
  const closeRef = useRef<(() => void) | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  const refresh = useCallback(() => {
    fetchPipelineStatus().then(setStatus).catch(() => setStatus(null));
    fetchRuns().then(setRuns).catch(() => setRuns([]));
  }, []);

  const watch = useCallback((runId: number, live: Step | null) => {
    closeRef.current?.();
    setEvents([]);
    setViewedRun(runId);
    setLiveStep(live);
    closeRef.current = subscribeRunEvents(
      runId,
      (e) => setEvents((prev) => [...prev, e]),
      () => {
        setLiveStep(null);
        refresh();
      },
    );
  }, [refresh]);

  useEffect(() => {
    fetchPipelineStatus().then(setStatus).catch(() => setStatus(null));
    fetchRuns()
      .then((r) => {
        setRuns(r);
        if (r.length > 0) watch(r[0].id, null); // replay the latest run
      })
      .catch(() => setRuns([]));
    return () => closeRef.current?.();
  }, [watch]);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [events]);

  async function trigger(step: Step) {
    try {
      const { run_id } = await startRun(step);
      watch(run_id, step);
      refresh();
    } catch (e) {
      if ((e as Error).message === "busy") setLiveStep(step);
    }
  }

  return (
    <section aria-label="Boru hattı monitörü" className="space-y-4">
      {/* Funnel + health — plain stat rhythm, not KPI cards (PRODUCT.md). */}
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 rounded-(--radius-panel) border border-line bg-surface px-4 py-3">
        <div className="num flex items-center gap-2 text-sm">
          <FunnelStat n={status?.collected} label="toplandı" />
          <span className="text-line-strong">→</span>
          <FunnelStat n={status?.extracted} label="çıkarıldı" />
          <span className="text-line-strong">→</span>
          <FunnelStat n={status?.validated} label="doğrulandı" />
        </div>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          {status?.db_ok ? (
            <Badge tone="success" icon={<Database size={12} aria-hidden />}>
              veritabanı
            </Badge>
          ) : (
            <Badge tone="danger" icon={<Database size={12} aria-hidden />}>
              veritabanı kapalı
            </Badge>
          )}
          {status?.model_ok ? (
            <Badge tone="success" icon={<Cpu size={12} aria-hidden />}>
              model sunucusu
            </Badge>
          ) : (
            <Badge tone="warning" icon={<Cpu size={12} aria-hidden />}>
              model bekleniyor
            </Badge>
          )}
          <span className="num text-xs text-ink-muted">
            {status?.scraped_banks ?? "—"}/{status?.banks ?? "—"} banka ·{" "}
            son toplama {formatDate(status?.last_collection ?? null)}
          </span>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {STEPS.map((s, i) => (
          <Button
            key={s}
            variant={i === 0 ? "primary" : "secondary"}
            onClick={() => trigger(s)}
            disabled={liveStep !== null}
          >
            {liveStep === s ? (
              <span className="pulse-dot size-2 rounded-full bg-current" />
            ) : (
              <Play size={14} aria-hidden />
            )}
            {STEP_LABELS[s]}
            {liveStep === s && "…"}
          </Button>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-[2fr_1fr]">
        <div className="rounded-(--radius-table) border border-line">
          <div className="flex items-center gap-2.5 border-b border-line bg-surface px-4 py-2.5 text-sm font-semibold">
            {liveStep ? (
              <>
                <span className="pulse-dot size-2 rounded-full bg-brand" />
                Canlı akış — {STEP_LABELS[liveStep]}
              </>
            ) : (
              <>
                <Terminal size={14} aria-hidden className="text-ink-muted" />
                İşlem akışı{viewedRun !== null && ` — çalıştırma #${viewedRun}`}
              </>
            )}
          </div>
          <div
            ref={scrollRef}
            className="max-h-[52dvh] min-h-[16rem] overflow-y-auto px-4 py-3"
            aria-live="polite"
          >
            {events.length === 0 ? (
              <p className="py-8 text-center text-sm text-ink-muted">
                Henüz etkinlik yok. Bir adımı başlatın — toplama, çıkarım ve
                doğrulama buradan canlı izlenir.
              </p>
            ) : (
              <ol className="space-y-0.5">
                {events.map((e, i) => (
                  <TimelineItem
                    key={e.seq}
                    event={e}
                    delayMs={Math.min(i, 8) * 30}
                  />
                ))}
              </ol>
            )}
          </div>
        </div>

        <div className="self-start rounded-(--radius-table) border border-line">
          <div className="border-b border-line bg-surface px-4 py-2.5 text-sm font-semibold">
            Geçmiş çalıştırmalar
          </div>
          <ol className="max-h-[52dvh] overflow-y-auto">
            {runs.length === 0 && (
              <li className="px-4 py-6 text-center text-sm text-ink-muted">
                Kayıtlı çalıştırma yok.
              </li>
            )}
            {runs.map((r) => (
              <li key={r.id}>
                <button
                  onClick={() => watch(r.id, null)}
                  aria-current={viewedRun === r.id}
                  className={`flex w-full cursor-pointer items-center gap-3 border-b border-line px-4 py-2.5 text-left text-sm transition-colors duration-150 last:border-b-0 ${
                    viewedRun === r.id
                      ? "bg-brand-tint"
                      : "[@media(hover:hover)]:hover:bg-surface-2"
                  }`}
                >
                  <RunOutcomeIcon ok={r.ok} />
                  <span className="font-medium">{STEP_LABELS[r.step]}</span>
                  <span className="num ml-auto text-xs text-ink-muted">
                    #{r.id} · {formatTime(r.started_at)}
                  </span>
                </button>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}

function FunnelStat({ n, label }: { n: number | null | undefined; label: string }) {
  return (
    <span>
      <span className="font-semibold">{n ?? "—"}</span>{" "}
      <span className="text-ink-muted">{label}</span>
    </span>
  );
}

function RunOutcomeIcon({ ok }: { ok: boolean | null }) {
  if (ok === null)
    return <span className="pulse-dot size-2 shrink-0 rounded-full bg-brand" />;
  return ok ? (
    <CheckCircle2 size={15} aria-label="başarılı" className="shrink-0 text-success" />
  ) : (
    <XCircle size={15} aria-label="başarısız" className="shrink-0 text-danger" />
  );
}

/** Structured event → clean timeline line (the polished replacement for
 *  raw terminal logs, ADR 0021). Unknown/raw `log` lines render muted —
 *  kept, never hidden. */
function TimelineItem({ event: e, delayMs }: { event: RunEvent; delayMs: number }) {
  const s = (k: string) => (e[k] as string | undefined) ?? "";
  const n = (k: string) => (e[k] as number | undefined) ?? "";

  let icon = <Terminal size={14} aria-hidden className="text-line-strong" />;
  let body: React.ReactNode = (
    <span className="text-ink-muted">{s("line")}</span>
  );
  let emphasis = false;

  switch (e.type) {
    case "step_started":
      icon = <Play size={14} aria-hidden className="text-brand" />;
      body = <strong>{STEP_LABELS[s("step")] ?? s("step")} başladı</strong>;
      emphasis = true;
      break;
    case "page_fetched":
      icon = <ArrowDownToLine size={14} aria-hidden className="text-ink-muted" />;
      body = (
        <span className="text-ink-muted">
          Sayfa alındı{" "}
          <span className="break-all text-ink">{shortUrl(s("url"))}</span>{" "}
          <span className="num">({n("status")})</span>
        </span>
      );
      break;
    case "bank_done":
      icon = <CheckCircle2 size={14} aria-hidden className="text-success" />;
      body = (
        <span>
          <strong>{s("bank")}</strong> —{" "}
          <span className="num">
            {n("collected")}/{n("total")}
          </span>{" "}
          kampanya toplandı
        </span>
      );
      emphasis = true;
      break;
    case "bank_failed":
      icon = <AlertTriangle size={14} aria-hidden className="text-danger" />;
      body = (
        <span>
          <strong>{s("bank")}</strong>: {s("reason")}{" "}
          <span className="break-all text-ink-muted">{shortUrl(s("url"))}</span>
        </span>
      );
      emphasis = true;
      break;
    case "pending":
      icon = <Layers size={14} aria-hidden className="text-info" />;
      body = (
        <span>
          <span className="num font-semibold">{n("count")}</span> kayıt işlem
          bekliyor
        </span>
      );
      break;
    case "extract_failed":
      icon = <AlertTriangle size={14} aria-hidden className="text-warning-ink" />;
      body = (
        <span>
          Kayıt <span className="num">#{n("run")}</span> çıkarılamadı:{" "}
          {s("reason")}
        </span>
      );
      break;
    case "field_dropped":
      icon = <ShieldAlert size={14} aria-hidden className="text-warning-ink" />;
      body = (
        <span>
          Kanıt kapısı — kayıt <span className="num">#{n("run")}</span>:{" "}
          {s("detail")}
        </span>
      );
      break;
    case "field_invalid":
      icon = <ShieldAlert size={14} aria-hidden className="text-warning-ink" />;
      body = (
        <span>
          Alan <span className="num">#{n("field_id")}</span> geçersiz:{" "}
          {s("reason")}
        </span>
      );
      break;
    case "summary":
      icon = <Flag size={14} aria-hidden className="text-brand" />;
      body = <span>Özet: {s("detail")}</span>;
      emphasis = true;
      break;
    case "model_info":
      icon = <Cpu size={14} aria-hidden className="text-ink-muted" />;
      body = <span className="text-ink-muted">Model: {s("detail")}</span>;
      break;
    case "step_done": {
      const ok = e.ok === true;
      icon = ok ? (
        <CheckCircle2 size={14} aria-hidden className="text-success" />
      ) : (
        <XCircle size={14} aria-hidden className="text-danger" />
      );
      body = <strong>{ok ? "Tamamlandı" : "Başarısız"}</strong>;
      emphasis = true;
      break;
    }
  }

  return (
    <li
      className={`rise-in flex items-baseline gap-2.5 rounded-md px-1.5 py-1 text-sm leading-relaxed ${
        emphasis ? "" : "opacity-90"
      }`}
      style={{ animationDelay: `${delayMs}ms` }}
    >
      <span className="translate-y-0.5 self-start">{icon}</span>
      <span className="min-w-0 flex-1">{body}</span>
      {typeof e.at === "string" && (
        <time className="num shrink-0 text-xs text-ink-muted">
          {formatTime(e.at)}
        </time>
      )}
    </li>
  );
}

function shortUrl(url: string): string {
  if (!url) return "";
  try {
    const u = new URL(url);
    const path = u.pathname.length > 34 ? `${u.pathname.slice(0, 34)}…` : u.pathname;
    return u.hostname.replace(/^www\./, "") + path;
  } catch {
    return url;
  }
}
