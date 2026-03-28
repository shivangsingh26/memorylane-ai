import clsx from "clsx";

interface Props {
  children: React.ReactNode;
  className?: string;
  as?: keyof JSX.IntrinsicElements;
}

export default function GradientText({ children, className, as: Tag = "span" }: Props) {
  const Component = Tag as React.ElementType;
  return (
    <Component className={clsx("gradient-text font-bold", className)}>
      {children}
    </Component>
  );
}
