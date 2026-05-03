import { Badge } from "@/components/ui/badge";
import type { TrendKeyword } from "@/types/api";

interface Props {
  trends: TrendKeyword[];
  emptyText?: string;
}

export function TrendList({ trends, emptyText = "트렌드 데이터 없음" }: Props) {
  if (trends.length === 0) {
    return <p className="py-2 text-sm text-muted-foreground">{emptyText}</p>;
  }
  return (
    <ol className="space-y-1.5">
      {trends.map((tk) => {
        const ratio = typeof tk.metadata?.ratio === "number" ? tk.metadata.ratio : null;
        const industryName =
          typeof tk.metadata?.industry_name === "string" ? tk.metadata.industry_name : null;
        return (
          <li key={tk.id} className="flex items-center gap-2 text-sm">
            <span className="w-6 text-right font-mono text-xs text-muted-foreground">
              {tk.rank}.
            </span>
            <a
              href={`https://search.naver.com/search.naver?query=${encodeURIComponent(tk.keyword)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="font-medium hover:underline"
            >
              {tk.keyword}
            </a>
            {industryName ? (
              <Badge variant="secondary" className="text-[10px]">
                {industryName}
              </Badge>
            ) : null}
            {ratio !== null ? (
              <span className="ml-auto font-mono text-xs text-muted-foreground">
                {ratio.toFixed(0)}
              </span>
            ) : null}
          </li>
        );
      })}
    </ol>
  );
}
