import { Button } from "@/components/ui/button";
import type { Industry } from "@/types/api";

interface Props {
  industries: Industry[];
  value?: string;
  onChange: (slug: string | undefined) => void;
}

export function IndustryFilter({ industries, value, onChange }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2">
      <Button
        variant={!value ? "default" : "outline"}
        size="sm"
        onClick={() => onChange(undefined)}
      >
        전체
      </Button>
      {industries.map((ind) => (
        <Button
          key={ind.slug}
          variant={value === ind.slug ? "default" : "outline"}
          size="sm"
          onClick={() => onChange(ind.slug)}
        >
          {ind.name}
        </Button>
      ))}
    </div>
  );
}
