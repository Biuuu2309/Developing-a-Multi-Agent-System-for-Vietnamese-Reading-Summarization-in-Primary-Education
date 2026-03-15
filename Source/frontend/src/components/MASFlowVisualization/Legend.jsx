import { Info } from 'lucide-react';
import { NODE_STATES, EDGE_STATES, COLORS } from './utils/masFlowConfig';
import './Legend.css';

export default function Legend() {
  const nodeStates = [
    { state: NODE_STATES.IDLE, label: 'Chưa chạy', color: COLORS.idle },
    { state: NODE_STATES.ACTIVE, label: 'Đang chạy', color: COLORS.active },
    { state: NODE_STATES.COMPLETED, label: 'Hoàn thành', color: COLORS.completed },
    { state: NODE_STATES.ERROR, label: 'Lỗi', color: COLORS.error },
    { state: NODE_STATES.SKIPPED, label: 'Bỏ qua', color: COLORS.skipped },
  ];

  const edgeStates = [
    { state: EDGE_STATES.PENDING, label: 'Chưa traverse', color: COLORS.idle },
    { state: EDGE_STATES.ACTIVE, label: 'Đang traverse', color: COLORS.active },
    { state: EDGE_STATES.COMPLETED, label: 'Đã traverse', color: COLORS.completed },
  ];

  return (
    <div className="mas-flow-legend">
      <div className="mas-flow-legend-header">
        <Info size={16} />
        <span>Chú thích</span>
      </div>
      <div className="mas-flow-legend-content">
        <div className="mas-flow-legend-section">
          <div className="mas-flow-legend-title">Trạng thái Node</div>
          <div className="mas-flow-legend-items">
            {nodeStates.map((item) => (
              <div key={item.state} className="mas-flow-legend-item">
                <div
                  className="mas-flow-legend-color"
                  style={{ backgroundColor: item.color }}
                />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="mas-flow-legend-section">
          <div className="mas-flow-legend-title">Trạng thái Edge</div>
          <div className="mas-flow-legend-items">
            {edgeStates.map((item) => (
              <div key={item.state} className="mas-flow-legend-item">
                <div
                  className="mas-flow-legend-color mas-flow-legend-color-edge"
                  style={{ borderColor: item.color, backgroundColor: 'transparent' }}
                />
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
