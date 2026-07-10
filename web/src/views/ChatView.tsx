import { useEffect, useRef, useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Diamond, SendHorizonal } from "lucide-react";
import { Badge, BrandMark, Note } from "../ui/primitives";
import { sendChat } from "../lib/api";
import type { Source } from "../lib/types";

interface Message {
  role: "user" | "assistant";
  answer: string;
  sources: Source[];
  isPreview?: boolean;
}

const SUGGESTIONS = [
  "En uygun konut finansmanı hangi bankada?",
  "Taşıt finansmanında en düşük kâr payı kimde?",
  "Hangi bankalarda yeni müşteri kampanyası var?",
];

/** The agent answers with light markdown bold; render just that — no
 *  markdown dependency for two asterisks. */
function renderAnswer(text: string): ReactNode[] {
  return text.split(/\*\*(.+?)\*\*/g).map((part, i) =>
    i % 2 === 1 ? <strong key={i}>{part}</strong> : part,
  );
}

export default function ChatView() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, busy]);

  async function ask(question: string) {
    const q = question.trim();
    if (!q || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", answer: q, sources: [] }]);
    setBusy(true);
    try {
      const res = await sendChat(q);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          answer: res.answer,
          sources: res.sources,
          isPreview: res.is_preview,
        },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          answer:
            "Şu anda yanıt veremiyorum — sunucuya ulaşılamadı. Lütfen tekrar deneyin.",
          sources: [],
        },
      ]);
    } finally {
      setBusy(false);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    ask(input);
  }

  return (
    <section
      aria-label="Sohbet"
      className="mx-auto flex min-h-[62dvh] max-w-[760px] flex-col"
    >
      <div className="flex-1 space-y-4">
        {messages.length === 0 && (
          <div className="space-y-4">
            <Note
              badge={
                <Badge tone="info" icon={<Diamond size={12} aria-hidden />}>
                  Sohbet
                </Badge>
              }
              title="Kampanyaları doğal dille sorun"
            >
              Her yanıtın altında <strong>Kaynaklar</strong> bölümü bulunur:
              cevaptaki her sayı, bankanın kendi kampanya metnindeki kanıt
              cümlesine dayanır. Veri veya model henüz hazır değilse yanıtlar
              örnek verilerle işaretli olarak gelir.
            </Note>
            <div className="flex flex-wrap gap-2">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={s}
                  onClick={() => ask(s)}
                  className="pressable rise-in cursor-pointer rounded-full border border-line bg-surface px-3.5 py-2 text-sm text-ink [@media(hover:hover)]:hover:border-line-strong [@media(hover:hover)]:hover:bg-surface-2"
                  style={{ animationDelay: `${i * 50}ms` }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} message={m} />
        ))}

        {busy && (
          <div className="rise-in flex items-center gap-2.5">
            <BrandMark size={20} />
            <span className="flex gap-1 rounded-(--radius-panel) bg-surface px-3.5 py-3">
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  className="think-dot size-1.5 rounded-full bg-ink-muted"
                />
              ))}
            </span>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={onSubmit} className="sticky bottom-4 mt-6 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Bir soru sorun…"
          aria-label="Sorunuz"
          className="w-full rounded-(--radius-panel) border border-line bg-bg px-4 py-3 text-sm text-ink shadow-[0_2px_8px_oklch(0.21_0.018_195/0.05)] outline-none transition-colors duration-150 placeholder:text-ink-muted focus-visible:border-line-strong focus-visible:ring-2 focus-visible:ring-brand-tint"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          aria-label="Gönder"
          className="pressable cursor-pointer rounded-(--radius-panel) bg-brand px-4 text-white disabled:cursor-not-allowed disabled:opacity-45 [@media(hover:hover)]:hover:bg-brand-hover"
        >
          <SendHorizonal size={18} aria-hidden />
        </button>
      </form>
    </section>
  );
}

function MessageBubble({ message: m }: { message: Message }) {
  if (m.role === "user") {
    return (
      <div className="rise-in flex justify-end">
        <div className="max-w-[52ch] rounded-(--radius-panel) rounded-br-[4px] bg-brand-tint px-4 py-2.5 text-sm leading-relaxed">
          {m.answer}
        </div>
      </div>
    );
  }
  return (
    <div className="rise-in flex items-start gap-2.5">
      <div className="mt-2 shrink-0">
        <BrandMark size={20} />
      </div>
      <div className="max-w-[62ch] space-y-3 rounded-(--radius-panel) rounded-bl-[4px] bg-surface px-4 py-3">
        {m.isPreview && (
          <Badge tone="info" icon={<Diamond size={12} aria-hidden />}>
            önizleme — örnek veriler
          </Badge>
        )}
        <p className="text-sm leading-relaxed">{renderAnswer(m.answer)}</p>
        {m.sources.length > 0 && (
          <div className="border-t border-line pt-2.5">
            <div className="mb-1.5 text-[0.7rem] font-semibold uppercase tracking-[0.02em] text-ink-muted">
              Kaynaklar
            </div>
            <ul className="space-y-2">
              {m.sources.map((s, i) => (
                <li key={i} className="text-xs leading-relaxed text-ink-muted">
                  <span className="font-semibold text-ink">{s.bank}</span>
                  {s.title && <> — {s.title}</>}
                  {s.evidence_quote && (
                    <em className="block">&ldquo;{s.evidence_quote}&rdquo;</em>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
