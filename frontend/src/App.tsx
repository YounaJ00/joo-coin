import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { MainPage } from '@/pages/MainPage';
import { CoinListPage } from '@/pages/CoinListPage';
import { Toaster } from '@/components/Toaster';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="/coins" element={<CoinListPage />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
