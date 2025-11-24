import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AVAILABLE_COINS } from "@/constants/coins";

interface CoinSelectorProps {
  selectedCoin: string | null;
  onCoinSelect: (coin: string) => void;
}

export function CoinSelector({
  selectedCoin,
  onCoinSelect,
}: CoinSelectorProps) {
  return (
    <Card className="shrink-0">
      <CardHeader>
        <CardTitle>거래 가능한 코인</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {AVAILABLE_COINS.map((coin) => (
            <Button
              key={coin}
              variant={selectedCoin === coin ? "default" : "outline"}
              size="sm"
              onClick={() => onCoinSelect(coin)}
            >
              {coin}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
