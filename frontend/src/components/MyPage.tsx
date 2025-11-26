type NavigateFunction = (page: string) => void;

interface MyPageProps {
  onNavigate: NavigateFunction;
}

export default function MyPage({ onNavigate }: MyPageProps) {
  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      <h1 className="mb-8">My 페이지</h1>

      <div className="grid grid-cols-3 gap-6">
        {/* Left Column - Profile */}
        <div className="col-span-1 space-y-6">
          {/* Profile Card */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="text-sm mb-4 pb-3 border-b border-gray-300">프로필</div>
            <div className="flex flex-col items-center mb-5">
              <div className="w-20 h-20 border border-gray-500 mb-3 flex items-center justify-center bg-gray-50">
                <span className="text-2xl text-gray-400">×</span>
              </div>
              <div className="text-sm mb-1">[사용자명]</div>
              <div className="text-xs text-gray-600">email@example.com</div>
            </div>

            <div className="space-y-2 mb-4">
              <div className="border border-gray-400 p-3 bg-gray-50">
                <div className="text-xs text-gray-600 mb-1">희망 직무</div>
                <div className="text-sm">백엔드 개발자</div>
              </div>
              <div className="border border-gray-400 p-3 bg-gray-50">
                <div className="text-xs text-gray-600 mb-1">경력</div>
                <div className="text-sm">신입</div>
              </div>
              <div className="border border-gray-400 p-3 bg-gray-50">
                <div className="text-xs text-gray-600 mb-1">희망 지역</div>
                <div className="text-sm">서울·경기</div>
              </div>
            </div>

            <button className="w-full py-2 border border-gray-900 bg-white text-sm">
              프로필 수정
            </button>
          </div>

          {/* Skills Card */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-300">
              <div className="text-sm">보유 기술 스택</div>
              <button className="text-xs border border-gray-900 px-2 py-1">편집</button>
            </div>
            <div className="flex flex-wrap gap-2 mb-4">
              {['React', 'TypeScript', 'Node.js', 'Python', 'Django', 'PostgreSQL'].map(
                (skill) => (
                  <span key={skill} className="px-2 py-1 border-2 border-gray-900 text-xs">
                    {skill}
                  </span>
                )
              )}
            </div>
            <button className="w-full py-2 border border-gray-900 bg-gray-900 text-white text-sm">
              + 스킬 추가
            </button>
          </div>

          {/* Career Path */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="text-sm mb-4 pb-3 border-b border-gray-300">커리어 로드맵</div>
            <div className="space-y-3">
              <div className="border-2 border-gray-900 bg-gray-900 text-white p-3">
                <div className="text-xs mb-1">현재</div>
                <div className="text-sm">주니어 개발자</div>
              </div>
              <div className="text-center text-gray-400">↓</div>
              <div className="border border-gray-400 bg-gray-50 p-3">
                <div className="text-xs mb-1">목표 1</div>
                <div className="text-sm">미들 개발자</div>
              </div>
              <div className="text-center text-gray-400">↓</div>
              <div className="border border-gray-400 bg-gray-50 p-3">
                <div className="text-xs mb-1">최종 목표</div>
                <div className="text-sm">시니어 개발자</div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Columns - Saved Items & Calendar */}
        <div className="col-span-2 space-y-6">
          {/* Saved Jobs */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-300">
              <div className="text-sm">찜한 채용공고</div>
              <button
                onClick={() => onNavigate('jobList')}
                className="text-xs border border-gray-900 px-3 py-1"
              >
                전체보기
              </button>
            </div>
            <div className="space-y-3">
              {[
                { company: '테크 회사 A', title: '백엔드 개발자', deadline: '2025.12.15', matching: 92 },
                { company: '스타트업 B', title: '풀스택 개발자', deadline: '2025.12.20', matching: 88 },
                { company: '기업 C', title: 'Python 개발자', deadline: '2025.12.25', matching: 85 },
              ].map((job, idx) => (
                <button
                  key={idx}
                  onClick={() => onNavigate('jobDetail')}
                  className="w-full border border-gray-400 bg-white hover:bg-gray-50 p-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-14 h-14 border border-gray-500 flex items-center justify-center bg-gray-50">
                      <span className="text-lg text-gray-400">×</span>
                    </div>
                    <div className="text-left">
                      <div className="text-xs text-gray-600 mb-1">[{job.company}]</div>
                      <div className="text-sm mb-1">{job.title}</div>
                      <div className="text-xs text-gray-600">마감: {job.deadline}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-1 border border-gray-900 text-xs">{job.matching}%</span>
                    <button className="w-8 h-8 border border-gray-900 flex items-center justify-center">
                      ♡
                    </button>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Saved Bootcamps */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-300">
              <div className="text-sm">찜한 부트캠프</div>
              <button
                onClick={() => onNavigate('bootcampList')}
                className="text-xs border border-gray-900 px-3 py-1"
              >
                전체보기
              </button>
            </div>
            <div className="grid grid-cols-2 gap-4">
              {[
                { institution: '코딩 부트캠프 A', course: 'DevOps 마스터', start: '2026.01.15' },
                { institution: '테크 아카데미 B', course: 'AWS 인프라', start: '2026.02.01' },
              ].map((bootcamp, idx) => (
                <button
                  key={idx}
                  onClick={() => onNavigate('bootcampDetail')}
                  className="border border-gray-400 bg-white hover:bg-gray-50 text-left"
                >
                  <div className="h-28 border-b border-gray-400 flex items-center justify-center bg-gray-50">
                    <span className="text-3xl text-gray-400">×</span>
                  </div>
                  <div className="p-4">
                    <div className="text-xs text-gray-600 mb-1">[{bootcamp.institution}]</div>
                    <div className="text-sm mb-2">{bootcamp.course}</div>
                    <div className="text-xs text-gray-600 mb-3">시작: {bootcamp.start}</div>
                    <div className="flex justify-end">
                      <button className="w-8 h-8 border border-gray-900 flex items-center justify-center">
                        ♡
                      </button>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Calendar */}
          <div className="border border-gray-400 bg-white p-6">
            <div className="text-sm mb-4 pb-3 border-b border-gray-300">일정 캘린더</div>

            {/* Calendar Grid */}
            <div className="border border-gray-400 mb-4">
              <div className="grid grid-cols-7 border-b border-gray-400 bg-gray-50">
                {['일', '월', '화', '수', '목', '금', '토'].map((day) => (
                  <div key={day} className="border-r border-gray-400 p-2 text-center text-xs last:border-r-0">
                    {day}
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-7">
                {Array.from({ length: 35 }).map((_, idx) => (
                  <div
                    key={idx}
                    className="border-r border-b border-gray-300 p-2 h-16 text-xs last:border-r-0"
                  >
                    <div className="text-gray-600">{idx + 1}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Upcoming Events */}
            <div>
              <div className="text-xs text-gray-600 mb-3">다가오는 일정</div>
              <div className="space-y-2">
                {[
                  { date: '12/15', title: '테크 회사 A 공고 마감', type: 'deadline' },
                  { date: '12/20', title: '스타트업 B 공고 마감', type: 'deadline' },
                  { date: '01/15', title: 'DevOps 과정 시작', type: 'course' },
                  { date: '02/01', title: 'AWS 과정 시작', type: 'course' },
                ].map((event, idx) => (
                  <div
                    key={idx}
                    className={`border p-3 flex items-center justify-between ${
                      event.type === 'deadline'
                        ? 'border-red-600 bg-red-50'
                        : 'border-blue-600 bg-blue-50'
                    }`}
                  >
                    <div>
                      <span className="text-xs">{event.date}</span>
                      <span className="mx-2">-</span>
                      <span className="text-sm">{event.title}</span>
                    </div>
                    <span
                      className={`px-2 py-1 border text-xs ${
                        event.type === 'deadline' ? 'border-red-600' : 'border-blue-600'
                      }`}
                    >
                      {event.type === 'deadline' ? '마감' : '시작'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
