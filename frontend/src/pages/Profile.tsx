import { useMemo, useState } from 'react'

type RecommendationCard = {
  title: string
  description: string
  tags: string[]
}

const careerStages = ['학생', '취준생', '주니어', '미들', '시니어']
const interests = ['백엔드', '프론트엔드', '데이터 분석', '머신러닝 엔지니어', 'AI/LLM', 'DevOps']
const stacks = ['Python', 'Pandas', 'SQL', 'React', 'Node.js', 'TensorFlow', 'PyTorch']

const ProfilePage = () => {
  const [name, setName] = useState('홍길동')
  const [career, setCareer] = useState<string>('주니어')
  const [selectedInterests, setSelectedInterests] = useState<Set<string>>(new Set(['백엔드']))
  const [selectedStacks, setSelectedStacks] = useState<Set<string>>(new Set(['Python', 'SQL']))
  const [showRecommendations, setShowRecommendations] = useState(false)

  const recommendations = useMemo<RecommendationCard[]>(
    () => [
      {
        title: 'Python 백엔드 주니어 채용',
        description: 'Django · FastAPI 기반 서비스 운영팀, 코드 리뷰 문화가 자리잡은 환경.',
        tags: ['백엔드', 'Python', 'Django'],
      },
      {
        title: '데이터 분석 입문 부트캠프',
        description: '국비 지원, 파이썬·SQL·대시보드 실습으로 포트폴리오 완성.',
        tags: ['데이터', 'SQL', 'Tableau'],
      },
    ],
    [],
  )

  const toggleSet = (value: string, setter: React.Dispatch<React.SetStateAction<Set<string>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">내 프로필</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">기본 정보를 입력하고 추천 받기</h1>
          <p className="text-sm text-slate-600">
            간단한 프로필만 입력하면 채용/부트캠프 추천을 즉시 제공합니다. 지금은 더미 결과가 노출됩니다.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <section className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="text-lg font-bold text-slate-900">기본 정보</h2>
            <div className="mt-4 grid gap-4">
              <label className="text-sm text-slate-700">
                이름
                <input
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="mt-2 w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
                  placeholder="이름을 입력하세요"
                />
              </label>

              <label className="text-sm text-slate-700">
                현재 커리어 단계
                <div className="mt-2 flex flex-wrap gap-2">
                  {careerStages.map((stage) => (
                    <button
                      key={stage}
                      type="button"
                      onClick={() => setCareer(stage)}
                      className={`rounded-full px-4 py-2 text-sm font-semibold ${
                        career === stage
                          ? 'bg-primary-600 text-white shadow-soft'
                          : 'border border-slate-200 bg-white text-slate-800'
                      }`}
                    >
                      {stage}
                    </button>
                  ))}
                </div>
              </label>

              <div>
                <p className="text-sm font-semibold text-slate-900">관심 직무</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {interests.map((interest) => {
                    const active = selectedInterests.has(interest)
                    return (
                      <button
                        key={interest}
                        type="button"
                        onClick={() => toggleSet(interest, setSelectedInterests)}
                        className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                          active
                            ? 'bg-primary-50 text-primary-700 ring-1 ring-primary-200'
                            : 'border border-slate-200 bg-white text-slate-800'
                        }`}
                      >
                        {interest}
                      </button>
                    )
                  })}
                </div>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-900">보유 기술 스택</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {stacks.map((stack) => {
                    const active = selectedStacks.has(stack)
                    return (
                      <button
                        key={stack}
                        type="button"
                        onClick={() => toggleSet(stack, setSelectedStacks)}
                        className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                          active
                            ? 'bg-slate-900 text-white shadow-soft'
                            : 'border border-slate-200 bg-white text-slate-800'
                        }`}
                      >
                        {stack}
                      </button>
                    )
                  })}
                </div>
              </div>

              <button
                onClick={() => setShowRecommendations(true)}
                className="mt-2 w-full rounded-xl bg-gradient-to-r from-primary-500 to-primary-600 px-4 py-3 text-sm font-semibold text-white shadow-soft transition hover:shadow-lg hover:shadow-primary-200"
              >
                추천 받기
              </button>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-100 bg-slate-50/70 p-6 shadow-soft">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900">추천 결과</h2>
              <span className="text-xs font-semibold text-primary-700">더미 데이터</span>
            </div>
            {!showRecommendations ? (
              <div className="mt-6 rounded-xl border border-dashed border-slate-200 bg-white p-5 text-sm text-slate-600">
                프로필을 입력하고 &quot;추천 받기&quot;를 눌러주세요. 선택한 스택과 직무에 맞춰 추천 카드가 표시됩니다.
              </div>
            ) : (
              <div className="mt-4 space-y-3">
                {recommendations.map((rec) => (
                  <div
                    key={rec.title}
                    className="rounded-xl border border-slate-100 bg-white p-4 shadow-soft"
                  >
                    <h3 className="text-base font-bold text-slate-900">{rec.title}</h3>
                    <p className="mt-1 text-sm text-slate-600">{rec.description}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {rec.tags.map((tag) => (
                        <span
                          key={tag}
                          className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage
