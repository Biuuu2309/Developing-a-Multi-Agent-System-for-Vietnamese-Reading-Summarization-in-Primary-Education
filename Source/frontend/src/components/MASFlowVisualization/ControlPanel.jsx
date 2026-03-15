import { Play, Pause, Square, RotateCcw, Gauge } from 'lucide-react';
import './ControlPanel.css';

export default function ControlPanel({
  isPlaying,
  isPaused,
  speed,
  onPlay,
  onPause,
  onResume,
  onStop,
  onReset,
  onSpeedChange,
}) {
  const speedOptions = [
    { value: 0.5, label: '0.5x' },
    { value: 1, label: '1x' },
    { value: 2, label: '2x' },
  ];

  return (
    <div className="mas-flow-control-panel">
      <div className="mas-flow-controls">
        {/* Play/Pause Button */}
        {!isPlaying ? (
          <button
            className="mas-flow-control-btn mas-flow-control-btn-primary"
            onClick={onPlay}
            title="Play"
          >
            <Play size={18} />
          </button>
        ) : isPaused ? (
          <button
            className="mas-flow-control-btn mas-flow-control-btn-primary"
            onClick={onResume}
            title="Resume"
          >
            <Play size={18} />
          </button>
        ) : (
          <button
            className="mas-flow-control-btn mas-flow-control-btn-primary"
            onClick={onPause}
            title="Pause"
          >
            <Pause size={18} />
          </button>
        )}

        {/* Stop Button */}
        <button
          className="mas-flow-control-btn"
          onClick={onStop}
          title="Stop"
          disabled={!isPlaying && !isPaused}
        >
          <Square size={18} />
        </button>

        {/* Reset Button */}
        <button
          className="mas-flow-control-btn"
          onClick={onReset}
          title="Reset"
        >
          <RotateCcw size={18} />
        </button>

        {/* Speed Control */}
        <div className="mas-flow-speed-control">
          <Gauge size={18} className="mas-flow-speed-icon" />
          <div className="mas-flow-speed-buttons">
            {speedOptions.map((option) => (
              <button
                key={option.value}
                className={`mas-flow-speed-btn ${
                  speed === option.value ? 'mas-flow-speed-btn-active' : ''
                }`}
                onClick={() => onSpeedChange(option.value)}
                title={`Speed: ${option.label}`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
