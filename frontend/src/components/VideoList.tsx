import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { formatDate } from "@/lib/utils";
import type { ContentItem } from "@/types/api";

interface Props {
  items: ContentItem[];
  emptyText?: string;
  showChannel?: boolean;
}

export function VideoList({ items, emptyText = "영상 없음", showChannel = true }: Props) {
  if (items.length === 0) {
    return <p className="py-2 text-sm text-muted-foreground">{emptyText}</p>;
  }
  return (
    <ul className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {items.map((item) => {
        const channel =
          typeof item.metadata?.channel === "string" ? item.metadata.channel : null;
        return (
          <li key={item.id} className="group">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="block overflow-hidden rounded-md border bg-card transition-shadow hover:shadow-md"
            >
              {item.thumbnail_url ? (
                <img
                  src={item.thumbnail_url}
                  alt=""
                  className="aspect-video w-full object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="flex aspect-video items-center justify-center bg-muted text-xs text-muted-foreground">
                  No thumbnail
                </div>
              )}
              <div className="space-y-1 p-3">
                <p className="line-clamp-2 text-sm font-medium group-hover:text-primary">
                  {item.title}
                </p>
                <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-muted-foreground">
                  {showChannel && channel ? <span className="truncate">{channel}</span> : null}
                  {item.published_at ? <span>· {formatDate(item.published_at)}</span> : null}
                  {item.industries.map((ind) => (
                    <Badge key={ind.id} variant="secondary" className="text-[10px]">
                      {ind.name}
                    </Badge>
                  ))}
                  <ExternalLink className="ml-auto h-3 w-3 opacity-0 group-hover:opacity-60" />
                </div>
              </div>
            </a>
          </li>
        );
      })}
    </ul>
  );
}
