import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { balanceApi } from "@/lib/api";
import { useToast } from "@/contexts/ToastContext";
import { Loader2 } from "lucide-react";

export function BalanceChart() {
  const [data, setData] = useState<Array<{ date: string; balance: number }>>(
    []
  );
  const [isLoading, setIsLoading] = useState(true);
  const { toast } = useToast();

  useEffect(() => {
    const fetchBalanceData = async () => {
      setIsLoading(true);
      try {
        // 최근 100개 데이터 조회 (차트에 충분한 데이터)
        const response = await balanceApi.getBalanceHistory(undefined, 100);

        // 날짜순으로 정렬 (오래된 것부터)
        const sortedItems = [...response.items].sort(
          (a, b) =>
            new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );

        // 차트 데이터 형식으로 변환
        const chartData = sortedItems.map((item) => ({
          date: new Date(item.created_at).toLocaleDateString("ko-KR", {
            month: "short",
            day: "numeric",
          }),
          balance: item.total_amount, // 총 자산 사용
        }));

        setData(chartData);
      } catch (error) {
        toast({
          title: "오류",
          description: "잔고 데이터를 불러오는데 실패했습니다.",
          variant: "destructive",
        });
        setData([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchBalanceData();
  }, [toast]);

  const formatBalance = (value: number) => {
    return new Intl.NumberFormat("ko-KR", {
      style: "currency",
      currency: "KRW",
      maximumFractionDigits: 0,
    }).format(value);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground">데이터가 없습니다.</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 10 }}
          interval="preserveStartEnd"
        />
        <YAxis
          tick={{ fontSize: 10 }}
          tickFormatter={(value) => {
            if (value >= 1000000) {
              return `${(value / 1000000).toFixed(1)}M`;
            }
            return `${(value / 1000).toFixed(0)}K`;
          }}
        />
        <Tooltip
          formatter={(value: number) => formatBalance(value)}
          labelFormatter={(label) => label}
        />
        <Line
          type="monotone"
          dataKey="balance"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
