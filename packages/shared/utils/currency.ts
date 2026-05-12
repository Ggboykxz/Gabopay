export function formatXAF(amount: number): string {
  return new Intl.NumberFormat('fr-GA', {
    style: 'currency',
    currency: 'XAF',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatXAFCompact(amount: number): string {
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(1)}M XAF`;
  }
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(0)}K XAF`;
  }
  return `${amount} XAF`;
}
