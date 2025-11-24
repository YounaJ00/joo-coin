import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Types
export interface Coin {
  id: number;
  name: string;
}

export interface CoinListResponse {
  items: Coin[];
}

export interface CreateCoinRequest {
  name: string;
}

export interface OhlcvItem {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  value: number;
}

export interface OhlcvResponse {
  items: OhlcvItem[];
}

export interface TransactionItem {
  id: number;
  coin_id: number | null;
  coin_name: string | null;
  type: string | null;
  price: number;
  amount: number;
  risk_level: string;
  status: string;
  timestamp: string;
  ai_reason: string | null;
  execution_reason: string | null;
}

export interface TransactionsResponse {
  items: TransactionItem[];
  next_cursor: number | null;
  has_next: boolean;
}

export interface BalanceItem {
  id: number;
  amount: number;
  coin_amount: number;
  total_amount: number;
  created_at: string;
}

export interface BalancesResponse {
  items: BalanceItem[];
  next_cursor: number | null;
  has_next: boolean;
}

// API functions
export const coinApi = {
  getMyCoins: async (): Promise<CoinListResponse> => {
    const response = await apiClient.get<CoinListResponse>("/my/coins");
    return response.data;
  },

  createCoin: async (data: CreateCoinRequest): Promise<void> => {
    await apiClient.post("/my/coins", data);
  },

  deleteCoin: async (coinId: number): Promise<void> => {
    await apiClient.delete(`/my/coins/${coinId}`);
  },
};

export const upbitApi = {
  getOhlcv: async (coinName: string): Promise<OhlcvResponse> => {
    const response = await apiClient.get<OhlcvResponse>(`/coins/${coinName}`);
    return response.data;
  },
};

export const tradeApi = {
  executeTrade: async (): Promise<void> => {
    await apiClient.post("/trade");
  },

  getTransactions: async (
    cursor?: number,
    limit: number = 20
  ): Promise<TransactionsResponse> => {
    const params = new URLSearchParams();
    if (cursor) params.append("cursor", cursor.toString());
    params.append("limit", limit.toString());
    const response = await apiClient.get<TransactionsResponse>(
      `/trade/transactions?${params.toString()}`
    );
    return response.data;
  },
};

export const balanceApi = {
  getBalanceHistory: async (
    cursor?: number,
    limit: number = 100
  ): Promise<BalancesResponse> => {
    const params = new URLSearchParams();
    if (cursor) params.append("cursor", cursor.toString());
    params.append("limit", limit.toString());
    const response = await apiClient.get<BalancesResponse>(
      `/balance/history?${params.toString()}`
    );
    return response.data;
  },
};
