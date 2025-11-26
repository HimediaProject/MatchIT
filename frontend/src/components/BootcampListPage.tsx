type NavigateFunction = (page: string) => void;

interface BootcampListPageProps {
  onNavigate: NavigateFunction;
  selectedBootcamps: number[];
  setSelectedBootcamps: (bootcamps: number[]) => void;
}

export default function BootcampListPage({
  onNavigate,
  selectedBootcamps,
  setSelectedBootcamps,
}: BootcampListPageProps) {
  const toggleBootcampSelection = (bootcampId: number) => {
    if (selectedBootcamps.includes(bootcampId)) {
      setSelectedBootcamps(selectedBootcamps.filter((id) => id !== bootcampId));
    } else if (selectedBootcamps.length < 3) {
      setSelectedBootcamps([...selectedBootcamps, bootcampId]);
    }
  };

  const bootcamps = Array.from({ length: 12 }).map((_, idx) => ({
    id: idx + 1,
    institution: `교육기관 ${idx + 1}`,
    course: `${['백엔드', '프론트엔드', 'DevOps'][idx % 3]} 개발자 양성 과정`,
    duration: `${4 + (idx % 3)}개월`,
    price: idx % 3 === 0 ? '국비지원' : `${300 + idx * 30}만원`,
    mode: idx % 2 === 0 ? '온라인' : '오프라인',
  }));

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="mb-2">부트캠프 & 교육 과정</h1>
        <p className="text-sm text-gray-600">총 456개 과정</p>
      </div>

      {/* Top Filter Bar - Horizontal Layout */}
      <div className="border border-gray-400 bg-white p-4 mb-6">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">정렬:</span>
            <select className="border border-gray-900 px-3 py-1 text-sm bg-white">
              <option>추천순</option>
              <option>최신순</option>
              <option>가격순</option>
            </select>
          </div>
          <div className="h-6 w-px bg-gray-300"></div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">직무:</span>
            <select className="border border-gray-900 px-3 py-1 text-sm bg-white">
              <option>전체</option>
              <option>백엔드</option>
              <option>프론트엔드</option>
            </select>
          </div>
          <div className="h-6 w-px bg-gray-300"></div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">국비지원:</span>
            <label className="flex items-center gap-1 text-sm">
              <input type="checkbox" className="w-3 h-3" />
              국비지원만
            </label>
          </div>
          <div className="h-6 w-px bg-gray-300"></div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-600">수강방식:</span>
            <select className="border border-gray-900 px-3 py-1 text-sm bg-white">
              <option>전체</option>
              <option>온라인</option>
              <option>오프라인</option>
            </select>
          </div>
        </div>
      </div>

      {/* Bootcamp Grid - 2 Columns with Left Image Layout */}
      <div className="grid grid-cols-2 gap-4 mb-8">
        {bootcamps.map((bootcamp) => (
          <div key={bootcamp.id} className="border border-gray-400 bg-white hover:bg-gray-50">
            <div className="flex">
              {/* Left: Thumbnail */}
              <div className="w-48 border-r border-gray-400 flex items-center justify-center bg-gray-50 flex-shrink-0">
                <span className="text-4xl text-gray-400">×</span>
              </div>

              {/* Right: Info */}
              <div className="flex-1 p-5">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="text-xs text-gray-600 mb-1">[{bootcamp.institution}]</div>
                    <div className="text-sm mb-2">{bootcamp.course}</div>
                  </div>
                  <button
                    onClick={() => toggleBootcampSelection(bootcamp.id)}
                    className={`w-8 h-8 border flex items-center justify-center flex-shrink-0 ml-2 ${
                      selectedBootcamps.includes(bootcamp.id)
                        ? 'border-gray-900 bg-gray-900 text-white'
                        : 'border-gray-500 bg-white'
                    }`}
                  >
                    +
                  </button>
                </div>

                <div className="flex items-center gap-2 mb-3">
                  <span className="px-2 py-1 border border-gray-900 text-xs">{bootcamp.price}</span>
                  <span className="text-xs text-gray-600">{bootcamp.duration}</span>
                  <span className="px-2 py-1 border border-gray-500 text-xs bg-gray-50">
                    {bootcamp.mode}
                  </span>
                </div>

                <div className="flex flex-wrap gap-1 mb-4">
                  <span className="text-xs border border-gray-500 px-2 py-0.5">Python</span>
                  <span className="text-xs border border-gray-500 px-2 py-0.5">Django</span>
                  <span className="text-xs border border-gray-500 px-2 py-0.5">React</span>
                </div>

                <button
                  onClick={() => onNavigate('bootcampDetail')}
                  className="px-4 py-2 border border-gray-900 text-xs hover:bg-gray-100"
                >
                  상세보기
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex justify-center gap-2">
        <button className="w-8 h-8 border border-gray-900 bg-white">←</button>
        {[1, 2, 3, 4, 5].map((page) => (
          <button
            key={page}
            className={`w-8 h-8 border border-gray-900 ${
              page === 1 ? 'bg-gray-900 text-white' : 'bg-white'
            }`}
          >
            {page}
          </button>
        ))}
        <button className="w-8 h-8 border border-gray-900 bg-white">→</button>
      </div>

      {/* Right Slide Panel for Comparison */}
      {selectedBootcamps.length > 0 && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l-2 border-gray-900 shadow-xl p-6 flex flex-col">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm">비교 목록</div>
              <button
                onClick={() => setSelectedBootcamps([])}
                className="text-xs text-gray-600 hover:underline"
              >
                전체 삭제
              </button>
            </div>
            <div className="text-xs text-gray-600">최대 3개까지 선택 가능</div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto">
            {selectedBootcamps.map((bootcampId) => {
              const bootcamp = bootcamps.find((b) => b.id === bootcampId);
              return (
                <div key={bootcampId} className="border border-gray-400 bg-gray-50 p-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="text-xs text-gray-600 mb-1">[{bootcamp?.institution}]</div>
                      <div className="text-sm">{bootcamp?.course}</div>
                    </div>
                    <button
                      onClick={() => toggleBootcampSelection(bootcampId)}
                      className="w-6 h-6 border border-gray-900 flex items-center justify-center text-xs"
                    >
                      ×
                    </button>
                  </div>
                  <div className="text-xs text-gray-600">
                    {bootcamp?.price} · {bootcamp?.duration}
                  </div>
                </div>
              );
            })}
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
