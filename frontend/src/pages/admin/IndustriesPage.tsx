import { useState } from "react";
import { Pencil, Plus, Trash2 } from "lucide-react";

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
  useAdminIndustries,
  useCreateIndustry,
  useDeleteIndustry,
  useUpdateIndustry,
} from "@/lib/queries";
import type { Industry } from "@/types/api";

interface FormState {
  name: string;
  slug: string;
  sort_order: number;
  is_active: boolean;
}

const empty: FormState = { name: "", slug: "", sort_order: 0, is_active: true };

export function IndustriesPage() {
  const { data, isLoading } = useAdminIndustries();
  const create = useCreateIndustry();
  const update = useUpdateIndustry();
  const remove = useDeleteIndustry();

  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<Industry | null>(null);
  const [form, setForm] = useState<FormState>(empty);

  function openCreate() {
    setEditing(null);
    setForm(empty);
    setOpen(true);
  }
  function openEdit(ind: Industry) {
    setEditing(ind);
    setForm({
      name: ind.name,
      slug: ind.slug,
      sort_order: ind.sort_order,
      is_active: ind.is_active,
    });
    setOpen(true);
  }
  async function submit() {
    if (editing) {
      await update.mutateAsync({ id: editing.id, ...form });
    } else {
      await create.mutateAsync(form);
    }
    setOpen(false);
  }

  return (
    <div>
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Industries</h1>
          <p className="text-sm text-muted-foreground">업종 관리</p>
        </div>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger asChild>
            <Button onClick={openCreate}>
              <Plus className="mr-1 h-4 w-4" /> 추가
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{editing ? "업종 수정" : "업종 추가"}</DialogTitle>
            </DialogHeader>
            <div className="grid gap-3">
              <div>
                <Label htmlFor="name">이름</Label>
                <Input
                  id="name"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                />
              </div>
              <div>
                <Label htmlFor="slug">Slug</Label>
                <Input
                  id="slug"
                  value={form.slug}
                  onChange={(e) => setForm({ ...form, slug: e.target.value })}
                  placeholder="legal, hospital, fashion ..."
                />
              </div>
              <div>
                <Label htmlFor="sort">정렬 순서</Label>
                <Input
                  id="sort"
                  type="number"
                  value={form.sort_order}
                  onChange={(e) =>
                    setForm({ ...form, sort_order: Number(e.target.value) })
                  }
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
              <Button onClick={submit} disabled={create.isPending || update.isPending}>
                저장
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {isLoading ? (
        <p className="text-muted-foreground">불러오는 중...</p>
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>이름</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>키워드</TableHead>
              <TableHead>순서</TableHead>
              <TableHead>활성</TableHead>
              <TableHead className="text-right">액션</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data?.map((ind) => (
              <TableRow key={ind.id}>
                <TableCell className="font-medium">{ind.name}</TableCell>
                <TableCell className="font-mono text-xs">{ind.slug}</TableCell>
                <TableCell>{ind.keyword_count ?? 0}</TableCell>
                <TableCell>{ind.sort_order}</TableCell>
                <TableCell>{ind.is_active ? "✓" : "—"}</TableCell>
                <TableCell className="text-right">
                  <Button variant="ghost" size="sm" onClick={() => openEdit(ind)}>
                    <Pencil className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      if (confirm(`"${ind.name}" 업종을 삭제할까요? (키워드도 함께 삭제됨)`)) {
                        remove.mutate(ind.id);
                      }
                    }}
                  >
                    <Trash2 className="h-3 w-3" />
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
