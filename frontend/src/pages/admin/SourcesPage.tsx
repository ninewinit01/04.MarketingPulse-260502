import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useAdminSources, useUpdateSource } from "@/lib/queries";

const TYPE_LABEL: Record<string, string> = {
  news: "뉴스",
  video: "동영상",
  search_trend: "검색 트렌드",
  sns: "SNS",
};

export function SourcesPage() {
  const { data, isLoading } = useAdminSources();
  const update = useUpdateSource();

  return (
    <div>
      <div className="mb-4">
        <h1 className="text-2xl font-bold">Sources</h1>
        <p className="text-sm text-muted-foreground">
          데이터 소스 활성/비활성. 비활성 소스는 수집 시 건너뜁니다.
        </p>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>이름</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>유형</TableHead>
              <TableHead>활성</TableHead>
              <TableHead className="text-right">액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((src) => (
              <TableRow key={src.id}>
                <TableCell className="font-medium">{src.name}</TableCell>
                <TableCell className="font-mono text-xs">{src.slug}</TableCell>
                <TableCell>
                  <Badge variant="outline">{TYPE_LABEL[src.type] ?? src.type}</Badge>
                </TableCell>
                <TableCell>
                  {src.is_active ? (
                    <Badge variant="success">활성</Badge>
                  ) : (
                    <Badge variant="secondary">비활성</Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    variant={src.is_active ? "outline" : "default"}
                    onClick={() =>
                      update.mutate({ id: src.id, is_active: !src.is_active })
                    }
                  >
                    {src.is_active ? "비활성화" : "활성화"}
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
