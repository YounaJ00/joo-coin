import { useCallback, useEffect, useState } from "react";
import { tradeApi, type TransactionItem } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Loader2, Play } from "lucide-react";
import { useToast } from "@/contexts/ToastContext";

export function TransactionHistory() {
  const [transactions, setTransactions] = useState<TransactionItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isExecuting, setIsExecuting] = useState(false);
  const [nextCursor, setNextCursor] = useState<number | null>(null);
  const [hasNext, setHasNext] = useState(false);
  const [selectedReason, setSelectedReason] = useState<{
    action: "buy" | "sell" | "hold";
    detail: string;
  } | null>(null);
  const { toast } = useToast();

  const fetchTransactions = useCallback(
    async (cursor?: number) => {
      setIsLoading(true);
      try {
        const response = await tradeApi.getTransactions(cursor);
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
        setIsLoading(false);
      }
    },
    [toast]
  );

  useEffect(() => {
    fetchTransactions();
  }, [fetchTransactions]);

  const handleExecuteTrade = async () => {
    setIsExecuting(true);
    try {
      await tradeApi.executeTrade();
      toast({
        title: "성공",
        description: "거래가 실행되었습니다.",
      });
      // 거래 실행 후 목록 새로고침
      setTimeout(() => {
        fetchTransactions();
      }, 1000);
    } catch (error) {
      console.error(error);
      toast({
        title: "오류",
        description: "거래 실행에 실패했습니다.",
        variant: "destructive",
      });
    } finally {
      setIsExecuting(false);
    }
  };

  const getTypeColor = (type: string | null) => {
    if (type === "buy") return "text-blue-600";
    if (type === "sell") return "text-red-600";
    return "text-gray-600";
  };

  const formatPrice = (value: number) => {
    return new Intl.NumberFormat("ko-KR", {
      style: "currency",
      currency: "KRW",
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatAmount = (value: number) => {
    return value.toFixed(8);
  };

  const getAiAction = (reason: string | null): "buy" | "sell" | "hold" => {
    if (!reason) return "hold";
    const lower = reason.toLowerCase();
    if (lower.includes("sell")) return "sell";
    if (lower.includes("buy")) return "buy";
    return "hold";
  };

  const getAiActionColor = (action: "buy" | "sell" | "hold") => {
    if (action === "buy") return "text-blue-500";
    if (action === "sell") return "text-red-500";
    return "text-muted-foreground";
  };

  const handleReasonClick = (reason: string | null) => {
    if (!reason) return;
    const action = getAiAction(reason);
    setSelectedReason({ action, detail: reason });
  };

  return (
    <Card className="h-full flex flex-col overflow-hidden">
      <CardHeader className="shrink-0 pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">거래 내역</CardTitle>
          <Button onClick={handleExecuteTrade} disabled={isExecuting} size="sm">
            {isExecuting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                실행 중...
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                거래 실행
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-y-auto p-0 min-h-0">
        {isLoading && transactions.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
          </div>
        ) : transactions.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <p className="text-muted-foreground">거래 내역이 없습니다.</p>
          </div>
        ) : (
          <>
            <div className="relative">
              <Table>
                <TableHeader className="sticky top-0 bg-card z-10">
                  <TableRow>
                    <TableHead className="text-xs">날짜</TableHead>
                    <TableHead className="text-xs">코인 ID</TableHead>
                    <TableHead className="text-xs">거래 종류</TableHead>
                    <TableHead className="text-xs">수량</TableHead>
                    <TableHead className="text-xs">가격</TableHead>
                    <TableHead className="text-xs">총액</TableHead>
                    <TableHead className="text-xs">AI 의견</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.map((transaction) => {
                    const totalAmount = transaction.price * transaction.amount;
                    return (
                      <TableRow key={transaction.id}>
                        <TableCell className="text-xs py-2">
                          {transaction.timestamp.split(" ")[0]}
                        </TableCell>
                        <TableCell className="font-medium text-xs py-2">
                          {transaction.coin_id || "-"}
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
                          {formatAmount(transaction.amount)}
                        </TableCell>
                        <TableCell className="text-xs py-2">
                          {formatPrice(transaction.price)}
                        </TableCell>
                        <TableCell className="font-semibold text-xs py-2">
                          {formatPrice(totalAmount)}
                        </TableCell>
                        <TableCell className="text-xs py-2">
                          {transaction.ai_reason ? (
                            <Button
                              variant="ghost"
                              size="sm"
                              className={`h-6 px-2 capitalize ${getAiActionColor(
                                getAiAction(transaction.ai_reason)
                              )}`}
                              onClick={() =>
                                handleReasonClick(transaction.ai_reason)
                              }
                            >
                              {getAiAction(transaction.ai_reason)}
                            </Button>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
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
                  onClick={() => fetchTransactions(nextCursor || undefined)}
                  disabled={isLoading}
                >
                  {isLoading ? (
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
      <Dialog
        open={selectedReason !== null}
        onOpenChange={(open) => {
          if (!open) setSelectedReason(null);
        }}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              AI 의견: {selectedReason?.action.toUpperCase()}
            </DialogTitle>
            <DialogDescription className="whitespace-pre-line">
              {selectedReason?.detail}
            </DialogDescription>
          </DialogHeader>
        </DialogContent>
      </Dialog>
    </Card>
  );
}
