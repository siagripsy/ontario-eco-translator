import type { PropsWithChildren, ReactNode } from "react";

type SectionCardProps = PropsWithChildren<{
  eyebrow: string;
  title: string;
  description?: string;
  action?: ReactNode;
  className?: string;
}>;

export function SectionCard({
  eyebrow,
  title,
  description,
  action,
  className,
  children,
}: SectionCardProps) {
  return (
    <section className={`glass-panel p-6 md:p-7 ${className || ""}`}>
      <div className="mb-5 flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div className="space-y-2">
          <p className="section-title">{eyebrow}</p>
          <div className="space-y-1">
            <h2 className="text-2xl font-semibold text-ink">{title}</h2>
            {description ? <p className="max-w-2xl text-sm leading-6 text-slate">{description}</p> : null}
          </div>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}
