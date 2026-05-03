export interface Industry {
  id: number;
  name: string;
  slug: string;
  is_active: boolean;
  sort_order: number;
  keyword_count?: number;
  created_at?: string;
}

export interface Keyword {
  id: number;
  industry: number;
  industry_name?: string;
  term: string;
  weight: number;
  is_active: boolean;
}

export interface Source {
  id: number;
  name: string;
  slug: string;
  type: "news" | "video" | "search_trend" | "sns";
  is_active: boolean;
}

export interface ContentItem {
  id: number;
  source: Source;
  external_id: string;
  title: string;
  url: string;
  thumbnail_url: string | null;
  published_at: string | null;
  collected_at: string;
  metadata: Record<string, unknown>;
  industries: Pick<Industry, "id" | "name" | "slug">[];
  is_pinned: boolean;
  llm_summary: string | null;
}

export interface TrendKeyword {
  id: number;
  source: Source;
  keyword: string;
  url?: string;
  rank: number;
  observed_at: string;
  metadata: Record<string, unknown>;
  industries: Pick<Industry, "id" | "name" | "slug">[];
}

export interface CollectionRun {
  id: number;
  source: Source | null;
  started_at: string;
  finished_at: string | null;
  status: "success" | "partial" | "failed" | "running";
  error_message: string;
  items_collected: number;
  duration_ms: number | null;
}

export interface CuratedChannel {
  id: number;
  name: string;
  handle: string;
  description: string;
  is_active: boolean;
  created_at?: string;
}

export interface DashboardResponse {
  date: string;
  industry: string | null;
  news: ContentItem[];
  by_industry: Record<string, ContentItem[]>;
  trends: Record<string, TrendKeyword[]>;
  youtube_marketing: ContentItem[];
  youtube_curated: ContentItem[];
  industries: Industry[];
  totals: { items: number; trends: number };
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
