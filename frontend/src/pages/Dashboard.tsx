import { Link, useSearchParams } from "react-router-dom";
import { Calendar, ChevronRight, Loader2 } from "lucide-react";

import { ContentList } from "@/components/ContentList";
import { DateNavigator } from "@/components/DateNavigator";
import { TrendList } from "@/components/TrendList";
import { VideoList } from "@/components/VideoList";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useDashboard } from "@/lib/queries";
import { todayISO } from "@/lib/utils";

export function Dashboard() {
  const [params, setParams] = useSearchParams();
  const date = params.get("date") ?? todayISO();

  const { data, isLoading, error } = useDashboard(date);

  function update(key: string, value?: string) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  }

  return (
    <div className="container py-6">
      <header className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <Link to="/" className="text-2xl font-bold">
            📈 MarketingPulse
          </Link>
          <p className="text-sm text-muted-foreground">
            매일 아침의 마케팅 트렌드 / 이슈 / 뉴스
          </p>
        </div>
        <div className="flex items-center gap-2">
          <DateNavigator date={date} onChange={(d) => update("date", d)} />
          <Button variant="outline" asChild>
            <Link to="/archive">
              <Calendar className="mr-1 h-4 w-4" />
              아카이브
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <Link to="/admin">Admin →</Link>
          </Button>
        </div>
      </header>

      {isLoading ? (
        <div className="flex items-center gap-2 py-12 text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" /> 불러오는 중...
        </div>
      ) : error ? (
        <Card>
          <CardContent className="py-6 text-sm text-destructive">
            데이터를 불러오지 못했습니다. 백엔드가 실행 중인지 확인하세요.
          </CardContent>
        </Card>
      ) : data ? (
        <>
          {/* 1행: 핫이슈 + 트렌드 */}
          <div className="grid grid-cols-1 items-start gap-6 lg:grid-cols-3">
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle>📰 오늘의 핫이슈</CardTitle>
              </CardHeader>
              <CardContent>
                <ContentList items={data.news} emptyText="일반 뉴스가 없습니다." />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>🔥 네이버 검색 TOP 10</CardTitle>
                <p className="text-xs text-muted-foreground">지난 7일 검색량 기준</p>
              </CardHeader>
              <CardContent>
                <TrendList trends={(data.trends["naver_datalab"] ?? []).slice(0, 10)} />
              </CardContent>
            </Card>
          </div>

          {/* 2행: 유튜브 — 마케팅 영상 + 큐레이션 채널 */}
          <div className="mt-6 grid grid-cols-1 items-start gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>🎬 오늘의 마케팅 영상 TOP</CardTitle>
                <p className="text-xs text-muted-foreground">
                  YouTube 마케팅 키워드 검색 (조회수 정렬)
                </p>
              </CardHeader>
              <CardContent>
                <VideoList
                  items={data.youtube_marketing.slice(0, 6)}
                  emptyText="마케팅 영상 데이터 없음"
                />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>🎙️ 마케팅 채널 신규</CardTitle>
                <p className="text-xs text-muted-foreground">
                  큐레이션 채널 (EO / 김미경TV / 퍼블리 등)의 최신 영상
                </p>
              </CardHeader>
              <CardContent>
                <VideoList
                  items={data.youtube_curated.slice(0, 6)}
                  emptyText="큐레이션 영상 없음"
                />
              </CardContent>
            </Card>
          </div>

          {/* 3행: 업종별 카드 */}
          <h2 className="mb-4 mt-10 text-xl font-semibold">🏷️ 업종별</h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            {data.industries.map((ind) => {
              const items = data.by_industry[ind.slug] ?? [];
              return (
                <Card key={ind.slug}>
                  <CardHeader className="flex flex-row items-center justify-between">
                    <CardTitle className="text-base">{ind.name}</CardTitle>
                    <Link
                      to={`/industries/${ind.slug}`}
                      className="flex items-center text-xs text-muted-foreground hover:text-foreground"
                    >
                      더보기 <ChevronRight className="h-3 w-3" />
                    </Link>
                  </CardHeader>
                  <CardContent>
                    <ContentList items={items.slice(0, 5)} emptyText="해당 업종 콘텐츠 없음" />
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <p className="mt-8 text-xs text-muted-foreground">
            총 {data.totals.items}건의 콘텐츠 / {data.totals.trends}개 트렌드 키워드
          </p>
        </>
      ) : null}
    </div>
  );
}
