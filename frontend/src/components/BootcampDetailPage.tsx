type NavigateFunction = (page: any, params?: any) => void;

interface BootcampDetailPageProps {
  onNavigate: NavigateFunction;
}

export default function BootcampDetailPage({ onNavigate }: BootcampDetailPageProps) {
  return (
    <div className="max-w-[1100px] mx-auto px-6 py-8">
      {/* Header Section */}
      <div className="border border-gray-400 bg-white p-8 mb-6">
        <div className="flex items-start justify-between mb-6">
          <div>
            <div className="text-sm text-gray-600 mb-2">[코딩 부트캠프 A]</div>
            <h1 className="mb-4">백엔드 개발자 양성 과정</h1>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <span>6개월 과정</span>
              <span>·</span>
              <span>오프라인</span>
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
            <div className="text-xs text-gray-600 mb-1">가격</div>
            <div className="text-sm">450만원</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">국비지원</div>
            <div className="text-sm">가능</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">시작일</div>
            <div className="text-sm">2026.02.01</div>
          </div>
          <div className="border border-gray-400 p-3 bg-gray-50">
            <div className="text-xs text-gray-600 mb-1">모집인원</div>
            <div className="text-sm">30명</div>
          </div>
        </div>
      </div>

      {/* Course Image */}
      <div className="border border-gray-400 bg-white mb-6">
        <div className="h-64 border-b border-gray-400 flex items-center justify-center bg-gray-50">
          <span className="text-6xl text-gray-400">×</span>
        </div>
      </div>

      {/* Learning Skills */}
      <div className="border border-gray-400 bg-white p-6 mb-6">
        <div className="text-sm mb-4">배우는 기술 스택</div>
        <div className="flex flex-wrap gap-2">
          {['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS', 'Git', 'REST API', 'Agile'].map(
            (skill) => (
              <span key={skill} className="px-3 py-2 border-2 border-gray-900 bg-white text-sm">
                {skill}
              </span>
            )
          )}
        </div>
      </div>

      {/* Curriculum */}
      <div className="border border-gray-400 bg-white p-6 mb-6">
        <div className="text-sm mb-4 pb-3 border-b border-gray-300">커리큘럼</div>
        <div className="space-y-3">
          {[
            { week: 'Week 1-4', title: 'Python 기초', topics: ['변수와 자료형', '함수', 'OOP'] },
            { week: 'Week 5-8', title: 'Django Framework', topics: ['MVC 패턴', 'ORM', 'REST API'] },
            { week: 'Week 9-12', title: 'Database', topics: ['SQL', 'PostgreSQL', '최적화'] },
            { week: 'Week 13-16', title: 'DevOps', topics: ['Docker', 'AWS', 'CI/CD'] },
            { week: 'Week 17-24', title: '프로젝트', topics: ['팀 프로젝트', '포트폴리오'] },
          ].map((module, idx) => (
            <div key={idx} className="border border-gray-400 p-4 bg-gray-50">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <span className="text-xs text-gray-600">{module.week}</span>
                  <div className="text-sm">{module.title}</div>
                </div>
                <button className="text-xs text-gray-600">▼</button>
              </div>
              <div className="flex gap-2 mt-2">
                {module.topics.map((topic) => (
                  <span key={topic} className="text-xs border border-gray-500 px-2 py-0.5 bg-white">
                    {topic}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Related Jobs Section */}
      <div className="border-2 border-gray-900 bg-gray-900 text-white p-6 mb-6">
        <div className="text-sm mb-4 pb-3 border-b border-white">
          수료 후 지원 가능한 채용공고
        </div>
        <div className="space-y-2">
          {[
            { company: '테크 기업 A', title: '백엔드 개발자', matching: 92 },
            { company: '스타트업 B', title: 'Django 개발자', matching: 88 },
            { company: '회사 C', title: 'Python 개발자', matching: 85 },
            { company: '기업 D', title: '서버 개발자', matching: 82 },
            { company: '테크 E', title: '주니어 백엔드', matching: 80 },
          ].map((job, idx) => (
            <button
              key={idx}
              onClick={() => onNavigate('jobDetail')}
              className="w-full border border-white bg-gray-800 hover:bg-gray-700 p-3 flex items-center justify-between text-left"
            >
              <div>
                <div className="text-xs text-gray-300 mb-1">[{job.company}]</div>
                <div className="text-sm">{job.title}</div>
              </div>
              <span className="px-2 py-1 border border-white text-xs">{job.matching}%</span>
            </button>
          ))}
        </div>
        <button
          onClick={() => onNavigate('jobList')}
          className="w-full mt-4 py-2 border border-white bg-white text-gray-900 text-sm"
        >
          더 많은 공고 보기 →
        </button>
      </div>

      {/* Additional Info */}
      <div className="border border-gray-400 bg-white p-6 mb-6">
        <div className="text-sm mb-4 pb-3 border-b border-gray-300">상세 정보</div>
        <div className="space-y-4">
          <div>
            <div className="text-sm mb-2">[ 수강 대상 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 백엔드 개발자 취업 준비생<br />
              - 프로그래밍 기초 보유자<br />
              - IT 업계 전환 희망자
            </div>
          </div>
          <div>
            <div className="text-sm mb-2">[ 수강 일정 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 월~금 09:00-18:00<br />
              - 총 960시간 (6개월)
            </div>
          </div>
          <div>
            <div className="text-sm mb-2">[ 수강료 지원 ]</div>
            <div className="border border-gray-400 p-4 bg-gray-50 text-sm text-gray-600">
              - 국비지원 과정 (조건 충족 시)<br />
              - 훈련장려금 최대 316만원<br />
              - 취업 성공 시 추가 지원금
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button className="flex-1 py-3 border border-gray-900 bg-white text-sm">공유</button>
        <button className="flex-1 py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
          수강 신청하기
        </button>
      </div>
    </div>
  );
}
