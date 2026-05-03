import { Loader2, Play } from "lucide-react";

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
import { useAdminRuns, useTriggerRun } from "@/lib/queries";
import { formatDate } from "@/lib/utils";

const STATUS_VARIANT: Record<string, "success" | "warning" | "destructive" | "secondary"> = {
  success: "success",
  partial: "warning",
  failed: "destructive",
  running: "secondary",
};

export function CollectionRunsPage() {
  const { data, isLoading } = useAdminRuns();
  const trigger = useTriggerRun();

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Collection Runs</h1>
          <p className="text-sm text-muted-foreground">
            수집 로그 (5초마다 갱신). 동기 실행 — 완료 후 응답까지 시간 걸릴 수 있음.
          </p>
        </div>
        <Button onClick={() => trigger.mutate()} disabled={trigger.isPending}>
          {trigger.isPending ? (
            <Loader2 className="mr-1 h-4 w-4 animate-spin" />
          ) : (
            <Play className="mr-1 h-4 w-4" />
          )}
          수동 수집 실행
        </Button>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Source</TableHead>
              <TableHead>시작</TableHead>
              <TableHead>종료</TableHead>
              <TableHead>상태</TableHead>
              <TableHead>건수</TableHead>
              <TableHead>소요(ms)</TableHead>
              <TableHead>에러</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((run) => (
              <TableRow key={run.id}>
                <TableCell className="font-medium">{run.source?.name ?? "—"}</TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {formatDate(run.started_at)}
                </TableCell>
                <TableCell className="text-xs text-muted-foreground">
                  {run.finished_at ? formatDate(run.finished_at) : "..."}
                </TableCell>
                <TableCell>
                  <Badge variant={STATUS_VARIANT[run.status] ?? "secondary"}>
                    {run.status}
                  </Badge>
                </TableCell>
                <TableCell>{run.items_collected}</TableCell>
                <TableCell>{run.duration_ms ?? "—"}</TableCell>
                <TableCell className="max-w-md truncate text-xs text-destructive">
                  {run.error_message}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
