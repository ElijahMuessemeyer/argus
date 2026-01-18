import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ScreenerPage } from './pages/ScreenerPage';
import { StockDetailPage } from './pages/StockDetailPage';
import { SignalsPage } from './pages/SignalsPage';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter
        future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
      >
        <Routes>
          <Route path="/" element={<ScreenerPage />} />
          <Route path="/stock/:symbol" element={<StockDetailPage />} />
          <Route path="/signals" element={<SignalsPage />} />
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
