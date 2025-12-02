type NavigateFunction = (page: any, params?: any) => void;

interface HomePageProps {
  onNavigate: NavigateFunction;
  onAddToCompare?: (id: number, type?: 'job' | 'bootcamp') => void;
  selectedJobs?: number[];
  setSelectedJobs?: (jobs: number[]) => void;
  selectedBootcamps?: number[];
  setSelectedBootcamps?: (bootcamps: number[]) => void;
}

export default function HomePage({ onNavigate, onAddToCompare, selectedJobs = [], setSelectedJobs, selectedBootcamps = [], setSelectedBootcamps }: HomePageProps) {
  const categories = [
    { id: 1, name: '백엔드', icon: 'BE' },
    { id: 2, name: '프론트엔드', icon: 'FE' },
    { id: 3, name: '데이터', icon: 'DA' },
    { id: 4, name: 'AI/ML', icon: 'AI' },
    { id: 5, name: 'DevOps', icon: 'DO' },
    { id: 6, name: 'PM', icon: 'PM' },
  ];

  // local handler to ensure consistent behavior if parent doesn't provide onAddToCompare
  const handleAddToCompare = (id: number, type: 'job' | 'bootcamp' = 'job') => {
    if (type === 'bootcamp') {
      // Cannot mix with jobs
      if ((selectedJobs ?? []).length > 0) {
        window.alert('부트캠프와 채용공고는 섞어서 비교할 수 없습니다. 현재 채용공고가 선택되어 있습니다.');
        return;
      }

      if (onAddToCompare) {
        onAddToCompare(id, 'bootcamp');
        return;
      }

      if (selectedBootcamps && selectedBootcamps.includes(id)) {
        setSelectedBootcamps && setSelectedBootcamps(selectedBootcamps.filter((i) => i !== id));
        return;
      }

      if ((selectedBootcamps ?? []).length >= 3) {
        window.alert('최대 3개까지 비교할 수 있습니다.');
        return;
      }
      setSelectedBootcamps && setSelectedBootcamps([...(selectedBootcamps ?? []), id]);
    } else {
      // job
      if ((selectedBootcamps ?? []).length > 0) {
        window.alert('채용공고와 부트캠프는 섞어서 비교할 수 없습니다. 현재 부트캠프가 선택되어 있습니다.');
        return;
      }

      if (onAddToCompare) {
        onAddToCompare(id, 'job');
        return;
      }

      if (selectedJobs && selectedJobs.includes(id)) {
        setSelectedJobs && setSelectedJobs(selectedJobs.filter((i) => i !== id));
        return;
      }

      if ((selectedJobs ?? []).length >= 3) {
        window.alert('최대 3개까지 비교할 수 있습니다.');
        return;
      }
      setSelectedJobs && setSelectedJobs([...(selectedJobs ?? []), id]);
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-12">
      {/* Hero Section */}
      <div className="border border-gray-400 bg-white p-16 mb-12">
        <div className="text-center max-w-2xl mx-auto">
          <div className="mb-6">
            <div className="inline-block border border-gray-900 px-4 py-1 mb-4 text-sm">
              HERO
            </div>
          </div>
          <h1 className="mb-4">기술 스택 기반 커리어 매칭</h1>
          <p className="text-gray-600 mb-8">
            당신의 스킬에 맞는 채용공고와 성장 교육 과정을 추천합니다
          </p>
        </div>
      </div>

      {/* Category Selection */}
      <div className="mb-16">
        <div className="mb-6">
          <div className="text-sm text-gray-600 mb-2">관심 직무 선택</div>
        </div>
        <div className="grid grid-cols-6 gap-4">
          {categories.map((cat) => (
            <button
              key={cat.id}
              className="aspect-square border border-gray-400 bg-white hover:bg-gray-50 flex flex-col items-center justify-center gap-3"
            >
              <div className="w-16 h-16 border border-gray-500 flex items-center justify-center text-xs bg-gray-50">
                {cat.icon}
              </div>
              <div className="text-sm">{cat.name}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Tech Stack Input */}
      <div className="mb-16">
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">보유 기술 스택</div>
        </div>
        <div className="border border-gray-400 bg-white p-6">
          <input
            type="text"
            placeholder="기술 스택 입력 (예: React, Node.js, Python...)"
            className="w-full border border-gray-900 px-4 py-3 mb-4 bg-gray-50"
          />
          <div className="flex flex-wrap gap-2">
            {['React', 'TypeScript', 'Node.js', 'Python', 'AWS', 'Docker'].map((tech) => (
              <button key={tech} className="px-3 py-1 border border-gray-900 text-sm bg-white">
                {tech} ×
              </button>
            ))}
          </div>
        </div>
        <div className="text-center mt-6">
          <button className="px-20 py-3 border-2 border-gray-900 bg-gray-900 text-white hover:bg-gray-700">
            추천 받기
          </button>
        </div>
      </div>

      {/* Recommended Jobs Section */}
      <div className="mb-16">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="mb-1">추천 채용공고</div>
            <p className="text-sm text-gray-600">매칭률 높은 순</p>
          </div>
          <button
            onClick={() => onNavigate('jobList')}
            className="px-4 py-2 border border-gray-900 text-sm"
          >
            전체 보기 →
          </button>
        </div>
        <ul className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, idx) => (
            <li key={idx} className="border border-gray-400 bg-white p-5 text-left hover:bg-gray-50">
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate('jobDetail');
                }}
                className="block"
              >
                <div className="flex gap-4 mb-3">
                  <div className="w-14 h-14 border border-gray-500 flex items-center justify-center bg-gray-50 flex-shrink-0">
                    <span className="text-xl text-gray-400">×</span>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="text-xs text-gray-600 mb-1">[Company {idx + 1}]</div>
                    <div className="text-sm truncate">[Job Title Text]</div>
                  </div>
                </div>
                <div className="flex flex-wrap gap-1 mb-3">
                  <span className="text-xs border border-gray-500 px-2 py-0.5">React</span>
                  <span className="text-xs border border-gray-500 px-2 py-0.5">Node.js</span>
                </div>
                <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
                  <span>신입·경력</span>
                </div>
              </a>
              {/* 각 채용공고마다 비교함 담기 버튼 */}
              <div className="pt-2 border-t border-gray-200">
                <button
                  className="w-full border border-gray-900 px-2 py-1 text-xs hover:bg-gray-50"
                  onClick={() => handleAddToCompare(idx + 1, 'job')} // job ID 전달
                >
                  비교함 담기
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>

      {/* Recommended Bootcamps Section */}
      <div className="mb-16">
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="mb-1">추천 교육 과정</div>
            <p className="text-sm text-gray-600">스킬 향상을 위한 부트캠프</p>
          </div>
          <button
            onClick={() => onNavigate('bootcampList')}
            className="px-4 py-2 border border-gray-900 text-sm"
          >
            전체 보기 →
          </button>
        </div>
        <ul className="grid grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, idx) => (
            <li key={idx} className="border border-gray-400 bg-white hover:bg-gray-50">
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate('bootcampDetail');
                }}
                className="block"
              >
                <div className="h-32 border-b border-gray-400 flex items-center justify-center bg-gray-50">
                  <span className="text-3xl text-gray-400">×</span>
                </div>
                <div className="p-4">
                  <div className="text-xs text-gray-600 mb-1">[Institution {idx + 1}]</div>
                  <div className="text-sm mb-3">[Course Title]</div>
                  <div className="flex items-center gap-2 text-xs mb-3">
                    <span className="border border-gray-900 px-2 py-0.5">6개월</span>
                    <span className="text-gray-600">국비지원</span>
                  </div>
                </div>
              </a>
              {/* 각 교육 과정마다 비교함 담기 버튼 */}
              <div className="pt-2 border-t border-gray-200 px-4 pb-4">
                <button
                  className="w-full border border-gray-900 px-2 py-1 text-xs hover:bg-gray-50"
                  onClick={() => handleAddToCompare(idx + 1, 'bootcamp')} // bootcamp 타입 구분
                >
                  비교함 담기
                </button>
              </div>
            </li>
          ))}
        </ul>
      </div>
      {/* Right Slide Panel for Comparison - Jobs */}
      {selectedJobs && selectedJobs.length > 0 && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l-2 border-gray-900 shadow-xl p-6 flex flex-col">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm">비교 목록</div>
              <button
                onClick={() => setSelectedJobs && setSelectedJobs([])}
                className="text-xs text-gray-600 hover:underline"
              >
                전체 삭제
              </button>
            </div>
            <div className="text-xs text-gray-600">최대 3개까지 선택 가능</div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto">
            {selectedJobs.map((jobId) => (
              <div key={jobId} className="border border-gray-400 bg-gray-50 p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">[Company {jobId}]</div>
                    <div className="text-sm">Job #{jobId}</div>
                  </div>
                  <button
                    onClick={() => setSelectedJobs && setSelectedJobs(selectedJobs.filter((id) => id !== jobId))}
                    className="w-6 h-6 border border-gray-900 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
                <div className="text-xs text-gray-600">--</div>
              </div>
            ))}
          </div>

          <button
            onClick={() => onNavigate('jobCompare')}
            disabled={selectedJobs.length < 2}
            className={`w-full py-3 border-2 border-gray-900 text-sm mt-4 ${
              selectedJobs.length >= 2
                ? 'bg-gray-900 text-white hover:bg-gray-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            비교하기 ({selectedJobs.length}/3)
          </button>
        </div>
      )}

      {/* Right Slide Panel for Comparison - Bootcamps */}
      {selectedBootcamps && selectedBootcamps.length > 0 && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l-2 border-gray-900 shadow-xl p-6 flex flex-col">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm">비교 목록</div>
              <button
                onClick={() => setSelectedBootcamps && setSelectedBootcamps([])}
                className="text-xs text-gray-600 hover:underline"
              >
                전체 삭제
              </button>
            </div>
            <div className="text-xs text-gray-600">최대 3개까지 선택 가능</div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto">
            {selectedBootcamps.map((bootcampId) => (
              <div key={bootcampId} className="border border-gray-400 bg-gray-50 p-3">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">[Institution {bootcampId}]</div>
                    <div className="text-sm">Course #{bootcampId}</div>
                  </div>
                  <button
                    onClick={() => setSelectedBootcamps && setSelectedBootcamps(selectedBootcamps.filter((id) => id !== bootcampId))}
                    className="w-6 h-6 border border-gray-900 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
                <div className="text-xs text-gray-600">--</div>
              </div>
            ))}
          </div>

          <button
            onClick={() => onNavigate('bootcampCompare')}
            disabled={selectedBootcamps.length < 2}
            className={`w-full py-3 border-2 border-gray-900 text-sm mt-4 ${
              selectedBootcamps.length >= 2
                ? 'bg-gray-900 text-white hover:bg-gray-700'
                : 'bg-gray-200 text-gray-500 cursor-not-allowed'
            }`}
          >
            비교하기 ({selectedBootcamps.length}/3)
          </button>
        </div>
      )}
    </div>
  );
}
