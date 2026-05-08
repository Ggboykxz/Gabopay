export function formatXAF(amountInCentimes: number): string {
  const amount = Math.round(amountInCentimes / 100);
  return new Intl.NumberFormat('fr-GA', {
    style: 'currency',
    currency: 'XAF',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

export function formatXAFCompact(amountInCentimes: number): string {
  const amount = Math.round(amountInCentimes / 100);
  if (amount >= 1000000) {
    return `${(amount / 1000000).toFixed(1)}M FCA`;
  }
  if (amount >= 1000) {
    return `${(amount / 1000).toFixed(0)}K FCA`;
  }
  return `${amount} FCA`;
}