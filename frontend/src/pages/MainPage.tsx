import { useState, useEffect } from "react";
import { coinApi, upbitApi, type Coin, type OhlcvItem } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TransactionHistory } from "@/components/TransactionHistory";
import { BalanceChart } from "@/components/BalanceChart";
import { CoinSelector } from "@/components/CoinSelector";
import { MyCoinList } from "@/components/MyCoinList";
import { CoinInfo } from "@/components/CoinInfo";
import { useToast } from "@/contexts/ToastContext";

export function MainPage() {
  const [myCoins, setMyCoins] = useState<Coin[]>([]);
  const [selectedCoin, setSelectedCoin] = useState<string | null>(null);
  const [coinData, setCoinData] = useState<OhlcvItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchMyCoins();
  }, []);

  useEffect(() => {
    if (selectedCoin) {
      fetchCoinData(selectedCoin);
    } else {
      setCoinData([]);
    }
  }, [selectedCoin]);

  const fetchMyCoins = async () => {
    try {
      const response = await coinApi.getMyCoins();
      setMyCoins(response.items);
    } catch (error) {
      toast({
        title: "오류",
        description: "코인 목록을 불러오는데 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  const fetchCoinData = async (coinName: string) => {
    setIsLoading(true);
    try {
      const response = await upbitApi.getOhlcv(coinName);
      setCoinData(response.items);
    } catch (error) {
      toast({
        title: "오류",
        description: "코인 데이터를 불러오는데 실패했습니다.",
        variant: "destructive",
      });
      setCoinData([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b bg-card sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">Joo Coin 거래소</h1>
        </div>
      </header>

      <main className="container mx-auto px-4 py-4 h-[calc(100vh-80px)] overflow-hidden">
        <div className="grid grid-cols-1 lg:grid-cols-10 gap-4 h-full">
          {/* 계좌 잔액 변동 + 거래 내역 */}
          <div className="lg:col-span-4 flex flex-col gap-4 h-full overflow-hidden">
            {/* 계좌 잔액 변동 그래프 */}
            <Card className="shrink-0">
              <CardHeader className="pb-2">
                <CardTitle className="text-lg">계좌 잔액 변동</CardTitle>
              </CardHeader>
              <CardContent className="h-48">
                <BalanceChart />
              </CardContent>
            </Card>

            {/* 거래 내역 */}
            <div className="flex-1 min-h-0">
              <TransactionHistory />
            </div>
          </div>

          {/* 오른쪽: 거래 코인 목록 페이지 내용 */}
          <div className="lg:col-span-6 flex flex-col gap-4 h-full overflow-hidden">
            {/* 코인 선택 바 */}
            <CoinSelector
              selectedCoin={selectedCoin}
              onCoinSelect={setSelectedCoin}
            />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 flex-1 min-h-0">
              {/* 거래 중인 코인 목록 */}
              <MyCoinList
                myCoins={myCoins}
                selectedCoin={selectedCoin}
                onCoinSelect={setSelectedCoin}
                onCoinsChange={fetchMyCoins}
              />

              {/* 선택된 코인 정보 */}
              <CoinInfo
                coinName={selectedCoin}
                coinData={coinData}
                isLoading={isLoading}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
