import { useEffect, useState } from 'react';
type NavigateFunction = (page: any, params?: any) => void;

interface JobListPageProps {
  onNavigate: NavigateFunction;
  selectedJobs: number[];
  setSelectedJobs: (jobs: number[]) => void;
  onAddToCompare?: (id: number, type?: 'job' | 'bootcamp') => void;
  selectedBootcamps?: number[];
}

export default function JobListPage({ onNavigate, selectedJobs, setSelectedJobs, onAddToCompare, selectedBootcamps = [] }: JobListPageProps) {
  const [jobs, setJobs] = useState<any[]>([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/jobs')
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .catch((e) => console.error('failed to fetch jobs', e));
  }, []);

  const toggleJobSelection = (jobId: number) => {
    if (selectedJobs.includes(jobId)) {
      setSelectedJobs(selectedJobs.filter((id) => id !== jobId));
      return;
    }

    // Prevent mixing with bootcamp selections
    if ((selectedBootcamps ?? []).length > 0) {
      window.alert('채용공고와 부트캠프는 섞어서 비교할 수 없습니다. 현재 부트캠프가 선택되어 있습니다.');
      return;
    }

    // Add either via global handler or local
    if (onAddToCompare) {
      onAddToCompare(jobId, 'job');
      return;
    }

    if (selectedJobs.length < 3) {
      setSelectedJobs([...selectedJobs, jobId]);
    } else {
      window.alert('최대 3개까지 비교할 수 있습니다.');
    }
  };

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="mb-2">채용공고</h1>
        <p className="text-sm text-gray-600">총 1,234개 공고</p>
      </div>

      <div className="flex gap-6">
        {/* Left Filter Panel */}
        <div className="w-64 flex-shrink-0">
          <div className="border border-gray-400 bg-white p-5">
            <div className="mb-5 pb-3 border-b border-gray-300">
              <div className="text-sm mb-3">필터</div>
            </div>

            <div className="mb-5">
              <div className="text-xs text-gray-600 mb-2">직무</div>
              <div className="space-y-1">
                {['백엔드', '프론트엔드', '풀스택', 'DevOps'].map((job) => (
                  <label key={job} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="w-3 h-3" />
                    {job}
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-5">
              <div className="text-xs text-gray-600 mb-2">경력</div>
              <div className="space-y-1">
                {['신입', '경력 1-3년', '경력 3-5년', '경력 5년+'].map((exp) => (
                  <label key={exp} className="flex items-center gap-2 text-sm">
                    <input type="checkbox" className="w-3 h-3" />
                    {exp}
                  </label>
                ))}
              </div>
            </div>

            <div className="mb-5">
              <div className="text-xs text-gray-600 mb-2">지역</div>
              <select className="w-full border border-gray-900 p-2 text-sm bg-white">
                <option>전체</option>
                <option>서울</option>
                <option>경기</option>
              </select>
            </div>

            <div className="mb-5">
              <div className="text-xs text-gray-600 mb-2">기술 스택</div>
              <input
                type="text"
                placeholder="검색..."
                className="w-full border border-gray-900 p-2 text-sm bg-gray-50"
              />
            </div>

            <button className="w-full py-2 border border-gray-900 bg-gray-900 text-white text-sm">
              적용
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1">
          {/* Sort Options */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex gap-2">
              <button className="px-3 py-1 border border-gray-900 bg-gray-900 text-white text-sm">
                매칭순
              </button>
              <button className="px-3 py-1 border border-gray-900 bg-white text-sm">최신순</button>
              <button className="px-3 py-1 border border-gray-900 bg-white text-sm">마감순</button>
            </div>
          </div>

          {/* Job Grid */}
          <div className="grid grid-cols-3 gap-4 mb-8">
              {jobs.map((job) => (
                <div key={job.PostID ?? job.id} className="border border-gray-400 bg-white hover:bg-gray-50">
                {/* Card Header with Compare Button */}
                <div className="p-4 border-b border-gray-300 flex items-start justify-between">
                  <div className="flex gap-3 flex-1">
                    <div className="w-12 h-12 border border-gray-500 flex items-center justify-center bg-gray-50 flex-shrink-0">
                      <span className="text-lg text-gray-400">×</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs text-gray-600 mb-1">[{job.company}]</div>
                      <div className="text-sm truncate">{job.title}</div>
                    </div>
                  </div>
                  <button
                    onClick={() => toggleJobSelection(job.PostID ?? job.id)}
                    className={`w-8 h-8 border flex items-center justify-center flex-shrink-0 ${
                      selectedJobs.includes(job.PostID ?? job.id)
                        ? 'border-gray-900 bg-gray-900 text-white'
                        : 'border-gray-500 bg-white'
                    }`}
                  >
                    +
                  </button>
                </div>

                {/* Card Body */}
                <div className="p-4">
                  <div className="flex flex-wrap gap-1 mb-3">
                    <span className="text-xs border border-gray-500 px-2 py-0.5">React</span>
                    <span className="text-xs border border-gray-500 px-2 py-0.5">Node.js</span>
                    <span className="text-xs border border-gray-500 px-2 py-0.5">AWS</span>
                  </div>
                  <div className="flex items-center justify-between text-xs text-gray-600 mb-3">
                    <span>{(job.ExperienceRequirement ?? job.exp) || ''}</span>
                    <span>{job.Location ?? job.location}</span>
                    <span>{job.EmploymentType ?? job.type}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-xs border border-gray-900 px-2 py-1">
                      매칭 {job.matching ?? 0}%
                    </span>
                    <button
                      onClick={() => onNavigate('jobDetail')}
                      className="px-3 py-1 border border-gray-900 text-xs hover:bg-gray-100"
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
        </div>
      </div>

      {/* Right Slide Panel for Comparison */}
      {selectedJobs.length > 0 && (
        <div className="fixed right-0 top-0 h-full w-80 bg-white border-l-2 border-gray-900 shadow-xl p-6 flex flex-col">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <div className="text-sm">비교 목록</div>
              <button
                onClick={() => setSelectedJobs([])}
                className="text-xs text-gray-600 hover:underline"
              >
                전체 삭제
              </button>
            </div>
            <div className="text-xs text-gray-600">최대 3개까지 선택 가능</div>
          </div>

          <div className="flex-1 space-y-3 overflow-y-auto">
            {selectedJobs.map((jobId) => {
              const job = jobs.find((j) => j.PostID === jobId || j.id === jobId);
              return (
                <div key={jobId} className="border border-gray-400 bg-gray-50 p-3">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="text-xs text-gray-600 mb-1">[{job?.company}]</div>
                      <div className="text-sm">{job?.title}</div>
                    </div>
                    <button
                      onClick={() => toggleJobSelection(jobId)}
                      className="w-6 h-6 border border-gray-900 flex items-center justify-center text-xs"
                    >
                      ×
                    </button>
                  </div>
                  <div className="text-xs text-gray-600">매칭 {job?.matching ?? 0}%</div>
                </div>
              );
            })}
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
    </div>
  );
}
