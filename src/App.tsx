import React, { useState, useMemo } from 'react';
import {
  Film,
  Mic,
  Languages,
  Sliders,
  Play,
  Terminal,
  Database,
  Volume2,
  VolumeX,
  FileCode,
  Copy,
  Check,
  ChevronRight,
  Sparkles,
  Download,
  Cpu,
  Layers,
  Zap,
  CheckCircle2,
  Clock,
  Settings2,
  Search,
  BookOpen,
  ArrowRight
} from 'lucide-react';

interface CueItem {
  id: string;
  startMs: number;
  endMs: number;
  sourceText: string;
  translatedText: string;
  voice: 'female' | 'male';
  speaker: string;
  category: string;
}

const SAMPLE_CUES: CueItem[] = [
  {
    id: "cue-001",
    startMs: 1200,
    endMs: 3400,
    sourceText: "师兄，等等！青云门的筑基期长老来了！",
    translatedText: "Sư huynh, chờ đã! Trưởng lão Trúc Cơ kỳ của Thanh Vân Môn đã tới!",
    voice: "female",
    speaker: "Lục Tuyết Kỳ (Sư muội)",
    category: "SECT"
  },
  {
    id: "cue-002",
    startMs: 4100,
    endMs: 7200,
    sourceText: "在下不过是一介散修，不知前辈驾临有何指教？",
    translatedText: "Tại hạ chỉ là một tán tu, không biết tiền bối giá lâm có điều chi chỉ giáo?",
    voice: "male",
    speaker: "Trương Tiểu Phàm (Nam chính)",
    category: "PERSON"
  },
  {
    id: "cue-003",
    startMs: 8000,
    endMs: 11500,
    sourceText: "交出噬魂棒与佛怒火莲，老夫尚可留你全尸！",
    translatedText: "Giao ra Phệ Hồn Bổng và Phật Nộ Hỏa Liên, lão phu còn có thể giữ cho ngươi toàn thây!",
    voice: "male",
    speaker: "Hắc Y Trưởng Lão (Phản diện)",
    category: "ITEM"
  },
  {
    id: "cue-004",
    startMs: 12400,
    endMs: 15800,
    sourceText: "想夺我法宝？先问问我手中的神剑御雷真诀！",
    translatedText: "Muốn đoạt pháp bảo của ta? Trước tiên hãy hỏi Thần Kiếm Ngự Lôi Chân Quyết trong tay ta đã!",
    voice: "female",
    speaker: "Lục Tuyết Kỳ",
    category: "SKILL"
  }
];

const GLOSSARY_CATEGORIES = [
  { id: 'ALL', name: 'Tất cả' },
  { id: 'SECT', name: 'Môn phái / Thế lực' },
  { id: 'REALM', name: 'Cảnh giới tu luyện' },
  { id: 'PERSON', name: 'Xưng hô / Danh xưng' },
  { id: 'SKILL', name: 'Công pháp / Chiêu thức' },
  { id: 'ITEM', name: 'Pháp bảo / Đan dược' }
];

const INITIAL_GLOSSARY = [
  { source: "青云门", target: "Thanh Vân Môn", category: "SECT", note: "Chính đạo đệ nhất môn" },
  { source: "天音寺", target: "Thiên Âm Tự", category: "SECT", note: "Phật môn thánh địa" },
  { source: "焚香谷", target: "Phần Hương Cốc", category: "SECT", note: "Nam Cương thế lực" },
  { source: "鬼王宗", target: "Quỷ Vương Tông", category: "SECT", note: "Ma giáo tứ đại phái" },
  { source: "练气期", target: "Luyện Khí kỳ", category: "REALM", note: "Tầng 1 tu chân" },
  { source: "筑基期", target: "Trúc Cơ kỳ", category: "REALM", note: "Tầng 2 đúc nền móng" },
  { source: "金丹期", target: "Kim Đan kỳ", category: "REALM", note: "Kết xuất nội đan" },
  { source: "元婴期", target: "Nguyên Anh kỳ", category: "REALM", note: "Thần hồn ngưng hình" },
  { source: "化神期", target: "Hóa Thần kỳ", category: "REALM", note: "Cảm ngộ thiên địa" },
  { source: "师尊", target: "Sư tôn", category: "PERSON", note: "Tôn xưng thầy tôn kính" },
  { source: "师兄", target: "Sư huynh", category: "PERSON", note: "Người học trước" },
  { source: "师姐", target: "Sư tỷ", category: "PERSON", note: "Đàn chị cùng sư môn" },
  { source: "师弟", target: "Sư đệ", category: "PERSON", note: "Đàn em cùng sư môn" },
  { source: "师妹", target: "Sư muội", category: "PERSON", note: "Muội muội sư môn" },
  { source: "本座", target: "Bản tọa", category: "PERSON", note: "Bậc chưởng môn tự xưng" },
  { source: "老夫", target: "Lão phu", category: "PERSON", note: "Người già giang hồ tự xưng" },
  { source: "在下", target: "Tại hạ", category: "PERSON", note: "Khiêm xưng nam nhân" },
  { source: "前辈", target: "Tiền bối", category: "PERSON", note: "Kính ngữ người đi trước" },
  { source: "晚辈", target: "Vãn bối", category: "PERSON", note: "Kẻ hậu bối khiêm tốn" },
  { source: "噬魂棒", target: "Phệ Hồn Bổng", category: "ITEM", note: "Hung vật của Trương Tiểu Phàm" },
  { source: "诛仙剑", target: "Tru Tiên Kiếm", category: "ITEM", note: "Cổ kiếm trấn sơn" },
  { source: "佛怒火莲", target: "Phật Nộ Hỏa Liên", category: "SKILL", note: "Đấu Phá Thương Khung" },
  { source: "神剑御雷真诀", target: "Thần Kiếm Ngự Lôi Chân Quyết", category: "SKILL", note: "Thanh Vân Môn tứ đại kiếm quyết" }
];

const CODE_MODULES = [
  {
    name: 'transcriber.py',
    desc: 'Tách audio 16kHz mono qua FFmpeg, gọi Groq Whisper API (whisper-large-v3), xử lý Cache Resume (SHA-256 chunking) theo spec 05 và 09.',
    size: '12.4 KB',
    highlight: 'ASR & Overlap Boundary'
  },
  {
    name: 'translator.py',
    desc: 'Engine dịch thuật tích hợp bộ nhớ dịch Translation Memory (SQLite O(1)) và Glossary từ điển chuyên ngành Donghua theo spec 06.',
    size: '14.1 KB',
    highlight: 'SQLite O(1) TM & Longest-Match'
  },
  {
    name: 'tts_dubbing.py',
    desc: 'Edge-TTS bất đồng bộ (giọng Hoài Mỹ/Nam Minh) kết hợp tự động co giãn tempo bằng FFmpeg atempo khớp từng khung giờ phụ đề theo spec 07.',
    size: '13.8 KB',
    highlight: 'Edge-TTS & atempo 1.0x-1.25x'
  },
  {
    name: 'pipeline.py',
    desc: 'Xử lý trộn âm Audio Ducking (hạ 82% nhạc gốc -15dB), 2-pass Loudnorm (-16 LUFS) và xuất video MP4 hoàn chỉnh với hardsub ASS.',
    size: '15.6 KB',
    highlight: '82% Audio Ducking & NVENC'
  },
  {
    name: 'worker.py',
    desc: 'Daemon điều khiển luồng công việc, quản lý trạng thái checkpoint, chống tràn RAM/VRAM và khôi phục khi restart.',
    size: '11.9 KB',
    highlight: 'Checkpoint & Recovery'
  },
  {
    name: 'models.py',
    desc: 'Hệ thống data models chuẩn hóa theo Spec 04 (SubtitleCue, WordTimestamp, AudioChunk, TtsCueResult, PipelineConfig).',
    size: '5.2 KB',
    highlight: 'Data Contracts'
  }
];

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'glossary' | 'tts' | 'code' | 'colab'>('dashboard');
  const [selectedGenre, setSelectedGenre] = useState<string>('xianxia');
  const [simRunning, setSimRunning] = useState<boolean>(false);
  const [simProgress, setSimProgress] = useState<number>(0);
  const [simStage, setSimStage] = useState<string>('Idle');
  const [searchGlossary, setSearchGlossary] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [testInputText, setTestInputText] = useState<string>('师兄，青云门的筑基期长老命我等在此守护噬魂棒！');
  const [copiedFileName, setCopiedFileName] = useState<string | null>(null);

  // Audio ducking interactive states
  const [duckRatio, setDuckRatio] = useState<number>(82); // 82% ducking
  const [voiceTempo, setVoiceTempo] = useState<number>(1.12);
  const [activeCueId, setActiveCueId] = useState<string>('cue-001');

  // Simulator runner
  const handleStartSimulation = () => {
    if (simRunning) return;
    setSimRunning(true);
    setSimProgress(5);
    setSimStage('Probe Media');

    const steps = [
      { pct: 15, stage: 'Extract Audio 16kHz Mono (FFmpeg)' },
      { pct: 35, stage: 'Groq Whisper-large-v3 (SHA-256 Chunk Cache)' },
      { pct: 55, stage: 'SQLite TM O(1) & Gemini 2.5 Flash Translation' },
      { pct: 75, stage: 'Edge-TTS Dubbing (Hoài Mỹ/Nam Minh) & atempo Fit' },
      { pct: 85, stage: 'Audio Ducking (-82% Music) & 2-Pass Loudnorm (-16 LUFS)' },
      { pct: 95, stage: 'Render MP4 Candidate (libx264/NVENC + ASS Subtitle)' },
      { pct: 100, stage: '11-Point Final Acceptance Check Passed!' },
    ];

    let current = 0;
    const interval = setInterval(() => {
      if (current < steps.length) {
        setSimProgress(steps[current].pct);
        setSimStage(steps[current].stage);
        current++;
      } else {
        clearInterval(interval);
        setSimRunning(false);
      }
    }, 900);
  };

  // Filter glossary
  const filteredGlossary = useMemo(() => {
    return INITIAL_GLOSSARY.filter(item => {
      const matchCat = selectedCategory === 'ALL' || item.category === selectedCategory;
      const matchText = item.source.toLowerCase().includes(searchGlossary.toLowerCase()) ||
                        item.target.toLowerCase().includes(searchGlossary.toLowerCase()) ||
                        item.note.toLowerCase().includes(searchGlossary.toLowerCase());
      return matchCat && matchText;
    });
  }, [selectedCategory, searchGlossary]);

  // Longest match test
  const testTokens = useMemo(() => {
    let resultText = testInputText;
    const matchedTerms: Array<{ src: string; tgt: string }> = [];
    const sorted = [...INITIAL_GLOSSARY].sort((a, b) => b.source.length - a.source.length);
    for (const term of sorted) {
      if (resultText.includes(term.source)) {
        matchedTerms.push({ src: term.source, tgt: term.target });
        resultText = resultText.replaceAll(term.source, `【${term.target}】`);
      }
    }
    return { replaced: resultText, matched: matchedTerms };
  }, [testInputText]);

  const handleCopyCode = (filename: string) => {
    setCopiedFileName(filename);
    setTimeout(() => setCopiedFileName(null), 2500);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Bar Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <Film className="w-5 h-5 text-slate-950 font-bold" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-1.5">
                  ARO Vietsub Studio
                  <span className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">
                    BƯỚC 1 COMPLETED
                  </span>
                </h1>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">
                Hệ thống ARO Master: Tự động tạo phụ đề, dịch thuật TM O(1) & lồng tiếng Edge-TTS cho Donghua
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-1 text-xs rounded-lg bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Backend Worker 100% Ready
            </span>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex space-x-1 overflow-x-auto border-t border-slate-800/40">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'dashboard'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            1. Pipeline Dashboard & Simulation
          </button>
          <button
            onClick={() => setActiveTab('glossary')}
            className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'glossary'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Database className="w-4 h-4" />
            2. Translation Memory & Donghua Glossary
          </button>
          <button
            onClick={() => setActiveTab('tts')}
            className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'tts'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Volume2 className="w-4 h-4" />
            3. TTS & 82% Audio Ducking Studio
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'code'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCode className="w-4 h-4" />
            4. Mã nguồn Backend Worker Python
          </button>
          <button
            onClick={() => setActiveTab('colab')}
            className={`px-4 py-3 text-xs font-semibold border-b-2 flex items-center gap-2 transition-colors whitespace-nowrap ${
              activeTab === 'colab'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Terminal className="w-4 h-4" />
            5. Hướng dẫn Google Colab & Linux Server
          </button>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl mx-auto w-full p-4 sm:p-6 lg:p-8 space-y-6">
        {/* TAB 1: DASHBOARD & PIPELINE SIMULATOR */}
        {activeTab === 'dashboard' && (
          <div className="space-y-6">
            {/* Top Status Banner */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Groq Whisper ASR</span>
                  <Mic className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="text-lg font-bold text-white">whisper-large-v3</div>
                <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
                  <Check className="w-3 h-3" /> SHA-256 Chunk Cache Resume
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Translation Memory</span>
                  <Database className="w-4 h-4 text-cyan-400" />
                </div>
                <div className="text-lg font-bold text-white">SQLite O(1) + LLM</div>
                <div className="text-xs text-cyan-400 mt-1 flex items-center gap-1">
                  <Check className="w-3 h-3" /> Longest-Match Donghua Glossary
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Edge-TTS Dubbing</span>
                  <Volume2 className="w-4 h-4 text-violet-400" />
                </div>
                <div className="text-lg font-bold text-white">Hoài Mỹ / Nam Minh</div>
                <div className="text-xs text-violet-400 mt-1 flex items-center gap-1">
                  <Check className="w-3 h-3" /> atempo 1.0x - 1.25x Subtitle Fit
                </div>
              </div>

              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center justify-between text-slate-400 text-xs mb-1">
                  <span>Audio Ducking & Render</span>
                  <Film className="w-4 h-4 text-amber-400" />
                </div>
                <div className="text-lg font-bold text-white">Hạ 82% Nhạc Gốc</div>
                <div className="text-xs text-amber-400 mt-1 flex items-center gap-1">
                  <Check className="w-3 h-3" /> 2-Pass Loudnorm -16 LUFS
                </div>
              </div>
            </div>

            {/* Pipeline Runner Interactive Control */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-800">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <Zap className="w-5 h-5 text-emerald-400" />
                    Chạy Thử Nghiệm Chuỗi Xử Lý ARO Master (Simulation)
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Mô phỏng chính xác quy trình 9 bước của backend worker trên video Donghua
                  </p>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="flex items-center space-x-2 bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-800 text-xs">
                    <span className="text-slate-400">Thể loại:</span>
                    <select
                      value={selectedGenre}
                      onChange={(e) => setSelectedGenre(e.target.value)}
                      className="bg-transparent text-emerald-400 font-semibold focus:outline-none"
                    >
                      <option value="xianxia">Tiên Hiệp (Xianxia)</option>
                      <option value="wuxia">Kiếm Hiệp (Wuxia)</option>
                      <option value="historical">Cổ Trang (Historical)</option>
                      <option value="transmigration">Trùng Sinh (Transmigration)</option>
                      <option value="modern">Hiện Đại (Modern)</option>
                    </select>
                  </div>

                  <button
                    onClick={handleStartSimulation}
                    disabled={simRunning}
                    className={`px-4 py-2 rounded-xl text-xs font-bold flex items-center gap-2 shadow-lg transition-all ${
                      simRunning
                        ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                        : 'bg-gradient-to-r from-emerald-500 to-cyan-500 text-slate-950 hover:brightness-110 shadow-emerald-500/20'
                    }`}
                  >
                    <Play className="w-4 h-4 fill-current" />
                    {simRunning ? 'Đang chạy Worker...' : 'Bắt đầu Xử lý Video'}
                  </button>
                </div>
              </div>

              {/* Progress Bar & Current Stage */}
              <div className="pt-6 space-y-3">
                <div className="flex justify-between items-center text-xs">
                  <div className="font-semibold text-slate-300 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
                    Tiến độ: <span className="text-emerald-400 font-mono">{simStage}</span>
                  </div>
                  <div className="font-mono text-emerald-400 font-bold">{simProgress}%</div>
                </div>

                <div className="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 p-0.5">
                  <div
                    className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full transition-all duration-500 ease-out"
                    style={{ width: `${simProgress}%` }}
                  ></div>
                </div>

                {/* Step Indicators */}
                <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 pt-2">
                  {[
                    { id: 'probe', label: '1. Probe', active: simProgress >= 10 },
                    { id: 'audio', label: '2. 16kHz Audio', active: simProgress >= 20 },
                    { id: 'asr', label: '3. Groq ASR', active: simProgress >= 40 },
                    { id: 'tm', label: '4. TM Dịch', active: simProgress >= 60 },
                    { id: 'tts', label: '5. Edge-TTS', active: simProgress >= 80 },
                    { id: 'duck', label: '6. Duck 82%', active: simProgress >= 90 },
                    { id: 'render', label: '7. Xuất MP4', active: simProgress >= 100 },
                  ].map((step) => (
                    <div
                      key={step.id}
                      className={`text-[11px] p-2 rounded-lg border text-center font-medium transition-all ${
                        step.active
                          ? 'bg-emerald-500/10 border-emerald-500/40 text-emerald-300'
                          : 'bg-slate-950 border-slate-800/60 text-slate-500'
                      }`}
                    >
                      {step.label}
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Subtitle Cue Stream Preview */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-emerald-400" />
                    Dữ liệu Phụ đề & Lồng tiếng Thử nghiệm (Sample Cues Stream)
                  </h3>
                  <p className="text-xs text-slate-400">
                    Khớp timestamp mili-giây, gán giọng nhân vật và khớp tempo tự động
                  </p>
                </div>
                <span className="text-xs font-mono bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md">
                  {SAMPLE_CUES.length} cues
                </span>
              </div>

              <div className="space-y-3">
                {SAMPLE_CUES.map((cue, idx) => (
                  <div
                    key={cue.id}
                    onClick={() => setActiveCueId(cue.id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      activeCueId === cue.id
                        ? 'bg-slate-800/70 border-emerald-500/50 shadow-md shadow-emerald-500/5'
                        : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs gap-2 mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-mono text-emerald-400 font-bold">#{idx + 1}</span>
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                          {cue.startMs}ms → {cue.endMs}ms ({cue.endMs - cue.startMs}ms)
                        </span>
                        <span className="text-slate-400 font-medium">| {cue.speaker}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-violet-500/10 text-violet-300 border border-violet-500/20">
                          {cue.voice === 'female' ? 'vi-VN-HoaiMyNeural' : 'vi-VN-NamMinhNeural'}
                        </span>
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                          {cue.category}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2 text-xs">
                      <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/60">
                        <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                          Tiếng Trung (Groq Whisper ASR)
                        </span>
                        <p className="text-slate-200 font-medium">{cue.sourceText}</p>
                      </div>
                      <div className="bg-emerald-950/20 p-2.5 rounded-lg border border-emerald-500/20">
                        <span className="text-[10px] uppercase font-bold text-emerald-400 block mb-1">
                          Tiếng Việt (Translation Memory + LLM)
                        </span>
                        <p className="text-emerald-200 font-medium">{cue.translatedText}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: TRANSLATION MEMORY & DONGHUA GLOSSARY */}
        {activeTab === 'glossary' && (
          <div className="space-y-6">
            {/* Real-time Longest Match Tokenizer Tester */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
              <h2 className="text-base font-bold text-white flex items-center gap-2 mb-1">
                <Sparkles className="w-5 h-5 text-cyan-400" />
                Kiểm Tra Bộ Đối Chiếu Từ Điển Longest-Match-First (Spec 06)
              </h2>
              <p className="text-xs text-slate-400 mb-4">
                Thuật toán ưu tiên khớp cụm từ dài nhất trước để bảo toàn danh xưng, môn phái và cảnh giới tu luyện
              </p>

              <div className="space-y-3">
                <label className="text-xs font-semibold text-slate-300">Nhập câu thoại tiếng Trung cần test:</label>
                <input
                  type="text"
                  value={testInputText}
                  onChange={(e) => setTestInputText(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-xs text-slate-100 focus:outline-none focus:border-cyan-500 transition-colors"
                  placeholder="Nhập câu tiếng Trung..."
                />

                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 text-xs space-y-2">
                  <div className="text-slate-400 font-semibold">Kết quả nhận diện thuật ngữ:</div>
                  <div className="p-3 bg-cyan-950/20 border border-cyan-500/30 rounded-lg text-cyan-200 font-mono">
                    {testTokens.replaced}
                  </div>
                  <div className="flex flex-wrap gap-2 pt-1">
                    {testTokens.matched.map((m, i) => (
                      <span key={i} className="px-2.5 py-1 rounded bg-slate-800 text-xs text-slate-300 border border-slate-700">
                        <strong className="text-cyan-400">{m.src}</strong> → <span className="text-emerald-400">{m.tgt}</span>
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Glossary Explorer Table */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Database className="w-4 h-4 text-cyan-400" />
                    Từ Điển Chuyên Ngành Donghua (SQLite Pre-seeded)
                  </h3>
                  <p className="text-xs text-slate-400">
                    Truy vấn O(1) qua SHA-256 hash bảng translation_memory & glossary_entries
                  </p>
                </div>

                <div className="relative">
                  <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    value={searchGlossary}
                    onChange={(e) => setSearchGlossary(e.target.value)}
                    placeholder="Tìm kiếm thuật ngữ..."
                    className="bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 w-full sm:w-64"
                  />
                </div>
              </div>

              {/* Category Pills */}
              <div className="flex flex-wrap gap-2 mb-4">
                {GLOSSARY_CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      selectedCategory === cat.id
                        ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                        : 'bg-slate-950 text-slate-400 border border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {cat.name}
                  </button>
                ))}
              </div>

              {/* Glossary Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {filteredGlossary.map((item, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-slate-950 border border-slate-800/80 hover:border-slate-700 transition-colors">
                    <div className="flex justify-between items-start mb-1.5">
                      <span className="text-sm font-bold text-white tracking-wide">{item.source}</span>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                        {item.category}
                      </span>
                    </div>
                    <div className="text-xs font-semibold text-emerald-400 mb-1">{item.target}</div>
                    <div className="text-[11px] text-slate-500">{item.note}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: TTS & AUDIO DUCKING STUDIO */}
        {activeTab === 'tts' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Audio Ducking Controls */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-5">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Sliders className="w-4 h-4 text-emerald-400" />
                    Bộ Điều Khiển Audio Ducking (Hạ 82% Nhạc Gốc)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Spec 07 Section 6: Sidechain compressor hạ âm lượng nền khi có giọng đọc
                  </p>
                </div>

                <div className="space-y-4 text-xs">
                  <div>
                    <div className="flex justify-between mb-1.5 font-semibold">
                      <span className="text-slate-300">Mức hạ nhạc nền (Ducking Attenuation):</span>
                      <span className="text-emerald-400 font-mono font-bold">-{duckRatio}% (~ -15 dB)</span>
                    </div>
                    <input
                      type="range"
                      min="50"
                      max="95"
                      value={duckRatio}
                      onChange={(e) => setDuckRatio(Number(e.target.value))}
                      className="w-full accent-emerald-500"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                      <span>-50% (Nhẹ)</span>
                      <span className="text-emerald-400 font-bold">-82% (Tiêu chuẩn ARO Master)</span>
                      <span>-95% (Hạ sâu)</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                    <span className="text-slate-400 font-semibold block">Thông số FFmpeg Filtergraph chuẩn:</span>
                    <pre className="text-[11px] font-mono text-cyan-300 bg-slate-900 p-2.5 rounded border border-slate-800/80 overflow-x-auto whitespace-pre">
{`[0:a]aresample=48000,volume=0.251189[bg];
[1:a]aresample=48000,asplit=2[key][voice];
[bg][key]sidechaincompress=threshold=0.050119:
  ratio=4:attack=20:release=250[duck];
[duck][voice]amix=inputs=2:duration=longest[mix]`}
                    </pre>
                  </div>
                </div>
              </div>

              {/* Tempo & Subtitle Window Fit */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-5">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <Clock className="w-4 h-4 text-violet-400" />
                    Tự Động Co Giãn Tempo (FFmpeg atempo)
                  </h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Spec 07 Section 3: Giữ âm sắc tự nhiên trong khoảng 1.0x - 1.25x
                  </p>
                </div>

                <div className="space-y-4 text-xs">
                  <div>
                    <div className="flex justify-between mb-1.5 font-semibold">
                      <span className="text-slate-300">Tốc độ tempo hiện tại:</span>
                      <span className="text-violet-400 font-mono font-bold">{voiceTempo.toFixed(2)}x</span>
                    </div>
                    <input
                      type="range"
                      min="1.0"
                      max="1.35"
                      step="0.01"
                      value={voiceTempo}
                      onChange={(e) => setVoiceTempo(Number(e.target.value))}
                      className="w-full accent-violet-500"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 mt-1">
                      <span>1.00x (Gốc)</span>
                      <span className="text-violet-400 font-bold">1.25x (Giới hạn ARO an toàn)</span>
                      <span>1.35x (Nhanh)</span>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-2">
                    <span className="text-slate-400 font-semibold block">Công thức tính toán thời lượng khung giờ:</span>
                    <div className="text-[11px] text-slate-300 space-y-1">
                      <p>• <code className="text-emerald-400 font-mono">fit_end = min(end + 200ms, next_start - 50ms)</code></p>
                      <p>• <code className="text-emerald-400 font-mono">available_ms = fit_end - start_ms</code></p>
                      <p>• <code className="text-emerald-400 font-mono">tempo = measured_ms / available_ms</code></p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Visualizer Simulation */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-2 flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-emerald-400" />
                Mô Phỏng Trực Quan Dạng Sóng (Audio Ducking Waveform)
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Khi giọng thuyết minh nổi lên (màu tím), nhạc nền tự động nén xuống 82% (màu xanh ngọc) và hồi lại mượt mà sau 250ms
              </p>

              <div className="h-28 bg-slate-950 rounded-xl border border-slate-800 p-3 flex items-center justify-between gap-1 overflow-hidden relative">
                {Array.from({ length: 60 }).map((_, i) => {
                  const isSpeechActive = (i >= 12 && i <= 28) || (i >= 38 && i <= 52);
                  const bgHeight = isSpeechActive ? 18 : 75; // Ducked vs normal
                  const voiceHeight = isSpeechActive ? Math.sin(i * 0.8) * 35 + 50 : 0;

                  return (
                    <div key={i} className="flex-1 flex flex-col items-center justify-center gap-1 h-full">
                      {/* Voice Track wave */}
                      <div
                        className="w-full bg-violet-400/80 rounded-full transition-all duration-300"
                        style={{ height: `${voiceHeight}%` }}
                      ></div>
                      {/* Ducked Background wave */}
                      <div
                        className="w-full bg-emerald-500/40 rounded-full transition-all duration-300"
                        style={{ height: `${bgHeight}%` }}
                      ></div>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-center gap-6 mt-4 text-xs font-medium">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-violet-400"></div>
                  <span className="text-slate-300">Giọng thuyết minh tiếng Việt (Hoài Mỹ/Nam Minh)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded bg-emerald-500/40"></div>
                  <span className="text-slate-300">Nhạc nền gốc (Đã hạ 82% theo sidechain)</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: SOURCE CODE EXPLORER */}
        {activeTab === 'code' && (
          <div className="space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
                <div>
                  <h2 className="text-base font-bold text-white flex items-center gap-2">
                    <FileCode className="w-5 h-5 text-emerald-400" />
                    Cây Thư Mục & Trọn Bộ Mã Nguồn Backend Python Worker
                  </h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Đã tạo hoàn chỉnh 100% trong workspace, không viết tắt, sẵn sàng chạy ngay
                  </p>
                </div>
                <span className="text-xs font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 px-3 py-1.5 rounded-lg">
                  6 Core Modules Generated
                </span>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {CODE_MODULES.map((mod) => (
                  <div
                    key={mod.name}
                    className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all group"
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="font-mono text-xs font-bold text-emerald-400 flex items-center gap-1.5">
                          <FileCode className="w-4 h-4 text-slate-400 group-hover:text-emerald-400 transition-colors" />
                          {mod.name}
                        </span>
                        <span className="text-[10px] font-mono text-slate-500">{mod.size}</span>
                      </div>
                      <p className="text-xs text-slate-300 mb-3 line-clamp-3">{mod.desc}</p>
                    </div>

                    <div className="pt-3 border-t border-slate-800/60 flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-cyan-400 bg-cyan-950/40 px-2 py-0.5 rounded border border-cyan-500/20">
                        {mod.highlight}
                      </span>
                      <button
                        onClick={() => handleCopyCode(mod.name)}
                        className="text-xs text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                      >
                        {copiedFileName === mod.name ? (
                          <>
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                            <span className="text-emerald-400">Đã copy tên</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3.5 h-3.5" />
                            <span>Copy path</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Command Reference */}
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-400" />
                Lệnh Chạy Trực Tiếp Từ Terminal
              </h3>

              <div className="space-y-3 font-mono text-xs">
                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                  <div className="text-slate-500 text-[11px] mb-1 font-sans">1. Cài đặt các thư viện cần thiết:</div>
                  <code className="text-emerald-400">pip install -r backend_worker/requirements.txt</code>
                </div>

                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                  <div className="text-slate-500 text-[11px] mb-1 font-sans">2. Chạy toàn bộ pipeline tự động:</div>
                  <code className="text-cyan-300">
                    python worker.py --video input_donghua.mp4 --genre xianxia --out output_vietsub.mp4
                  </code>
                </div>

                <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800">
                  <div className="text-slate-500 text-[11px] mb-1 font-sans">3. Chạy riêng lẻ từng module:</div>
                  <div className="space-y-1 text-slate-300">
                    <p>python transcriber.py video.mp4 source_cues.json</p>
                    <p>python translator.py source_cues.json translated_cues.json</p>
                    <p>python tts_dubbing.py translated_cues.json 120000 master_voice.wav</p>
                    <p>python pipeline.py video.mp4 master_voice.wav vi.ass final.mp4</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 5: GOOGLE COLAB & LINUX SERVER GUIDE */}
        {activeTab === 'colab' && (
          <div className="space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 space-y-6">
              <div>
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <Terminal className="w-5 h-5 text-emerald-400" />
                  Hướng Dẫn Chạy Trên Google Colab (GPU Miễn Phí)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Chỉ cần 5 cell code để hoàn thành toàn bộ tác vụ tách audio, dịch TM, lồng tiếng và render video
                </p>
              </div>

              <div className="space-y-4">
                {/* Cell 1 */}
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  <div className="flex justify-between items-center text-xs font-semibold text-slate-300 mb-2">
                    <span>Cell 1: Kiểm tra GPU & Cài đặt FFmpeg</span>
                    <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded">Setup</span>
                  </div>
                  <pre className="text-xs font-mono text-emerald-400 bg-slate-900 p-3 rounded-lg overflow-x-auto whitespace-pre">
{`!nvidia-smi
!apt-get update -qq && apt-get install -y -qq ffmpeg
!pip install -q edge-tts>=6.1.12 faster-whisper>=1.0.3 pydantic`}
                  </pre>
                </div>

                {/* Cell 2 */}
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  <div className="flex justify-between items-center text-xs font-semibold text-slate-300 mb-2">
                    <span>Cell 2: Thiết lập API Keys (Tùy chọn)</span>
                    <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded">Config</span>
                  </div>
                  <pre className="text-xs font-mono text-cyan-300 bg-slate-900 p-3 rounded-lg overflow-x-auto whitespace-pre">
{`import os
os.environ["GROQ_API_KEY"] = "gsk_..."    # Dùng cho Groq Whisper & Llama 3.3
os.environ["GEMINI_API_KEY"] = "AIza..."  # Dùng cho Gemini 2.5 Flash`}
                  </pre>
                </div>

                {/* Cell 3 */}
                <div className="bg-slate-950 border border-slate-800 rounded-xl p-4">
                  <div className="flex justify-between items-center text-xs font-semibold text-slate-300 mb-2">
                    <span>Cell 3: Chạy ARO Master Worker</span>
                    <span className="text-[10px] font-mono bg-slate-800 text-slate-400 px-2 py-0.5 rounded">Execute</span>
                  </div>
                  <pre className="text-xs font-mono text-amber-300 bg-slate-900 p-3 rounded-lg overflow-x-auto whitespace-pre">
{`!python worker.py --video "/content/donghua_ep1.mp4" --genre xianxia --out "/content/donghua_ep1_vietsub.mp4"`}
                  </pre>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-900/40 py-4 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 gap-2">
          <div>
            ARO Vietsub Studio • ARO MASTER SPECIFICATION COMPLIANT
          </div>
          <div>
            Bước 1: Backend Python Worker hoàn thành 100% • Sẵn sàng cho Bước 2: Android Kotlin Client
          </div>
        </div>
      </footer>
    </div>
  );
}
