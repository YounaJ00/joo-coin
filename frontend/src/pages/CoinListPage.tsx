import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import {
  coinApi,
  upbitApi,
  tradeApi,
  type Coin,
  type OhlcvItem,
  type TransactionItem,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ArrowLeft } from "lucide-react";
import { CoinSelector } from "@/components/CoinSelector";
import { MyCoinList } from "@/components/MyCoinList";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useToast } from "@/contexts/ToastContext";
import { Loader2 } from "lucide-react";

export function CoinListPage() {
  const navigate = useNavigate();
  const [myCoins, setMyCoins] = useState<Coin[]>([]);
  const [selectedCoin, setSelectedCoin] = useState<string | null>(null);
  const [coinData, setCoinData] = useState<OhlcvItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [isLoadingTransactions, setIsLoadingTransactions] = useState(false);
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [hasNext, setHasNext] = useState(false);
  const { toast } = useToast();

  const fetchMyCoins = useCallback(async () => {
    try {
      const response = await coinApi.getMyCoins();
      setMyCoins(response.items);
    } catch (error) {
      console.error(error);
      toast({
        title: "오류",
        description: "코인 목록을 불러오는데 실패했습니다.",
        variant: "destructive",
      });
    }
  }, [toast]);

  const fetchTransactions = useCallback(
    async (cursor?: number) => {
      setIsLoadingTransactions(true);
      try {
        const response = await tradeApi.getTransactions(cursor, 20);
        if (cursor) {
          setTransactions((prev) => [...prev, ...response.items]);
        } else {
          setTransactions(response.items);
        }
        setNextCursor(response.next_cursor);
        setHasNext(response.has_next);
      } catch (error) {
        console.error(error);
        toast({
          title: "오류",
          description: "거래 내역을 불러오는데 실패했습니다.",
          variant: "destructive",
        });
      } finally {
        setIsLoadingTransactions(false);
      }
    },
    [toast]
  );

  useEffect(() => {
    fetchMyCoins();
    fetchTransactions();
  }, [fetchMyCoins, fetchTransactions]);

  const fetchCoinData = useCallback(
    async (coinName: string) => {
      setIsLoading(true);
      try {
        const response = await upbitApi.getOhlcv(coinName);
        setCoinData(response.items);
      } catch (error) {
        console.error(error);
        toast({
          title: "오류",
          description: "코인 데이터를 불러오는데 실패했습니다.",
          variant: "destructive",
        });
        setCoinData([]);
      } finally {
        setIsLoading(false);
      }
    },
    [toast]
  );

  useEffect(() => {
    if (selectedCoin) {
      fetchCoinData(selectedCoin);
    } else {
      setCoinData([]);
    }
  }, [selectedCoin, fetchCoinData]);

  const getTypeColor = (type: string | null) => {
    if (type === "buy") return "text-blue-600";
    if (type === "sell") return "text-red-600";
    return "text-gray-600";
  };

  const formatAmount = (value: number) => {
    return value.toFixed(8);
  };

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
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => navigate("/")}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              메인으로
            </Button>
            <h1 className="text-2xl font-bold">거래 코인 목록</h1>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 h-[calc(100vh-100px)]">
          {/* 왼쪽 화면 */}
          <div className="flex flex-col gap-4 h-full">
            {/* 코인 선택 바 */}
            <CoinSelector
              selectedCoin={selectedCoin}
              onCoinSelect={setSelectedCoin}
            />

            {/* 거래 중인 코인 목록 */}
            <div className="flex-1 min-h-0">
              <MyCoinList
                myCoins={myCoins}
                selectedCoin={selectedCoin}
                onCoinSelect={setSelectedCoin}
                onCoinsChange={fetchMyCoins}
              />
            </div>
          </div>

          {/* 중앙: 선택된 코인 정보 */}
          <div className="h-full">
            <Card className="h-full">
              <CardHeader>
                <CardTitle>
                  {selectedCoin ? `${selectedCoin}/KRW` : "코인을 선택해주세요"}
                </CardTitle>
              </CardHeader>
              <CardContent className="h-[calc(100%-80px)]">
                {!selectedCoin ? (
                  <div className="flex items-center justify-center h-full">
                    <p className="text-muted-foreground">
                      코인을 선택해주세요.
                    </p>
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
          </div>

          {/* 오른쪽: 거래 내역 */}
          <div className="h-full">
            <Card className="h-full flex flex-col overflow-hidden">
              <CardHeader className="shrink-0 pb-3">
                <CardTitle className="text-lg">거래 내역</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 overflow-y-auto p-0 min-h-0">
                {isLoadingTransactions && transactions.length === 0 ? (
                  <div className="flex items-center justify-center h-32">
                    <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                  </div>
                ) : transactions.length === 0 ? (
                  <div className="flex items-center justify-center h-32">
                    <p className="text-muted-foreground">
                      거래 내역이 없습니다.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="relative">
                      <Table>
                        <TableHeader className="sticky top-0 bg-card z-10">
                          <TableRow>
                            <TableHead className="text-xs">날짜</TableHead>
                            <TableHead className="text-xs">코인</TableHead>
                            <TableHead className="text-xs">종류</TableHead>
                            <TableHead className="text-xs">가격</TableHead>
                            <TableHead className="text-xs">수량</TableHead>
                            <TableHead className="text-xs">총액</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {transactions.map((transaction) => {
                            const totalAmount =
                              transaction.price * transaction.amount;
                            return (
                              <TableRow key={transaction.id}>
                                <TableCell className="text-xs py-2">
                                  {transaction.timestamp.split(" ")[0]}
                                </TableCell>
                                <TableCell className="font-medium text-xs py-2">
                                  {transaction.coin_name || "-"}
                                </TableCell>
                                <TableCell
                                  className={`text-xs py-2 ${getTypeColor(
                                    transaction.type
                                  )}`}
                                >
                                  {transaction.type === "buy"
                                    ? "매수"
                                    : transaction.type === "sell"
                                    ? "매도"
                                    : "-"}
                                </TableCell>
                                <TableCell className="text-xs py-2">
                                  {formatPrice(transaction.price)}
                                </TableCell>
                                <TableCell className="text-xs py-2">
                                  {formatAmount(transaction.amount)}
                                </TableCell>
                                <TableCell className="font-semibold text-xs py-2">
                                  {formatPrice(totalAmount)}
                                </TableCell>
                              </TableRow>
                            );
                          })}
                        </TableBody>
                      </Table>
                    </div>
                    {hasNext && (
                      <div className="sticky bottom-0 bg-card border-t p-2 text-center">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            fetchTransactions(nextCursor || undefined)
                          }
                          disabled={isLoadingTransactions}
                        >
                          {isLoadingTransactions ? (
                            <>
                              <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                              로딩 중...
                            </>
                          ) : (
                            "더 보기"
                          )}
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
