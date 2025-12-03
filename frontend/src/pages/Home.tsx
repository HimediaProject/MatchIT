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
  type: '채용' | '부트캠프'
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
  const careerStages = useMemo(
    () => ['주니어·인턴', '1-3년차', '4-6년차', '시니어', '커리어 전환 준비'],
    [],
  )
  const previewItems: PreviewItem[] = [
    { title: '프론트엔드 엔지니어', company: '핀테크 스타트업', tag: 'React · TS', type: '채용' },
    { title: '백엔드 부트캠프', company: '클라우드 집중 과정', tag: 'Spring · AWS', type: '부트캠프' },
    { title: '풀스택 포지션', company: '커머스 스케일업', tag: 'Next.js · Node', type: '채용' },
  ]
  const recommendations: Recommendation[] = [
    {
      title: '초보 Python 개발자에게 인기 있는 채용 포지션',
      description: '웹 크롤링/ETL 경험이 있으면 우대, Django·FastAPI 기반 서비스 운영 팀.',
      tags: ['백엔드', 'Python', 'Django'],
    },
    {
      title: '데이터 분석 입문자를 위한 국비 부트캠프',
      description: '기초 파이썬부터 SQL, Tableau 대시보드까지 12주 완주 커리큘럼.',
      tags: ['데이터', 'SQL', '시각화'],
    },
    {
      title: 'AI 서비스 PoC 경험을 쌓을 수 있는 스타트업 포지션',
      description: 'LLM API 연동, RAG 파이프라인 구축 경험자를 우대하는 초기팀.',
      tags: ['AI', 'LLM', 'Vector DB'],
    },
    {
      title: '클라우드 기반 백엔드 부트캠프',
      description: 'AWS 기반 CI/CD와 마이크로서비스 아키텍처를 실습 중심으로 학습.',
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
              내 스택 기반 AI 추천
            </div>
            <div className="space-y-4">
              <h1 className="text-3xl font-bold leading-tight text-slate-950 sm:text-4xl lg:text-5xl">
                내 기술 스택과 커리어 단계에 맞춰
                <br />
                채용공고와 부트캠프를 한 번에.
              </h1>
              <p className="max-w-xl text-lg text-slate-600">
                기술 스택, 커리어 단계, 성장 목표를 입력하면 가장 적합한 채용과 부트캠프를 큐레이션해드려요. 더 이상 흩어진 정보를
                찾느라 시간을 쓰지 마세요.
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                to="/"
                className="rounded-full bg-gradient-to-r from-primary-500 to-primary-600 px-6 py-3 text-sm font-semibold text-white shadow-soft transition hover:shadow-lg hover:shadow-primary-200"
              >
                지금 바로 추천 받기
              </Link>
              <Link
                to="/jobs"
                className="rounded-full border border-slate-200 px-6 py-3 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:text-primary-700"
              >
                채용공고 둘러보기
              </Link>
            </div>

            <div className="grid grid-cols-2 gap-4 rounded-2xl border border-slate-100 bg-white/80 p-4 shadow-soft sm:grid-cols-4">
              <div>
                <p className="text-2xl font-bold text-slate-950">+1,240</p>
                <p className="text-xs text-slate-500">실시간 맞춤 채용</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">+180</p>
                <p className="text-xs text-slate-500">부트캠프 과정</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">94%</p>
                <p className="text-xs text-slate-500">만족도</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">24시간</p>
                <p className="text-xs text-slate-500">업데이트 주기</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-x-6 top-8 h-full rounded-3xl bg-gradient-to-b from-primary-100/80 to-white blur-2xl" />
            <div className="relative rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-soft">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-primary-700">추천 미리보기</p>
                  <h3 className="text-xl font-bold text-slate-900">내 스택에 맞는 포지션</h3>
                  <p className="text-sm text-slate-500">입력한 정보로 즉시 맞춤 리스트를 생성합니다.</p>
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
                      <p className="text-xs font-semibold text-primary-700">{item.type}</p>
                      <p className="text-lg font-semibold text-slate-900">{item.title}</p>
                      <p className="text-sm text-slate-600">{item.company}</p>
                      <div className="mt-2 inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-700">
                        {item.tag}
                      </div>
                    </div>
                    <div className="flex h-full items-center">
                      <span className="rounded-full bg-primary-600 px-3 py-1 text-xs font-semibold text-white">맞춤</span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-6 flex items-center justify-between rounded-2xl border border-dashed border-primary-200 bg-primary-50/60 p-4">
                <div>
                  <p className="text-sm font-semibold text-primary-800">오른쪽 영역은 Illustration/Chart 자리</p>
                  <p className="text-xs text-primary-700">
                    지원 현황, 성장 곡선 등 원하는 그래프나 이미지로 교체하세요.
                  </p>
                </div>
                <div className="hidden h-16 w-16 items-center justify-center rounded-2xl border border-primary-200 text-xs font-semibold text-primary-700 md:flex">
                  Placeholder
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
              <p className="text-sm font-semibold text-primary-700">온보딩 2단계</p>
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">간단한 정보만 입력하면 맞춤 추천 시작</h2>
              <p className="mt-2 text-sm text-slate-600">
                기술 스택과 커리어 단계만 선택하면 AI가 바로 큐레이션합니다. 추후 프로필 연동으로 더 정교해집니다.
              </p>
            </div>
            <Link
              to="/"
              className="inline-flex w-fit items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-slate-800"
            >
              30초만에 시작하기
            </Link>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <StepCard
              step={{
                title: '기술 스택 입력',
                description: '주력 기술 3개를 선택하면 관련 채용과 부트캠프를 먼저 보여드려요.',
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
                  + 직접 입력
                </button>
              </div>
            </StepCard>

            <StepCard
              step={{
                title: '커리어 단계 선택',
                description: '현재 경력 레벨과 목표를 알려주시면 난이도와 성장 경로에 맞춰 추천합니다.',
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
              <p className="text-sm font-semibold text-primary-700">추천 결과 미리보기</p>
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">채용/부트캠프 큐레이션</h2>
              <p className="mt-2 text-sm text-slate-600">
                입력한 스택과 커리어 단계에 맞춰 생성된 추천 리스트 예시입니다.
              </p>
            </div>
            <Link
              to="/jobs"
              className="inline-flex w-fit items-center justify-center rounded-full border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-800 transition hover:border-primary-200 hover:text-primary-700"
            >
              전체 보기
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
