import { useEffect, useMemo, useState } from "react";
import { ChevronDown, Diamond, CheckCircle2, XCircle } from "lucide-react";
import { Badge, Chip, Note, Select } from "../ui/primitives";
import { fetchCampaigns } from "../lib/api";
import { typeLabel } from "../lib/labels";
import type { CampaignItem } from "../lib/types";

type SortKey = "recommended" | "rate_asc" | "rate_desc" | "term_asc" | "bank_az";

const SORTS: { id: SortKey; label: string }[] = [
  { id: "recommended", label: "Önerilen" },
  { id: "rate_asc", label: "Kâr payı (artan)" },
  { id: "rate_desc", label: "Kâr payı (azalan)" },
  { id: "term_asc", label: "Vade (artan)" },
  { id: "bank_az", label: "Banka (A–Z)" },
];

const BIG = Number.POSITIVE_INFINITY;

function sortItems(items: CampaignItem[], sort: SortKey): CampaignItem[] {
  const rows = [...items];
  const rate = (r: CampaignItem) => r.rate_normalized ?? BIG;
  switch (sort) {
    case "rate_asc":
      return rows.sort((a, b) => rate(a) - rate(b));
    case "rate_desc":
      return rows.sort(
        (a, b) => (b.rate_normalized ?? -1) - (a.rate_normalized ?? -1),
      );
    case "term_asc":
      return rows.sort((a, b) => (a.term_months ?? BIG) - (b.term_months ?? BIG));
    case "bank_az":
      return rows.sort((a, b) => a.bank.localeCompare(b.bank, "tr"));
    default:
      return rows.sort(
        (a, b) =>
          typeLabel(a.campaign_type).localeCompare(typeLabel(b.campaign_type), "tr") ||
          rate(a) - rate(b),
      );
  }
}

const Null = () => <span className="text-ink-muted">—</span>;

export default function PanelView() {
  const [items, setItems] = useState<CampaignItem[]>([]);
  const [isSample, setIsSample] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [type, setType] = useState("all");
  const [sort, setSort] = useState<SortKey>("recommended");
  const [openRow, setOpenRow] = useState<number | null>(null);

  useEffect(() => {
    const load = () =>
      fetchCampaigns()
        .then((r) => {
          setItems(r.items);
          setIsSample(r.is_sample);
        })
        .finally(() => setLoaded(true));
    load();
    // Refetch when a pipeline run finishes (Monitör dispatches this) so the
    // Panel flips from sample to real data without a page reload.
    window.addEventListener("kiyasai:data-changed", load);
    return () => window.removeEventListener("kiyasai:data-changed", load);
  }, []);

  const types = useMemo(
    () =>
      [...new Set(items.map((i) => i.campaign_type))].sort((a, b) =>
        typeLabel(a).localeCompare(typeLabel(b), "tr"),
      ),
    [items],
  );

  const singleType = type !== "all";
  const rows = useMemo(() => {
    const filtered = singleType
      ? items.filter((i) => i.campaign_type === type)
      : items;
    return sortItems(filtered, sort);
  }, [items, type, sort, singleType]);

  // Best value only within one product type — cross-type rate comparison
  // would be misleading (PRODUCT.md principle 3).
  const bestRate = useMemo(() => {
    if (!singleType) return null;
    const rates = rows
      .map((r) => r.rate_normalized)
      .filter((r): r is number => r !== null);
    return rates.length ? Math.min(...rates) : null;
  }, [rows, singleType]);

  return (
    <section aria-label="Karşılaştırma paneli" className="space-y-4">
      {loaded && isSample && (
        <Note
          badge={
            <Badge tone="info" icon={<Diamond size={12} aria-hidden />}>
              Önizleme — örnek veriler
            </Badge>
          }
          title="Çıkarım katmanı henüz çalışmadı"
        >
          Aşağıdaki ürün alanları (kâr payı, vade, tutar) örnek verilerdir.
          Gerçek değerler, yerel LLM ham kampanya metnini işleyince otomatik
          olarak veritabanından gelecek — kod değişmeden. Banka listesi ve
          toplama sayıları gerçektir.
        </Note>
      )}

      <div className="flex flex-wrap items-end gap-3">
        <label className="flex flex-col gap-1 text-xs font-semibold text-ink-muted">
          Ürün tipi
          <Select value={type} onChange={(e) => setType(e.target.value)}>
            <option value="all">Tümü</option>
            {types.map((t) => (
              <option key={t} value={t}>
                {typeLabel(t)}
              </option>
            ))}
          </Select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-semibold text-ink-muted">
          Sırala
          <Select
            value={sort}
            onChange={(e) => setSort(e.target.value as SortKey)}
          >
            {SORTS.map((s) => (
              <option key={s.id} value={s.id}>
                {s.label}
              </option>
            ))}
          </Select>
        </label>
        <div className="num ml-auto pb-2 text-sm text-ink-muted">
          {rows.length} kampanya
          {singleType && bestRate !== null && " · en düşük kâr payı işaretli"}
        </div>
      </div>

      <div className="overflow-x-auto rounded-(--radius-table) border border-line">
        <table className="w-full min-w-[820px] border-collapse text-left text-sm">
          <thead>
            <tr className="sticky top-0 bg-surface text-[0.7rem] font-semibold uppercase tracking-[0.02em] text-ink-muted">
              <th className="px-4 py-3">Banka</th>
              <th className="px-4 py-3">Kampanya</th>
              <th className="px-4 py-3">Tür</th>
              <th className="px-4 py-3">Kâr Payı (aylık)</th>
              <th className="px-4 py-3">Vade</th>
              <th className="px-4 py-3">Tutar</th>
              <th className="px-4 py-3">Kaynak</th>
            </tr>
          </thead>
          <tbody>
            {!loaded && (
              <tr>
                <td colSpan={7} className="px-4 py-8">
                  {/* Skeleton rows, not a spinner (product register). */}
                  <div className="space-y-3" aria-label="Yükleniyor">
                    {[0, 1, 2].map((i) => (
                      <div
                        key={i}
                        className="h-4 animate-pulse rounded bg-surface-2"
                        style={{ width: `${88 - i * 14}%` }}
                      />
                    ))}
                  </div>
                </td>
              </tr>
            )}
            {loaded && rows.length === 0 && (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-ink-muted">
                  Bu ürün tipinde kampanya yok. Filtreyi &ldquo;Tümü&rdquo; yapıp
                  diğer tiplere bakabilirsiniz.
                </td>
              </tr>
            )}
            {rows.map((r, idx) => {
              const isBest =
                bestRate !== null && r.rate_normalized === bestRate;
              const isOpen = openRow === idx;
              return (
                <RowPair
                  key={`${r.bank}-${r.title}-${idx}`}
                  row={r}
                  isBest={isBest}
                  isOpen={isOpen}
                  onToggle={() => setOpenRow(isOpen ? null : idx)}
                />
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function RowPair({
  row: r,
  isBest,
  isOpen,
  onToggle,
}: {
  row: CampaignItem;
  isBest: boolean;
  isOpen: boolean;
  onToggle: () => void;
}) {
  const quote = r.evidence_quote;
  return (
    <>
      <tr
        onClick={onToggle}
        aria-expanded={isOpen}
        className={`cursor-pointer border-t border-line transition-colors duration-150 ${
          isBest ? "bg-brand-tint" : "[@media(hover:hover)]:hover:bg-surface-2"
        }`}
      >
        <td className="px-4 py-3 font-medium whitespace-nowrap">
          <span className="mr-2 inline-block size-1.5 rounded-full bg-brand align-middle" />
          {r.bank}
        </td>
        <td className="max-w-[26ch] truncate px-4 py-3" title={r.title}>
          {r.title}
        </td>
        <td className="px-4 py-3">
          <Chip>{typeLabel(r.campaign_type)}</Chip>
        </td>
        <td className="num px-4 py-3 font-semibold whitespace-nowrap">
          {r.profit_share_rate ?? <Null />}
          {isBest && (
            <span className="ml-2 rounded-full bg-brand px-2 py-0.5 text-[0.65rem] font-bold uppercase text-white">
              en düşük
            </span>
          )}
        </td>
        <td className="num px-4 py-3 whitespace-nowrap">
          {r.term_months !== null ? `${r.term_months} ay` : <Null />}
        </td>
        <td className="num px-4 py-3 whitespace-nowrap">
          {r.cost_amount ?? <Null />}
        </td>
        <td className="px-4 py-3 text-ink-muted">
          <span className="flex items-center gap-1.5">
            <span className="max-w-[22ch] truncate">
              {quote ? `❝ ${quote}` : "—"}
            </span>
            <ChevronDown
              size={14}
              aria-hidden
              className={`shrink-0 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`}
            />
          </span>
        </td>
      </tr>
      <tr aria-hidden={!isOpen} className={isBest ? "bg-brand-tint" : ""}>
        <td colSpan={7} className="p-0">
          {/* Evidence transparency is the product's soul (ADR 0016): the
              full verbatim quote, one click from the number it proves. */}
          <div className="expander" data-open={isOpen}>
            <div>
              <div className="expander-body flex flex-wrap items-start gap-3 border-t border-line/60 px-4 py-3">
                <blockquote className="max-w-[72ch] text-sm leading-relaxed text-ink">
                  <span className="mr-1 text-brand">❝</span>
                  {quote || "Bu kampanya için kanıt cümlesi yok."}
                  {quote && <span className="ml-1 text-brand">❞</span>}
                </blockquote>
                <span className="ml-auto">
                  {r.is_valid ? (
                    <Badge tone="success" icon={<CheckCircle2 size={12} aria-hidden />}>
                      doğrulandı
                    </Badge>
                  ) : (
                    <Badge tone="danger" icon={<XCircle size={12} aria-hidden />}>
                      geçersiz
                    </Badge>
                  )}
                </span>
              </div>
            </div>
          </div>
        </td>
      </tr>
    </>
  );
}
