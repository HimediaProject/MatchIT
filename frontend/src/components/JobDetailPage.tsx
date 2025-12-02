type NavigateFunction = (page: any, params?: any) => void;

interface JobDetailPageProps {
  onNavigate: NavigateFunction;
}

export default function JobDetailPage({ onNavigate }: JobDetailPageProps) {
  return (
    <div className="max-w-[1100px] mx-auto px-6 py-8">
      {/* Header Section */}
      <div className="border border-gray-400 bg-white p-8 mb-6">
        <div className="flex items-start gap-6 mb-6">
          <div className="w-20 h-20 border border-gray-500 flex items-center justify-center bg-gray-50">
            <span className="text-2xl text-gray-400">×</span>
          </div>
          <div className="flex-1">
            <div className="text-sm text-gray-600 mb-2">[테크 스타트업 A]</div>
            <h1 className="mb-3">시니어 백엔드 개발자</h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>정규직</span>
              <span>·</span>
              <span>경력 3년 이상</span>
              <span>·</span>
              <span>서울 강남구</span>
            </div>
          </div>
          <button className="w-10 h-10 border border-gray-900 flex items-center justify-center">
            ♡
          </button>
        </div>

        {/* Key Info Grid */}
        <div className="grid grid-cols-4 gap-3">
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">연봉</div>
            <div className="text-sm">5,000~7,000만</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">근무형태</div>
            <div className="text-sm">정규직</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">마감일</div>
            <div className="text-sm">2025.12.31</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">채용인원</div>
            <div className="text-sm">0명</div>
          </div>
        </div>
      </div>

      {/* Matching Score */}
      <div className="border-2 border-gray-900 bg-gray-900 text-white p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>나와의 매칭률</div>
          <div className="text-3xl">85%</div>
        </div>
        <div className="h-3 bg-gray-700 border border-white">
          <div className="h-full bg-white" style={{ width: '85%' }}></div>
        </div>
      </div>

      {/* Required Skills */}
      <div className="border border-gray-400 bg-white p-6 mb-6">
        <div className="mb-4">
          <div className="text-sm mb-3">필수 기술</div>
          <div className="flex flex-wrap gap-2">
            {['React', 'TypeScript', 'Node.js', 'PostgreSQL'].map((skill) => (
              <span key={skill} className="px-3 py-2 border-2 border-gray-900 bg-white text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
        <div>
          <div className="text-sm mb-3">우대 기술</div>
          <div className="flex flex-wrap gap-2">
            {['Docker', 'Kubernetes', 'AWS', 'GraphQL'].map((skill) => (
              <span key={skill} className="px-3 py-2 border border-gray-500 bg-gray-50 text-sm">
                {skill}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Missing Skills Alert */}
      <div className="border-2 border-gray-900 bg-yellow-50 p-6 mb-6">
        <div className="text-sm mb-3">부족한 스킬</div>
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="px-3 py-2 border-2 border-red-600 bg-white text-sm">Docker</span>
          <span className="px-3 py-2 border-2 border-red-600 bg-white text-sm">Kubernetes</span>
        </div>
        <button
          onClick={() => onNavigate('bootcampList')}
          className="w-full py-3 border border-gray-900 bg-gray-900 text-white text-sm"
        >
          부족 스킬 학습 가능한 과정 찾기 →
        </button>
      </div>

      {/* Job Description */}
      <div className="border border-gray-400 bg-white p-6 mb-6">
        <div className="mb-4 pb-3 border-b border-gray-300">
          <div className="text-sm">상세 설명</div>
        </div>

        <div className="space-y-5">
          <div>
            <div className="text-sm mb-2">[ 주요 업무 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 업무 내용 라인 1<br />
              - 업무 내용 라인 2<br />
              - 업무 내용 라인 3
            </div>
          </div>

          <div>
            <div className="text-sm mb-2">[ 자격 요건 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 자격 요건 라인 1<br />
              - 자격 요건 라인 2
            </div>
          </div>

          <div>
            <div className="text-sm mb-2">[ 복지 및 혜택 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 복지 내용 라인 1<br />
              - 복지 내용 라인 2<br />
              - 복지 내용 라인 3
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button className="flex-1 py-3 border border-gray-900 bg-white text-sm">공유</button>
        <button className="flex-1 py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
          지원하기
        </button>
      </div>
    </div>
  );
}
