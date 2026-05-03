import { Link } from "react-router-dom";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function lastNDays(n: number): string[] {
  const result: string[] = [];
  const today = new Date();
  for (let i = 0; i < n; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() - i);
    result.push(d.toISOString().slice(0, 10));
  }
  return result;
}

export function Archive() {
  const days = lastNDays(30);
  return (
    <div className="container py-6">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">📅 아카이브</h1>
          <p className="text-sm text-muted-foreground">최근 30일</p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/">대시보드로</Link>
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>날짜 선택</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-7">
            {days.map((date) => (
              <Button key={date} variant="outline" asChild>
                <Link to={`/?date=${date}`}>{date}</Link>
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
