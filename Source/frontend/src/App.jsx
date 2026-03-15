import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './pages/home/Home.jsx';
import Summary from './pages/summary/summary.jsx';
import MASFlowPage from './pages/mas-flow/MASFlowPage.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/summary" element={<Summary />} />
        <Route path="/mas-flow" element={<MASFlowPage />} />
      </Routes>
    </BrowserRouter>
  );
}
