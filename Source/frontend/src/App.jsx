import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/home/Home.jsx';
import Summary from './pages/summary/summary.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/summary" element={<Summary />} />
      </Routes>
    </BrowserRouter>
  );
}
