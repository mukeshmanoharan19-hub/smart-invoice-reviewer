type Props = {
  children: React.ReactNode
  className?: string
}

export function Panel({ children, className = '' }: Props) {
  return (
    <section className={`rounded-xl border border-slate-200 bg-white p-5 shadow-sm ${className}`}>
      {children}
    </section>
  )
}
