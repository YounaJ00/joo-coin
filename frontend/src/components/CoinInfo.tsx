import { type OhlcvItem } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { Loader2 } from "lucide-react";

interface CoinInfoProps {
  coinName: string | null;
  coinData: OhlcvItem[];
  isLoading: boolean;
}

export function CoinInfo({ coinName, coinData, isLoading }: CoinInfoProps) {
  const formatPrice = (value: number) => {
    return new Intl.NumberFormat("ko-KR", {
      style: "currency",
      currency: "KRW",
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatDate = (timestamp: string) => {
    return new Date(timestamp).toLocaleString("ko-KR", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const chartData = coinData.map((item) => ({
    time: formatDate(item.timestamp),
    close: item.close,
  }));

  const latestPrice =
    coinData.length > 0 ? coinData[coinData.length - 1]?.close : 0;
  const prevPrice =
    coinData.length > 1 ? coinData[coinData.length - 2]?.close : latestPrice;
  const change = latestPrice - prevPrice;
  const changePercent = prevPrice > 0 ? (change / prevPrice) * 100 : 0;

  return (
    <Card className="flex flex-col overflow-hidden">
      <CardHeader>
        <CardTitle>
          {coinName ? `${coinName}/KRW` : "코인을 선택해주세요"}
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto">
        {!coinName ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">코인을 선택해주세요.</p>
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : chartData.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">데이터가 없습니다.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {/* 현재가 정보 */}
            <div>
              <div className="flex items-baseline gap-4">
                <span className="text-2xl font-bold">
                  {formatPrice(latestPrice)}
                </span>
                <span
                  className={`text-lg ${
                    change >= 0 ? "text-red-500" : "text-blue-500"
                  }`}
                >
                  {change >= 0 ? "+" : ""}
                  {changePercent.toFixed(2)}% ({change >= 0 ? "+" : ""}
                  {formatPrice(change)})
                </span>
              </div>
            </div>

            {/* 작은 차트 */}
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="time"
                    tick={{ fontSize: 10 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis
                    tick={{ fontSize: 10 }}
                    tickFormatter={(value) => formatPrice(value)}
                  />
                  <Tooltip
                    formatter={(value: number) => formatPrice(value)}
                    labelFormatter={(label) => label}
                  />
                  <Line
                    type="monotone"
                    dataKey="close"
                    stroke="#3b82f6"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 코인 상세 정보 */}
            {coinData.length > 0 && (
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">시가</p>
                  <p className="font-semibold">
                    {formatPrice(coinData[coinData.length - 1].open)}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">고가</p>
                  <p className="font-semibold text-red-500">
                    {formatPrice(coinData[coinData.length - 1].high)}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">저가</p>
                  <p className="font-semibold text-blue-500">
                    {formatPrice(coinData[coinData.length - 1].low)}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">종가</p>
                  <p className="font-semibold">
                    {formatPrice(coinData[coinData.length - 1].close)}
                  </p>
                </div>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

