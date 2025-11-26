type NavigateFunction = (page: string) => void;

interface BootcampComparePageProps {
  onNavigate: NavigateFunction;
  selectedBootcamps: number[];
}

export default function BootcampComparePage({ onNavigate, selectedBootcamps }: BootcampComparePageProps) {
  const bootcamps = [
    {
      id: 1,
      institution: '코딩 부트캠프 A',
      course: '백엔드 개발자 양성 과정',
      price: '450만원',
      support: '국비지원 가능',
      duration: '6개월',
      schedule: '월~금 09:00-18:00',
      hours: '960시간',
      mode: '오프라인',
      location: '서울 강남구',
      startDate: '2026.02.01',
      skills: ['Python', 'Django', 'PostgreSQL', 'Docker', 'AWS', 'Git'],
      curriculum: [
        'Week 1-4: Python 기초',
        'Week 5-8: Django Framework',
        'Week 9-12: Database',
        'Week 13-16: DevOps',
        'Week 17-24: 프로젝트',
      ],
    },
    {
      id: 2,
      institution: '테크 아카데미 B',
      course: 'DevOps 엔지니어 양성',
      price: '500만원',
      support: '부분 지원',
      duration: '5개월',
      schedule: '월~금 10:00-19:00',
      hours: '800시간',
      mode: '온라인',
      location: '온라인',
      startDate: '2026.02.15',
      skills: ['Linux', 'Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Terraform'],
      curriculum: [
        'Week 1-4: Linux & 네트워크',
        'Week 5-8: 컨테이너 기술',
        'Week 9-12: 클라우드 인프라',
        'Week 13-16: CI/CD',
        'Week 17-20: 프로젝트',
      ],
    },
    {
      id: 3,
      institution: '온라인 코딩스쿨 C',
      course: '프론트엔드 개발자 부트캠프',
      price: '350만원',
      support: '지원 불가',
      duration: '4개월',
      schedule: '자율 학습',
      hours: '640시간',
      mode: '온라인',
      location: '온라인',
      startDate: '상시 모집',
      skills: ['HTML', 'CSS', 'JavaScript', 'React', 'TypeScript', 'Next.js'],
      curriculum: [
        'Week 1-4: HTML/CSS/JavaScript',
        'Week 5-8: React 기초',
        'Week 9-12: React 심화',
        'Week 13-16: 프로젝트',
      ],
    },
  ].filter((bootcamp) => selectedBootcamps.includes(bootcamp.id));

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      {/* Back Button */}
      <button
        onClick={() => onNavigate('bootcampList')}
        className="mb-6 px-4 py-2 border border-gray-900 text-sm"
      >
        ← 목록으로
      </button>

      <h1 className="mb-8">부트캠프 비교</h1>

      {/* Summary Headers */}
      <div className="flex gap-4 mb-8 overflow-x-auto pb-4">
        {bootcamps.map((bootcamp) => (
          <div
            key={bootcamp.id}
            className="min-w-[320px] border border-gray-400 bg-white p-5 flex-shrink-0"
          >
            <div className="text-xs text-gray-600 mb-1">[{bootcamp.institution}]</div>
            <div className="text-sm mb-3">{bootcamp.course}</div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-1 border border-gray-900 text-xs">{bootcamp.price}</span>
              <span className="text-xs text-gray-600">{bootcamp.duration}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Sections */}
      <div className="space-y-6">
        {/* Enrollment Info */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">모집 정보 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {bootcamps.map((bootcamp) => (
              <div key={bootcamp.id} className="min-w-[320px] flex-shrink-0 space-y-2">
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">시작일</div>
                  <div className="text-sm">{bootcamp.startDate}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">교육 기간</div>
                  <div className="text-sm">{bootcamp.duration}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">수업 시간</div>
                  <div className="text-sm">{bootcamp.schedule}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">총 시간</div>
                  <div className="text-sm">{bootcamp.hours}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">수강 방식</div>
                  <div className="text-sm">{bootcamp.mode}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">위치</div>
                  <div className="text-sm">{bootcamp.location}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Cost Comparison */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">비용 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {bootcamps.map((bootcamp) => (
              <div key={bootcamp.id} className="min-w-[320px] flex-shrink-0">
                <div className="border-2 border-gray-900 p-4 bg-gray-50 mb-3">
                  <div className="text-xs text-gray-600 mb-2">수강료</div>
                  <div className="text-lg mb-2">{bootcamp.price}</div>
                  <div className="text-xs text-gray-600">총 {bootcamp.hours}</div>
                </div>
                <div className="border border-gray-400 p-4 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-2">지원금</div>
                  <div className="text-sm">{bootcamp.support}</div>
                  {bootcamp.support.includes('국비') && (
                    <div className="text-xs text-gray-600 mt-2">훈련장려금 별도</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skills Comparison */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">배우는 기술 스택</div>
          <div className="flex gap-4 overflow-x-auto">
            {bootcamps.map((bootcamp) => (
              <div key={bootcamp.id} className="min-w-[320px] flex-shrink-0">
                <div className="flex flex-wrap gap-2 mb-2">
                  {bootcamp.skills.map((skill) => (
                    <span key={skill} className="px-2 py-1 border-2 border-gray-900 text-xs">
                      {skill}
                    </span>
                  ))}
                </div>
                <div className="text-xs text-gray-600 mt-3">총 {bootcamp.skills.length}개 기술</div>
              </div>
            ))}
          </div>
        </div>

        {/* Curriculum Comparison - Accordion Style */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">커리큘럼 비교</div>
          <div className="flex gap-4 overflow-x-auto">
            {bootcamps.map((bootcamp) => (
              <div key={bootcamp.id} className="min-w-[320px] flex-shrink-0">
                <div className="space-y-2">
                  {bootcamp.curriculum.map((module, idx) => (
                    <div key={idx} className="border border-gray-400 bg-gray-50">
                      <button className="w-full p-3 flex items-center justify-between text-left">
                        <span className="text-xs">{module}</span>
                        <span className="text-xs text-gray-600">▼</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Summary */}
        <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">특징 요약</div>
          <div className="flex gap-4 overflow-x-auto">
            {bootcamps.map((bootcamp) => (
              <div key={bootcamp.id} className="min-w-[320px] flex-shrink-0">
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="w-4 h-4 border border-gray-900 flex items-center justify-center text-xs flex-shrink-0">
                      ✓
                    </span>
                    <span>실무 중심 커리큘럼</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-4 h-4 border border-gray-900 flex items-center justify-center text-xs flex-shrink-0">
                      ✓
                    </span>
                    <span>포트폴리오 제작 지원</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="w-4 h-4 border border-gray-900 flex items-center justify-center text-xs flex-shrink-0">
                      ✓
                    </span>
                    <span>취업 연계 프로그램</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-8">
        {bootcamps.map((bootcamp) => (
          <div key={bootcamp.id} className="flex-1">
            <button className="w-full py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
              {bootcamp.institution} 신청하기
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
