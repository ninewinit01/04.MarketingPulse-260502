import { useState } from "react";
import { ExternalLink, Pencil, Plus, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  useAdminChannels,
  useCreateChannel,
  useDeleteChannel,
  useUpdateChannel,
} from "@/lib/queries";
import type { CuratedChannel } from "@/types/api";

interface FormState {
  name: string;
  handle: string;
  description: string;
  is_active: boolean;
}
const empty: FormState = { name: "", handle: "", description: "", is_active: true };

export function ChannelsPage() {
  const { data, isLoading } = useAdminChannels();
  const create = useCreateChannel();
  const update = useUpdateChannel();
  const remove = useDeleteChannel();

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<CuratedChannel | null>(null);
  const [form, setForm] = useState<FormState>(empty);

  function openCreate() {
    setEditing(null);
    setForm(empty);
    setOpen(true);
  }
  function openEdit(ch: CuratedChannel) {
    setEditing(ch);
    setForm({
      name: ch.name,
      handle: ch.handle,
      description: ch.description,
      is_active: ch.is_active,
    });
    setOpen(true);
  }
  async function submit() {
    if (!form.handle.trim()) return;
    if (editing) await update.mutateAsync({ id: editing.id, ...form });
    else await create.mutateAsync(form);
    setOpen(false);
  }

  return (
    <div>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">YouTube 큐레이션 채널</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            "마케팅 채널 신규" 카드에 표시할 채널들. <br />
            <code className="rounded bg-muted px-1 text-xs">@핸들</code> (예:
            <code className="rounded bg-muted px-1 text-xs">@sebasi15</code>) 또는
            <code className="rounded bg-muted px-1 text-xs">UC...</code> channel ID 입력 가능.
          </p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="mr-1 h-4 w-4" /> 추가
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? "채널 수정" : "채널 추가"}</DialogTitle>
            </DialogHeader>
            <div className="grid gap-3">
              <div>
                <Label htmlFor="handle">핸들 / Channel ID</Label>
                <Input
                  id="handle"
                  value={form.handle}
                  onChange={(e) => setForm({ ...form, handle: e.target.value })}
                  placeholder="@sebasi15 또는 UCxxxxxxxx"
                />
                <p className="mt-1 text-xs text-muted-foreground">
                  youtube.com 채널 페이지의 주소창에서 확인 (예: youtube.com/@sebasi15)
                </p>
              </div>
              <div>
                <Label htmlFor="name">표시 이름 (선택)</Label>
                <Input
                  id="name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  placeholder="비우면 채널 메타에서 자동"
                />
              </div>
              <div>
                <Label htmlFor="desc">메모 (선택)</Label>
                <Input
                  id="desc"
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                />
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={form.is_active}
                  onChange={(e) => setForm({ ...form, is_active: e.target.checked })}
                />
                활성
              </label>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setOpen(false)}>
                취소
              </Button>
              <Button onClick={submit} disabled={!form.handle.trim()}>
                저장
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : data && data.length > 0 ? (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>이름</TableHead>
              <TableHead>핸들</TableHead>
              <TableHead>메모</TableHead>
              <TableHead>활성</TableHead>
              <TableHead className="text-right">액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((ch) => {
              const youtubeUrl = ch.handle.startsWith("@")
                ? `https://www.youtube.com/${ch.handle}`
                : `https://www.youtube.com/channel/${ch.handle}`;
              return (
                <TableRow key={ch.id}>
                  <TableCell className="font-medium">{ch.name || "—"}</TableCell>
                  <TableCell className="font-mono text-xs">
                    <a
                      href={youtubeUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 hover:underline"
                    >
                      {ch.handle} <ExternalLink className="h-3 w-3 opacity-60" />
                    </a>
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">{ch.description}</TableCell>
                  <TableCell>
                    {ch.is_active ? (
                      <Badge variant="success">활성</Badge>
                    ) : (
                      <Badge variant="secondary">비활성</Badge>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="sm" onClick={() => openEdit(ch)}>
                      <Pencil className="h-3 w-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        if (confirm(`"${ch.handle}" 채널을 삭제할까요?`)) remove.mutate(ch.id);
                      }}
                    >
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      ) : (
        <p className="text-sm text-muted-foreground">
          아직 등록된 채널이 없습니다. 우상단 "추가" 버튼으로 등록하세요.
        </p>
      )}
    </div>
  );
}
