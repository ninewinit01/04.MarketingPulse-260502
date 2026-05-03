import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { ContentItem } from "@/types/api";

interface Props {
  items: ContentItem[];
  emptyText?: string;
}

export function ContentList({ items, emptyText = "수집된 콘텐츠가 없습니다." }: Props) {
  if (items.length === 0) {
    return <p className="py-4 text-sm text-muted-foreground">{emptyText}</p>;
  }
  return (
    <ul className="divide-y divide-border">
      {items.map((item) => (
        <li key={item.id} className="py-3">
          <div className="flex items-start gap-3">
            {item.thumbnail_url ? (
              <img
                src={item.thumbnail_url}
                alt=""
                className="h-16 w-24 flex-shrink-0 rounded object-cover"
                loading="lazy"
              />
            ) : null}
            <div className="min-w-0 flex-1">
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-center gap-1 text-sm font-medium hover:underline"
              >
                <span className="truncate">{item.title}</span>
                <ExternalLink className="h-3 w-3 flex-shrink-0 opacity-50 group-hover:opacity-100" />
              </a>
              <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                <span>{item.source.name}</span>
                {item.published_at ? <span>· {formatDate(item.published_at)}</span> : null}
                {item.industries.map((ind) => (
                  <Badge key={ind.id} variant="secondary" className="text-[10px]">
                    {ind.name}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </li>
      ))}
    </ul>
  );
}
