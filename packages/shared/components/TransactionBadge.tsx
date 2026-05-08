type Status = 'succeeded' | 'failed' | 'pending' | 'processing' | 'refunded';

const config: Record<Status, { label: string; class: string }> = {
  succeeded:  { label: 'Succès',      class: 'bg-[#001a10] text-[#009e60] border-[#003b24]' },
  failed:     { label: 'Échoué',      class: 'bg-[#1a0505] text-[#fa5252] border-[#3b1010]' },
  pending:    { label: 'En attente',  class: 'bg-[#050f1a] text-[#339af0] border-[#0e2d4a]' },
  processing: { label: 'En cours',   class: 'bg-[#1a0a00] text-[#fd7e14] border-[#3b1f00]' },
  refunded:   { label: 'Remboursé',  class: 'bg-[#0a0a1a] text-[#868e96] border-[#2a2d31]' },
};

export function TransactionBadge({ status }: { status: Status }) {
  const { label, class: cls } = config[status];
  return (
    <span className={`
      inline-flex items-center gap-1.5 px-2 py-0.5
      text-[11px] font-medium tracking-wide uppercase
      border rounded-[4px] font-mono
      ${cls}
    `}>
      <span className="w-1.5 h-1.5 rounded-full bg-current opacity-80" />
      {label}
    </span>
  );
}