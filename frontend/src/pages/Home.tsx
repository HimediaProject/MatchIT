import { type ReactNode, useMemo } from 'react'
import { Link } from 'react-router-dom'

type Step = {
  title: string
  description: string
}

type PreviewItem = {
  title: string
  company: string
  tag: string
  type: 'Job' | 'Bootcamp'
}

type Recommendation = {
  title: string
  description: string
  tags: string[]
}

const StepCard = ({ step, index, children }: { step: Step; index: number; children: ReactNode }) => (
  <div className="rounded-2xl border border-slate-100 bg-white/90 p-6 shadow-soft">
    <div className="flex items-start gap-4">
      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary-50 text-sm font-semibold text-primary-700">
        {index}
      </div>
      <div className="space-y-2">
        <div className="text-sm font-semibold text-primary-700">STEP {index}</div>
        <h3 className="text-lg font-bold text-slate-900">{step.title}</h3>
        <p className="text-sm text-slate-600">{step.description}</p>
        {children}
      </div>
    </div>
  </div>
)

const HomePage = () => {
  const techStacks = useMemo(() => ['React', 'TypeScript', 'Node.js', 'Spring', 'Next.js'], [])
  const careerStages = useMemo(() => ['학생', '1-3년차', '4-6년차', '7년차 이상', '커리어 전환'], [])

  const previewItems: PreviewItem[] = [
    { title: '프론트엔드 엔지니어', company: 'Acme Corp', tag: 'React · TS', type: 'Job' },
    { title: '백엔드 부트캠프', company: 'Hyper Study', tag: 'Spring · AWS', type: 'Bootcamp' },
    { title: '프로덕트 디자이너', company: 'Pixel Labs', tag: 'Figma · UX', type: 'Job' },
  ]

  const recommendations: Recommendation[] = [
    {
      title: '주니어 파이썬 데이터 분석 채용',
      description: 'Django/FastAPI 기반 서비스의 ETL 파이프라인을 다루며 시니어 멘토링을 제공합니다.',
      tags: ['백엔드', 'Python', 'Django'],
    },
    {
      title: '입문자를 위한 데이터 분석 부트캠프',
      description: '12주 동안 SQL, Tableau, 실무 대시보드 제작을 다룹니다.',
      tags: ['데이터', 'SQL', 'Tableau'],
    },
    {
      title: 'AI 서비스 프로토타입 프로젝트',
      description: 'LLM API 연동과 RAG 파이프라인 실습을 포함한 실전 과제 중심 과정입니다.',
      tags: ['AI', 'LLM', 'Vector DB'],
    },
    {
      title: '클라우드 중심 백엔드 부트캠프',
      description: 'AWS 기반 CI/CD와 마이크로서비스 실습, DevOps 워크플로우를 다룹니다.',
      tags: ['백엔드', 'AWS', 'DevOps'],
    },
  ]

  return (
    <div className="bg-white">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(45,109,255,0.08),transparent_30%),radial-gradient(circle_at_80%_10%,rgba(245,159,0,0.08),transparent_20%)]" />
        <div className="relative mx-auto grid max-w-6xl grid-cols-1 items-center gap-10 px-4 py-16 md:px-6 lg:grid-cols-2 lg:py-20">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-4 py-2 text-sm font-semibold text-primary-700">
              스택 기반 AI 추천
            </div>
            <div className="space-y-4">
              <h1 className="text-3xl font-bold leading-tight text-slate-950 sm:text-4xl lg:text-5xl">
                기술 커리어를 위한 더 똑똑한 매칭
                <br />
                채용과 부트캠프를 한 번에 찾으세요.
              </h1>
              <p className="max-w-xl text-lg text-slate-600">
                보유 스택과 경력, 목표를 알려주면 맞춤 채용과 부트캠프를 바로 추천해 드립니다.
                방문할 때마다 새롭게 갱신된 추천을 받아보세요.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                to="/"
                className="rounded-full bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:shadow-lg hover:shadow-primary-200"
              >
                추천 받기
              </Link>
              <Link
                to="/jobs"
                className="rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:text-primary-700"
              >
                채용 보러가기
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-4 rounded-2xl border border-slate-100 bg-white/80 p-4 shadow-soft sm:grid-cols-4">
              <div>
                <p className="text-2xl font-bold text-slate-950">+1,240</p>
                <p className="text-xs text-slate-500">실시간 채용 매칭</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">+180</p>
                <p className="text-xs text-slate-500">부트캠프 옵션</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">94%</p>
                <p className="text-xs text-slate-500">사용자 만족도</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">24시간</p>
                <p className="text-xs text-slate-500">데이터 새로고침 주기</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-x-6 top-8 h-full rounded-3xl bg-gradient-to-b from-primary-100/80 to-white blur-2xl" />
            <div className="relative rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-soft">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-primary-700">추천 미리보기</p>
                  <h3 className="text-xl font-bold text-slate-900">당신이 좋아할 매칭</h3>
                  <p className="text-sm text-slate-500">프로필을 업데이트하면 바로 예시를 새로 보여드립니다.</p>
                </div>
                <span className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">실시간</span>
              </div>

              <div className="mt-6 space-y-3">
                {previewItems.map((item) => (
                  <div
                    key={`${item.title}-${item.company}`}
                    className="flex items-start justify-between rounded-2xl border border-slate-100 bg-slate-50/60 p-4"
                  >
                    <div className="space-y-1">
                      <p className="text-xs font-semibold text-primary-700">{item.type === 'Job' ? '채용' : '부트캠프'}</p>
                      <p className="text-lg font-semibold text-slate-900">{item.title}</p>
                      <p className="text-sm text-slate-600">{item.company}</p>
                      <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                        {item.tag}
                      </div>
                    </div>
                    <div className="flex h-full items-center">
                      <span className="rounded-full bg-primary-600 px-3 py-1 text-xs font-semibold text-white">매칭</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex items-center justify-between rounded-2xl border border-dashed border-primary-200 bg-primary-50/60 p-4">
                <div>
                  <p className="text-sm font-semibold text-primary-800">이력서 간단 업로드</p>
                  <p className="text-xs text-primary-700">보유 기술을 더 정확히 반영해 추천을 고도화합니다.</p>
                </div>
                <div className="hidden h-16 w-16 items-center justify-center rounded-2xl border border-primary-200 text-xs font-semibold text-primary-700 md:flex">
                  준비 중
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-100 bg-gradient-to-b from-white to-slate-50">
        <div className="mx-auto max-w-6xl px-4 py-14 md:px-6">
          <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm font-semibold text-primary-700">3단계 요약</p>
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">몇 가지 정보로 추천을 열어보세요</h2>
              <p className="mt-2 text-sm text-slate-600">보유 스택과 커리어 단계만 선택하면 바로 맞춤 추천을 보여드립니다.</p>
            </div>
            <Link
              to="/"
              className="inline-flex w-fit items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-slate-800"
            >
              30초 만에 시작
            </Link>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <StepCard
              step={{
                title: '사용 기술 선택',
                description: '핵심 기술 3개 이상을 고르면 바로 매칭을 시작합니다.',
              }}
              index={1}
            >
              <div className="mt-3 flex flex-wrap gap-2">
                {techStacks.map((stack) => (
                  <span
                    key={stack}
                    className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-800 ring-1 ring-inset ring-slate-200"
                  >
                    {stack}
                  </span>
                ))}
                <button className="rounded-full border border-dashed border-slate-300 px-3 py-1 text-xs font-semibold text-slate-600 hover:border-primary-300 hover:text-primary-700">
                  + 스택 추가
                </button>
              </div>
            </StepCard>

            <StepCard
              step={{
                title: '커리어 단계 선택',
                description: '현재 상황을 알려주시면 성장 또는 안정에 맞게 추천을 조정합니다.',
              }}
              index={2}
            >
              <div className="mt-3 grid gap-2 sm:grid-cols-2">
                {careerStages.map((stage) => (
                  <div
                    key={stage}
                    className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50/80 px-3 py-3 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:bg-white"
                  >
                    {stage}
                    <span className="text-xs font-bold text-primary-600">선택</span>
                  </div>
                ))}
              </div>
            </StepCard>
          </div>
        </div>
      </section>

      <section className="border-t border-slate-100 bg-white">
        <div className="mx-auto max-w-6xl px-4 py-14 md:px-6">
          <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="text-sm font-semibold text-primary-700">추천 결과</p>
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">큐레이션된 채용 · 부트캠프</h2>
              <p className="mt-2 text-sm text-slate-600">비슷한 사용자 패턴을 반영한 실시간 공고와 프로그램을 섞어 제공합니다.</p>
            </div>
            <Link
              to="/jobs"
              className="inline-flex w-fit items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:text-primary-700"
            >
              전체 채용 보기
            </Link>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-2">
            {recommendations.map((rec) => (
              <div
                key={rec.title}
                className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-slate-50/80 p-6 shadow-soft"
              >
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-bold text-slate-900">{rec.title}</h3>
                  <span className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700">
                    추천
                  </span>
                </div>
                <p className="text-sm text-slate-600">{rec.description}</p>
                <div className="flex flex-wrap gap-2">
                  {rec.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-800 ring-1 ring-slate-200"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
