import clsx from "clsx";

interface Props {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  hover?: boolean;
}

export default function GlassCard({ children, className, glow, hover }: Props) {
  return (
    <div
      className={clsx(
        "glass rounded-2xl",
        hover && "glass-hover cursor-pointer",
        glow && "glow-border",
        className
      )}
    >
      {children}
    </div>
  );
}
