import { Link, useParams } from "react-router-dom";
import { Loader2 } from "lucide-react";

import { ContentList } from "@/components/ContentList";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useContentList, usePublicIndustries } from "@/lib/queries";

export function IndustryDetail() {
  const { slug } = useParams<{ slug: string }>();
  const { data: industries } = usePublicIndustries();
  const { data, isLoading } = useContentList({ industry: slug });

  const industry = industries?.find((i) => i.slug === slug);

  return (
    <div className="container py-6">
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{industry?.name ?? slug}</h1>
          <p className="text-sm text-muted-foreground">업종별 누적 콘텐츠</p>
        </div>
        <Button variant="outline" asChild>
          <Link to="/">대시보드로</Link>
        </Button>
      </header>

      <Card>
        <CardHeader>
          <CardTitle>콘텐츠</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> 불러오는 중...
            </div>
          ) : (
            <ContentList items={data?.results ?? []} />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
