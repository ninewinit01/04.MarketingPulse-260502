import { ChevronLeft, ChevronRight } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Props {
  date: string;
  onChange: (date: string) => void;
}

function shift(date: string, days: number): string {
  const d = new Date(date);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export function DateNavigator({ date, onChange }: Props) {
  return (
    <div className="flex items-center gap-2">
      <Button variant="outline" size="icon" onClick={() => onChange(shift(date, -1))}>
        <ChevronLeft className="h-4 w-4" />
      </Button>
      <Input
        type="date"
        value={date}
        onChange={(e) => onChange(e.target.value)}
        className="w-[170px]"
      />
      <Button variant="outline" size="icon" onClick={() => onChange(shift(date, 1))}>
        <ChevronRight className="h-4 w-4" />
      </Button>
    </div>
  );
}
