import { useEffect, useState } from "react";
import { LayoutPanelTop, MessageCircle, Activity } from "lucide-react";
import { BrandMark } from "./ui/primitives";
import { fetchStats } from "./lib/api";
import { formatDate } from "./lib/labels";
import type { Stats } from "./lib/types";
import PanelView from "./views/PanelView";
import ChatView from "./views/ChatView";
import MonitorView from "./views/MonitorView";

type View = "panel" | "chat" | "monitor";

const NAV: { id: View; label: string; icon: typeof Activity }[] = [
  { id: "panel", label: "Panel", icon: LayoutPanelTop },
  { id: "chat", label: "Sohbet", icon: MessageCircle },
  { id: "monitor", label: "Monitör", icon: Activity },
];

export default function App() {
  const [view, setView] = useState<View>("panel");
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    const load = () => fetchStats().then(setStats).catch(() => setStats(null));
    load();
    window.addEventListener("kiyasai:data-changed", load);
    return () => window.removeEventListener("kiyasai:data-changed", load);
  }, []);

  return (
    <div className="min-h-dvh">
      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex max-w-[1160px] flex-wrap items-center gap-x-6 gap-y-3 px-5 py-3.5">
          <div className="flex min-w-0 items-center gap-3">
            <BrandMark />
            <div className="min-w-0">
              <div className="text-[1.35rem] font-[650] leading-tight tracking-[-0.02em]">
                KıyasAI
              </div>
              <div className="hidden truncate text-xs text-ink-muted sm:block">
                Türkiye katılım bankalarının ürünlerini tek yerde karşılaştırın
              </div>
            </div>
          </div>

          <nav
            aria-label="Görünümler"
            className="order-3 flex w-full gap-1 rounded-(--radius-panel) sm:order-none sm:w-auto"
          >
            {NAV.map(({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => setView(id)}
                aria-current={view === id ? "page" : undefined}
                className={`pressable flex flex-1 cursor-pointer items-center justify-center gap-2 rounded-(--radius-input) px-3.5 py-2 text-sm font-semibold sm:flex-none ${
                  view === id
                    ? "bg-brand-tint text-brand-hover"
                    : "text-ink-muted [@media(hover:hover)]:hover:bg-surface-2 [@media(hover:hover)]:hover:text-ink"
                }`}
              >
                <Icon size={16} strokeWidth={2.2} aria-hidden />
                {label}
              </button>
            ))}
          </nav>

          <div className="num ml-auto hidden text-right text-xs leading-relaxed text-ink-muted md:block">
            {stats?.db_ok ? (
              <>
                <span className="font-semibold text-ink">{stats.banks}</span> banka
                {" · "}
                <span className="font-semibold text-ink">{stats.campaigns}</span>{" "}
                kampanya
                <br />
                Son toplama: {formatDate(stats.last_collection)} · çevrimdışı
              </>
            ) : (
              <>
                Veritabanı kapalı · örnek veri
                <br />
                <span className="opacity-70">docker compose up postgres</span>
              </>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-[1160px] px-5 py-6">
        {/* All three stay mounted: chat history and the live SSE stream
            survive view switches. The entrance animation restarts when a
            view's box is regenerated (hidden → visible). */}
        <div hidden={view !== "panel"} className="view-in">
          <PanelView />
        </div>
        <div hidden={view !== "chat"} className="view-in">
          <ChatView />
        </div>
        <div hidden={view !== "monitor"} className="view-in">
          <MonitorView />
        </div>
      </main>
    </div>
  );
}
