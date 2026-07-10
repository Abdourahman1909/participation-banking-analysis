/** Turkish UI vocabulary — one place, used by every view (Turkish-first). */

export const CAMPAIGN_TYPE_LABELS: Record<string, string> = {
  funding: "Katılım Fonu",
  personal_financing: "Bireysel Finansman",
  housing_finance: "Konut Finansmanı",
  vehicle_financing: "Taşıt Finansmanı",
  card: "Kart",
  shopping_points: "Alışveriş Puanı",
  new_customer: "Yeni Müşteri",
  investment_product: "Yatırım Ürünü",
  other: "Diğer",
};

export const typeLabel = (t: string) => CAMPAIGN_TYPE_LABELS[t] ?? t;

export const STEP_LABELS: Record<string, string> = {
  collection: "Toplama",
  extraction: "Çıkarım",
  validation: "Doğrulama",
};

export function formatDate(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("tr-TR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    timeZone: "Europe/Istanbul",
  });
}

export function formatTime(iso: string | null): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleTimeString("tr-TR", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZone: "Europe/Istanbul",
  });
}
