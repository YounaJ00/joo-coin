import { useState } from "react";
import { coinApi, type Coin } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Plus, Trash2 } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useToast } from "@/contexts/ToastContext";
import { AVAILABLE_COINS } from "@/constants/coins";

interface MyCoinListProps {
  myCoins: Coin[];
  selectedCoin: string | null;
  onCoinSelect: (coin: string | null) => void;
  onCoinsChange: () => void;
}

export function MyCoinList({
  myCoins,
  selectedCoin,
  onCoinSelect,
  onCoinsChange,
}: MyCoinListProps) {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedCoinToAdd, setSelectedCoinToAdd] = useState<string>("");
  const [isAddingCoin, setIsAddingCoin] = useState(false);
  const { toast } = useToast();

  const handleAddCoin = async () => {
    if (!selectedCoinToAdd) {
      toast({
        title: "오류",
        description: "코인을 선택해주세요.",
        variant: "destructive",
      });
      return;
    }

    if (myCoins.some((coin) => coin.name === selectedCoinToAdd)) {
      toast({
        title: "오류",
        description: "이미 추가된 코인입니다.",
        variant: "destructive",
      });
      return;
    }

    setIsAddingCoin(true);
    try {
      await coinApi.createCoin({ name: selectedCoinToAdd });
      setSelectedCoinToAdd("");
      setIsDialogOpen(false);
      onCoinsChange();
      toast({
        title: "성공",
        description: "코인이 추가되었습니다.",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "오류",
        description: "코인 추가에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsAddingCoin(false);
    }
  };

  const handleDeleteCoin = async (coinId: number) => {
    if (!confirm("정말 이 코인을 삭제하시겠습니까?")) return;

    try {
      const targetCoin = myCoins.find((c) => c.id === coinId);
      await coinApi.deleteCoin(coinId);
      onCoinsChange();
      if (targetCoin?.name === selectedCoin) {
        onCoinSelect(null);
      }
      toast({
        title: "성공",
        description: "코인이 삭제되었습니다.",
      });
    } catch (error) {
      console.error(error);
      toast({
        title: "오류",
        description: "코인 삭제에 실패했습니다.",
        variant: "destructive",
      });
    }
  };

  return (
    <Card className="flex flex-col overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>거래 중인 코인 목록</CardTitle>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" variant="outline">
                <Plus className="h-4 w-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>코인 추가</DialogTitle>
                <DialogDescription>
                  거래 가능한 코인 목록에서 선택하세요.
                </DialogDescription>
              </DialogHeader>
              <div className="py-4">
                <Select
                  value={selectedCoinToAdd}
                  onValueChange={setSelectedCoinToAdd}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="코인을 선택하세요" />
                  </SelectTrigger>
                  <SelectContent>
                    {AVAILABLE_COINS.filter(
                      (coin) => !myCoins.some((myCoin) => myCoin.name === coin)
                    ).map((coin) => (
                      <SelectItem key={coin} value={coin}>
                        {coin}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <DialogFooter>
                <Button
                  onClick={handleAddCoin}
                  disabled={isAddingCoin || !selectedCoinToAdd}
                >
                  추가
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-0">
        <div className="divide-y">
          {myCoins.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              거래 중인 코인이 없습니다. 코인을 추가해주세요.
            </div>
          ) : (
            myCoins.map((coin) => (
              <div
                key={coin.id}
                className={`flex items-center justify-between p-3 cursor-pointer hover:bg-muted/50 transition-colors ${
                  selectedCoin === coin.name ? "bg-muted" : ""
                }`}
                onClick={() => onCoinSelect(coin.name)}
              >
                <span className="font-medium">{coin.name}</span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-8 w-8 p-0"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteCoin(coin.id);
                  }}
                >
                  <Trash2 className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
