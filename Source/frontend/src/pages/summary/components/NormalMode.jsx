import { useState, useEffect } from 'react';
import Select from 'react-select';
import { Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { submitSummary, parseSummaryResponse } from '../../../services/summaryService';
import { getCurrentUserId, getOrCreateSession } from '../../../services/sessionService';
import { handleAPIError } from '../../../services/errorHandler';
import SummaryResult from './SummaryResult';
import './SummaryModes.css';

const summaryOptions = [
  { value: 'abstractive', label: 'Tóm tắt diễn giải' },
  { value: 'extractive', label: 'Tóm tắt trích xuất' },
];

const gradeOptions = [
  { value: '1', label: 'Lớp 1' },
  { value: '2', label: 'Lớp 2' },
  { value: '3', label: 'Lớp 3' },
  { value: '4', label: 'Lớp 4' },
  { value: '5', label: 'Lớp 5' },
];

export default function NormalMode({ onSubmit, initialData }) {
  const [summaryType, setSummaryType] = useState(null);
  const [gradeLevel, setGradeLevel] = useState(null);
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [sessionId, setSessionId] = useState(null);

  // Load initial data if provided
  useEffect(() => {
    if (initialData) {
      setSummaryType(summaryOptions.find(opt => opt.value === initialData.summaryType) || null);
      setGradeLevel(gradeOptions.find(opt => opt.value === initialData.gradeLevel) || null);
      setText(initialData.text || '');
      if (initialData.result) {
        setResult(initialData.result);
      }
      if (initialData.sessionId) {
        setSessionId(initialData.sessionId);
      }
    }
  }, [initialData]);

  // Reset grade level when switching to extractive
  useEffect(() => {
    if (summaryType?.value === 'extractive') {
      setGradeLevel(null);
    }
  }, [summaryType]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!summaryType || !text.trim() || (summaryType?.value === 'abstractive' && !gradeLevel)) {
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const userId = getCurrentUserId();
      
      // Get or create session
      let currentSessionId = sessionId;
      if (!currentSessionId) {
        currentSessionId = await getOrCreateSession(userId);
        setSessionId(currentSessionId);
      }

      // Submit summary request
      const formData = {
        summaryType: summaryType.value,
        gradeLevel: summaryType.value === 'abstractive' ? gradeLevel?.value : null,
        text: text.trim(),
      };

      const response = await submitSummary({
        userId,
        sessionId: currentSessionId,
        conversationId: null,
        formData,
      });

      // Parse response
      const parsedResult = parseSummaryResponse(response);
      setResult(parsedResult);

      // Call parent onSubmit callback with full data
      if (onSubmit) {
        onSubmit({
          summaryType: formData.summaryType,
          gradeLevel: formData.gradeLevel,
          text: formData.text,
          result: parsedResult,
          sessionId: currentSessionId,
        });
      }
    } catch (err) {
      const userError = handleAPIError(err);
      setError(userError.message);
      console.error('Submit summary error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset grade level when switching to extractive
  useEffect(() => {
    if (summaryType?.value === 'extractive') {
      setGradeLevel(null);
    }
  }, [summaryType]);

  const customSelectStyles = {
    control: (provided, state) => ({
      ...provided,
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: state.isFocused ? '#3B82F6' : '#E5E7EB',
      borderRadius: '8px',
      boxShadow: state.isFocused ? '0 0 0 3px rgba(59, 130, 246, 0.1)' : 'none',
      minHeight: '44px',
      '&:hover': {
        borderColor: '#3B82F6',
      },
    }),
    option: (provided, state) => ({
      ...provided,
      backgroundColor: state.isSelected
        ? '#3B82F6'
        : state.isFocused
        ? '#EFF6FF'
        : 'white',
      color: state.isSelected ? 'white' : '#374151',
      '&:hover': {
        backgroundColor: state.isSelected ? '#3B82F6' : '#EFF6FF',
      },
    }),
  };

  const isAbstractive = summaryType?.value === 'abstractive';
  const isSubmitDisabled = !summaryType || !text.trim() || (isAbstractive && !gradeLevel) || isLoading;

  return (
    <div className="summary-mode-container">
      <form onSubmit={handleSubmit} className="summary-form">
        <div className="form-group">
          <label htmlFor="summary-type">Loại tóm tắt</label>
          <Select
            id="summary-type"
            options={summaryOptions}
            value={summaryType}
            onChange={setSummaryType}
            placeholder="Chọn loại tóm tắt..."
            styles={customSelectStyles}
            isSearchable={false}
            isDisabled={isLoading}
          />
        </div>

        {isAbstractive && (
          <div className="form-group fade-in">
            <label htmlFor="grade-level">Cấp lớp</label>
            <Select
              id="grade-level"
              options={gradeOptions}
              value={gradeLevel}
              onChange={setGradeLevel}
              placeholder="Chọn cấp lớp..."
              styles={customSelectStyles}
              isSearchable={false}
              isDisabled={isLoading}
            />
          </div>
        )}

        <div className="form-group">
          <label htmlFor="text-input">Văn bản cần tóm tắt</label>
          <textarea
            id="text-input"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Nhập văn bản cần tóm tắt..."
            rows={10}
            className="summary-textarea"
            disabled={isLoading}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="error-message">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Success Message */}
        {result && !error && (
          <div className="success-message">
            <CheckCircle2 size={18} />
            <span>Tóm tắt thành công!</span>
          </div>
        )}

        <button 
          type="submit" 
          className="summary-submit-btn" 
          disabled={isSubmitDisabled}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="spinning" />
              <span>Đang xử lý...</span>
            </>
          ) : (
            'Tóm tắt'
          )}
        </button>
      </form>

      {/* Result Display */}
      {result && <SummaryResult result={result} />}
    </div>
  );
}
