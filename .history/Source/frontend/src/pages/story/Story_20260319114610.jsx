import { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BookOpen, BookText, Home as HomeIcon, Search, Zap } from 'lucide-react';
import { MorphingNavigation } from "../../components/lightswind/morphing-navigation.tsx";
import { GravityStarsBackground } from '../../components/animate-ui/components/backgrounds/gravity-stars';
import './Story.css';
import {
  getAllSummaries,
  getSummariesByContributor,
  getSummariesByGrade,
  getSummariesByMethod,
  getSummariesByStatus,
  getTop10Summaries,
  searchSummaries,
} from '../../services/summaryApi';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8081';

function formatDate(value) {
  if (!value) return '';
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  return d.toLocaleString();
}

function resolveImageSrc(src) {
  if (!src) return '';
  if (typeof src !== 'string') return '';
  if (src.startsWith('http://') || src.startsWith('https://')) return src;
  if (src.startsWith('/')) return `${API_BASE_URL}${src}`;
  return `${API_BASE_URL}/${src}`;
}

function parseImageUrls(imageUrl) {
  // imageUrl from SummaryDTO is often a JSON array string (e.g. '["https://...","https://..."]')
  if (!imageUrl) return [];
  try {
    const raw = typeof imageUrl === 'string' ? imageUrl.trim() : imageUrl;
    if (typeof raw === 'string') {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed)) {
        return parsed
          .map((item) => {
            if (!item) return null;
            if (typeof item === 'string') return item;
            if (typeof item === 'object') return item.url || item.imageUrl || null;
            return null;
          })
          .filter(Boolean);
      }
    }
  } catch {
    // Fallback: treat it as a direct URL/path
  }
  return [typeof imageUrl === 'string' ? imageUrl : ''].filter(Boolean);
}

function SummaryCard({ s, onOpen }) {
  return (
    <button type="button" className="story-card" onClick={() => onOpen(s)} title="Xem chi tiết">
      <div className="story-card-title">{s.title || '(No title)'}</div>
      <div className="story-card-meta">
        <span className="tag">{s.grade || 'N/A'}</span>
        <span className="tag">{s.method || 'N/A'}</span>
        <span className={`tag tag-${(s.status || 'UNKNOWN').toLowerCase()}`}>{s.status || 'UNKNOWN'}</span>
        <span className="muted">Reads: {Number(s.readCount ?? 0)}</span>
      </div>
      <div className="story-card-sub">
        <span className="muted">By: {s.createdByUserId || 'N/A'}</span>
        {s.createdAt ? <span className="muted">{formatDate(s.createdAt)}</span> : null}
      </div>
      <div className="story-card-preview">{s.summaryContent || s.content || ''}</div>
    </button>
  );
}

export default function Story() {
  const navigate = useNavigate();

  const navLinks = useMemo(
    () => [
      { id: 'home', label: 'Home', href: '/', icon: <HomeIcon size={30} /> },
      { id: 'summary', label: 'Summary', href: '/summary', icon: <BookOpen size={30} /> },
      { id: 'story', label: 'Story', href: '/story', icon: <BookText size={30} /> },
      { id: 'mas-flow', label: 'MAS Flow', href: '/mas-flow', icon: <Zap size={30} /> },
    ],
    [],
  );

  const handleLinkClick = useCallback(
    (link) => {
      if (link.id === 'home') navigate('/');
      else if (link.id === 'summary') navigate('/summary');
      else if (link.id === 'story') navigate('/story');
      else if (link.id === 'mas-flow') navigate('/mas-flow');
    },
    [navigate],
  );

  const [top10, setTop10] = useState([]);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [searchTerm, setSearchTerm] = useState('');
  const [searchGrade, setSearchGrade] = useState('');

  const [status, setStatus] = useState('');
  const [contributor, setContributor] = useState('');
  const [grade, setGrade] = useState('');
  const [method, setMethod] = useState('');

  const [selected, setSelected] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [all, top] = await Promise.all([getAllSummaries(), getTop10Summaries()]);
      setItems(Array.isArray(all) ? all : []);
      setTop10(Array.isArray(top) ? top : []);
    } catch (e) {
      setError(e?.message || 'Failed to load summaries');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const applyFilters = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      if (searchTerm.trim()) {
        const res = await searchSummaries({ searchTerm: searchTerm.trim(), grade: searchGrade || undefined });
        setItems(Array.isArray(res) ? res : []);
        return;
      }

      if (status) {
        const res = await getSummariesByStatus(status);
        setItems(Array.isArray(res) ? res : []);
        return;
      }
      if (contributor) {
        const res = await getSummariesByContributor(contributor.trim());
        setItems(Array.isArray(res) ? res : []);
        return;
      }
      if (grade) {
        const res = await getSummariesByGrade(grade);
        setItems(Array.isArray(res) ? res : []);
        return;
      }
      if (method) {
        const res = await getSummariesByMethod(method);
        setItems(Array.isArray(res) ? res : []);
        return;
      }

      await load();
    } catch (e) {
      setError(e?.message || 'Failed to apply filters');
    } finally {
      setLoading(false);
    }
  }, [contributor, grade, load, method, searchGrade, searchTerm, status]);

  useEffect(() => {
    applyFilters();
  }, [applyFilters]);

  const resetAll = useCallback(() => {
    setSearchTerm('');
    setSearchGrade('');
    setStatus('');
    setContributor('');
    setGrade('');
    setMethod('');
  }, []);

  return (
    <div className="story-page" style={{ width: '100%', minHeight: '100vh', position: 'relative' }}>
      <GravityStarsBackground className="gravity-stars-bg" starsCount={100} starsSize={4} starsOpacity={0.8} glowIntensity={20} movementSpeed={0.4} mouseInfluence={150} mouseGravity="attract" gravityStrength={100} />
      <MorphingNavigation
        links={navLinks}
        theme="custom"
        backgroundColor="#ffffff00"
        textColor="#0000ff"
        borderColor="rgba(59, 130, 246, 0.9)"
        onLinkClick={handleLinkClick}
        scrollThreshold={150}
        animationDuration={1.5}
        enablePageBlur={true}
        glowIntensity={5}
      />

      <div className="story-wrap">
        <div className="story-header">
          <div>
            <div className="story-title">Story</div>
            <div className="story-subtitle">Các văn bản đã được tóm tắt (từ bảng summaries)</div>
          </div>
        </div>

        <div className="story-filters">
          <div className="story-search">
            <div className="story-search-input">
              <Search size={18} />
              <input
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Tìm theo title (có thể kèm filter grade)..."
              />
            </div>
            <select value={searchGrade} onChange={(e) => setSearchGrade(e.target.value)}>
              <option value="">Grade (optional)</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="F">F</option>
            </select>
          </div>

          <div className="story-filter-row">
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">Status</option>
              <option value="PENDING">PENDING</option>
              <option value="APPROVED">APPROVED</option>
              <option value="REJECTED">REJECTED</option>
            </select>

            <select value={grade} onChange={(e) => setGrade(e.target.value)}>
              <option value="">Grade</option>
              <option value="A">A</option>
              <option value="B">B</option>
              <option value="C">C</option>
              <option value="D">D</option>
              <option value="F">F</option>
            </select>

            <select value={method} onChange={(e) => setMethod(e.target.value)}>
              <option value="">Method</option>
              <option value="extractive">extractive</option>
              <option value="abstractive">abstractive</option>
              <option value="MAS">MAS</option>
              <option value="Normal">Normal</option>
            </select>

            <input
              className="story-filter-input"
              value={contributor}
              onChange={(e) => setContributor(e.target.value)}
              placeholder="Contributor userId"
            />

            <button type="button" className="story-btn" onClick={resetAll}>
              Reset
            </button>
          </div>

          <div className="story-hint">
            Lưu ý: UI ưu tiên theo thứ tự: Search → Status → Contributor → Grade → Method. Nếu bạn muốn “kết hợp nhiều filter cùng lúc”, mình sẽ nâng cấp sang API kết hợp hoặc filter client-side.
          </div>
        </div>

        <div className="story-grid">
          <div className="story-panel">
            <div className="panel-title">Top 10 bản tóm tắt tốt nhất (đọc nhiều nhất)</div>
            <div className="panel-body">
              {top10.length ? (
                <div className="story-list">
                  {top10.map((s) => (
                    <SummaryCard key={s.summaryId} s={s} onOpen={setSelected} />
                  ))}
                </div>
              ) : (
                <div className="muted">Chưa có dữ liệu.</div>
              )}
            </div>
          </div>

          <div className="story-panel">
            <div className="panel-title">Danh sách summaries (tối đa theo API trả về)</div>
            <div className="panel-body">
              {error ? <div className="story-error">{error}</div> : null}
              {loading ? <div className="muted">Đang tải...</div> : null}
              {!loading && !items.length ? <div className="muted">Không có kết quả.</div> : null}
              <div className="story-list">
                {items.map((s) => (
                  <SummaryCard key={s.summaryId} s={s} onOpen={setSelected} />
                ))}
              </div>
            </div>
          </div>
        </div>

        {selected ? (
          <div className="story-modal-backdrop" role="dialog" aria-modal="true" onClick={() => setSelected(null)}>
            <div className="story-modal" onClick={(e) => e.stopPropagation()}>
              <div className="story-modal-head">
                <div className="story-modal-title">{selected.title || '(No title)'}</div>
                <button type="button" className="story-btn" onClick={() => setSelected(null)}>
                  Đóng
                </button>
              </div>
              <div className="story-modal-meta">
                <span className="tag">{selected.grade || 'N/A'}</span>
                <span className="tag">{selected.method || 'N/A'}</span>
                <span className={`tag tag-${(selected.status || 'UNKNOWN').toLowerCase()}`}>{selected.status || 'UNKNOWN'}</span>
                <span className="muted">Reads: {Number(selected.readCount ?? 0)}</span>
                <span className="muted">By: {selected.createdByUserId || 'N/A'}</span>
                {selected.createdAt ? <span className="muted">{formatDate(selected.createdAt)}</span> : null}
              </div>

              <div className="story-modal-section">
                <div className="section-title">Bản tóm tắt</div>
                {(() => {
                  const imageUrls = parseImageUrls(selected?.imageUrl);
                  if (imageUrls.length) {
                    return (
                      <div className="story-modal-img">
                        <img src={resolveImageSrc(imageUrls[0])} alt="Summary" />
                      </div>
                    );
                  }
                  return <div className="section-content">{selected.summaryContent || '(trống)'}</div>;
                })()}
              </div>

              <div className="story-modal-section">
                <div className="section-title">Văn bản gốc</div>
                <div className="section-content">{selected.content || '(trống)'}</div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

