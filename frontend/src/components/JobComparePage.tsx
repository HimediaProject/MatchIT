type NavigateFunction = (page: string) => void;

interface JobComparePageProps {
  onNavigate: NavigateFunction;
  selectedJobs: number[];
}

export default function JobComparePage({ onNavigate, selectedJobs }: JobComparePageProps) {
  const jobs = [
    {
      id: 1,
      company: '테크 스타트업 A',
      title: '시니어 백엔드 개발자',
      matching: 92,
      salary: '5,000~7,000만',
      exp: '경력 3년 이상',
      location: '서울 강남구',
      type: '정규직',
      deadline: '2025.12.31',
      requiredSkills: ['React', 'Node.js', 'PostgreSQL', 'TypeScript'],
      preferredSkills: ['Docker', 'AWS', 'GraphQL'],
      benefits: ['재택근무', '건강검진', '교육비 지원', '점심 제공'],
    },
    {
      id: 2,
      company: '글로벌 IT 기업 B',
      title: '백엔드 개발자',
      matching: 88,
      salary: '4,500~6,000만',
      exp: '경력 2년 이상',
      location: '서울 판교',
      type: '정규직',
      deadline: '2025.12.25',
      requiredSkills: ['Java', 'Spring', 'MySQL', 'Git'],
      preferredSkills: ['Kubernetes', 'Redis', 'Jenkins'],
      benefits: ['유연근무', '스톡옵션', '간식 무제한', '도서 구입비'],
    },
    {
      id: 3,
      company: '핀테크 스타트업 C',
      title: '주니어 백엔드 개발자',
      matching: 85,
      salary: '4,000~5,000만',
      exp: '신입~경력 2년',
      location: '서울 서초구',
      type: '정규직',
      deadline: '2025.12.20',
      requiredSkills: ['Python', 'Django', 'PostgreSQL'],
      preferredSkills: ['Docker', 'AWS', 'CI/CD'],
      benefits: ['재택근무', '점심 제공', '커피&간식', '컨퍼런스 참가 지원'],
    },
  ].filter((job) => selectedJobs.includes(job.id));

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      {/* Back Button */}
      <button
        onClick={() => onNavigate('jobList')}
        className="mb-6 px-4 py-2 border border-gray-900 text-sm"
      >
        ← 목록으로
      </button>

      <h1 className="mb-8">채용공고 비교</h1>

      {/* Summary Headers - Horizontal Scroll Cards */}
      <div className="flex gap-4 mb-8 overflow-x-auto pb-4">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="min-w-[320px] border border-gray-400 bg-white p-5 flex-shrink-0"
          >
            <div className="flex items-start gap-3 mb-3">
              <div className="w-14 h-14 border border-gray-500 flex items-center justify-center bg-gray-50">
                <span className="text-lg text-gray-400">×</span>
              </div>
              <div className="flex-1">
                <div className="text-xs text-gray-600 mb-1">[{job.company}]</div>
                <div className="text-sm mb-2">{job.title}</div>
                <div className="inline-block px-2 py-1 border border-gray-900 text-xs">
                  매칭 {job.matching}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Sections */}
      <div className="space-y-6">
        {/* Basic Info Comparison */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">기본 정보 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {jobs.map((job) => (
              <div key={job.id} className="min-w-[320px] flex-shrink-0 space-y-2">
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">연봉</div>
                  <div className="text-sm">{job.salary}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">경력</div>
                  <div className="text-sm">{job.exp}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">근무지</div>
                  <div className="text-sm">{job.location}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">고용형태</div>
                  <div className="text-sm">{job.type}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">마감일</div>
                  <div className="text-sm">{job.deadline}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skills Comparison */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">기술 스택 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {jobs.map((job) => (
              <div key={job.id} className="min-w-[320px] flex-shrink-0">
                <div className="mb-4">
                  <div className="text-xs text-gray-600 mb-2">필수 기술</div>
                  <div className="flex flex-wrap gap-2">
                    {job.requiredSkills.map((skill) => (
                      <span key={skill} className="px-2 py-1 border-2 border-gray-900 text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-600 mt-2">총 {job.requiredSkills.length}개</div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-2">우대 기술</div>
                  <div className="flex flex-wrap gap-2">
                    {job.preferredSkills.map((skill) => (
                      <span key={skill} className="px-2 py-1 border border-gray-500 text-xs bg-gray-50">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-600 mt-2">총 {job.preferredSkills.length}개</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Benefits Comparison */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">복지 및 혜택 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {jobs.map((job) => (
              <div key={job.id} className="min-w-[320px] flex-shrink-0">
                <div className="space-y-2">
                  {job.benefits.map((benefit, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <span className="w-4 h-4 border border-gray-900 flex items-center justify-center text-xs">
                        ✓
                      </span>
                      <span>{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Company Info */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">회사 정보</div>
          <div className="flex gap-4 overflow-x-auto">
            {jobs.map((job) => (
              <div key={job.id} className="min-w-[320px] flex-shrink-0">
                <div className="border border-gray-400 p-4 bg-gray-50">
                  <div className="text-sm mb-2">{job.company}</div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>업종: IT 서비스</div>
                    <div>설립: 2015년</div>
                    <div>직원수: 150명</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-8">
        {jobs.map((job) => (
          <div key={job.id} className="flex-1">
            <button className="w-full py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
              {job.company} 지원하기
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
