import { useMemo, useState } from "react";
import { Plus, X } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  useAdminIndustries,
  useAdminKeywords,
  useCreateKeyword,
  useDeleteKeyword,
  useUpdateKeyword,
} from "@/lib/queries";
import type { Industry, Keyword } from "@/types/api";

export function KeywordsPage() {
  const { data: industries } = useAdminIndustries();
  const { data: keywords, isLoading } = useAdminKeywords();

  const grouped = useMemo(() => {
    const map = new Map<number, Keyword[]>();
    (keywords ?? []).forEach((kw) => {
      const list = map.get(kw.industry) ?? [];
      list.push(kw);
      map.set(kw.industry, list);
    });
    return map;
  }, [keywords]);

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Keywords</h1>
        <p className="text-sm text-muted-foreground">
          업종별 시드 키워드. <b>칩 클릭</b>: 활성 토글 · <b>가중치 클릭</b>: 수정 ·{" "}
          <b>X</b>: 삭제
        </p>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {industries?.map((ind) => (
            <IndustryKeywordCard
              key={ind.id}
              industry={ind}
              keywords={grouped.get(ind.id) ?? []}
            />
          ))}
        </div>
      )}
    </div>
  );
}

interface CardProps {
  industry: Industry;
  keywords: Keyword[];
}

function IndustryKeywordCard({ industry, keywords }: CardProps) {
  const [adding, setAdding] = useState(false);
  const [term, setTerm] = useState("");
  const [weightInput, setWeightInput] = useState("1");
  const create = useCreateKeyword();
  const update = useUpdateKeyword();
  const remove = useDeleteKeyword();

  async function submit() {
    const trimmed = term.trim();
    if (!trimmed) return;
    const w = Number(weightInput) || 1;
    await create.mutateAsync({
      industry: industry.id,
      term: trimmed,
      weight: w,
      is_active: true,
    });
    setTerm("");
    setWeightInput("1");
    setAdding(false);
  }

  function editWeight(kw: Keyword) {
    const next = window.prompt(`"${kw.term}" 가중치 (현재 ${kw.weight})`, String(kw.weight));
    if (next === null) return;
    const num = Number(next);
    if (Number.isNaN(num) || num <= 0) {
      alert("0보다 큰 숫자를 입력하세요.");
      return;
    }
    update.mutate({ id: kw.id, weight: num });
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
        <CardTitle className="text-base">
          {industry.name}
          <span className="ml-2 text-xs font-normal text-muted-foreground">
            ({keywords.length})
          </span>
        </CardTitle>
        <Button size="sm" variant="outline" onClick={() => setAdding((v) => !v)}>
          <Plus className="h-3 w-3" />
        </Button>
      </CardHeader>
      <CardContent>
        {keywords.length === 0 ? (
          <p className="text-xs text-muted-foreground">키워드 없음</p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <Badge
                key={kw.id}
                variant={kw.is_active ? "default" : "secondary"}
                className={`flex items-center gap-1 pr-1 ${
                  !kw.is_active ? "opacity-50 line-through" : ""
                }`}
              >
                <span
                  role="button"
                  onClick={() => update.mutate({ id: kw.id, is_active: !kw.is_active })}
                  title={kw.is_active ? "클릭: 비활성화" : "클릭: 활성화"}
                  className="cursor-pointer"
                >
                  {kw.term}
                </span>
                <span
                  role="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    editWeight(kw);
                  }}
                  title="가중치 수정"
                  className="cursor-pointer rounded-sm bg-black/15 px-1 text-[10px] font-mono leading-tight hover:bg-black/30"
                >
                  ×{kw.weight}
                </span>
                <span
                  role="button"
                  aria-label="삭제"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (confirm(`"${kw.term}" 삭제할까요?`)) remove.mutate(kw.id);
                  }}
                  className="cursor-pointer rounded-full p-0.5 opacity-60 hover:bg-black/20 hover:opacity-100"
                >
                  <X className="h-3 w-3" />
                </span>
              </Badge>
            ))}
          </div>
        )}

        {adding ? (
          <div className="mt-3 flex gap-2">
            <Input
              autoFocus
              value={term}
              onChange={(e) => setTerm(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submit();
                if (e.key === "Escape") {
                  setAdding(false);
                  setTerm("");
                }
              }}
              placeholder="새 키워드"
              className="h-8 flex-1"
            />
            <Input
              type="number"
              step="0.1"
              min="0"
              value={weightInput}
              onChange={(e) => setWeightInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") submit();
              }}
              title="가중치"
              className="h-8 w-16"
            />
            <Button size="sm" onClick={submit} disabled={create.isPending || !term.trim()}>
              추가
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => {
                setAdding(false);
                setTerm("");
                setWeightInput("1");
              }}
            >
              취소
            </Button>
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
