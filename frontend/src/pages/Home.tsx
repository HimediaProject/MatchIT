import { type ReactNode, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import SkillSelector from '../components/SkillSelector'
import { metaApi } from '../services/apiService'

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

const StepCard = ({ step, index, children, className }: { step: Step; index: number; children: ReactNode; className?: string }) => (
  <div className={`rounded-2xl border border-slate-100 bg-white/90 p-6 shadow-soft ${className}`}>
    <div className="flex items-start gap-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary-50 text-sm font-semibold text-primary-700">
        {index}
      </div>
      <div className="w-full space-y-2">
        <div className="text-sm font-semibold text-primary-700">STEP {index}</div>
        <h3 className="text-lg font-bold text-slate-900">{step.title}</h3>
        <p className="text-sm text-slate-600">{step.description}</p>
        {children}
      </div>
    </div>
  </div>
)

const HomePage = () => {
  const navigate = useNavigate()
  const [selectedStacks, setSelectedStacks] = useState<string[]>([])
  const [careerLevels, setCareerLevels] = useState<any[]>([])
  const [experienceRanges, setExperienceRanges] = useState<any[]>([])
  const [selectedSource, setSelectedSource] = useState<'all' | 'jobs' | 'bootcamps'>('all')
  const [selectedCareerLevelId, setSelectedCareerLevelId] = useState<number | null>(null)
  const [selectedExperienceRangeId, setSelectedExperienceRangeId] = useState<number | null>(null)
  const [loadingMeta, setLoadingMeta] = useState(true)

  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const [cls, ers] = await Promise.all([metaApi.getCareerLevels().catch(() => []), metaApi.getExperienceRanges().catch(() => [])])
        const careerList = Array.isArray(cls) ? cls : cls?.careerlevels || []
        const expList = Array.isArray(ers) ? ers : ers?.experienceranges || []
        setCareerLevels(careerList)
        setExperienceRanges(expList)
        if (careerList.length > 0) setSelectedCareerLevelId(careerList[0].id ?? careerList[0].CareerLevelID ?? null)
        if (expList.length > 0) setSelectedExperienceRangeId(expList[0].id ?? expList[0].RangeID ?? null)
      } finally {
        setLoadingMeta(false)
      }
    }

    fetchMeta()
  }, [])

  const previewItems: PreviewItem[] = [
    { title: '프론트엔드 주니어', company: 'Acme Corp', tag: 'React · TS', type: 'Job' },
    { title: '백엔드 부트캠프', company: 'Hyper Study', tag: 'Spring · AWS', type: 'Bootcamp' },
    { title: '프로덕트 디자이너', company: 'Pixel Labs', tag: 'Figma · UX', type: 'Job' },
  ]

  const recommendations: Recommendation[] = [
    {
      title: '주니어 데이터 분석 채용',
      description: 'Django/FastAPI 기반 서비스의 데이터 파이프라인을 다루며 메트릭을 설계합니다.',
      tags: ['데이터', 'Python', 'Django'],
    },
    {
      title: '입문자를 위한 데이터 분석 부트캠프',
      description: '12주 SQL, Tableau, 프로젝트 중심 커리큘럼을 제공합니다.',
      tags: ['데이터', 'SQL', 'Tableau'],
    },
    {
      title: 'AI 서비스 프로토타입 제작',
      description: 'LLM API 연동과 RAG 파이프라인을 통해 서비스 MVP를 완성합니다.',
      tags: ['AI', 'LLM', 'Vector DB'],
    },
    {
      title: '클라우드 중심 백엔드 부트캠프',
      description: 'AWS 기반 CI/CD와 DevOps 워크플로우를 익힙니다.',
      tags: ['백엔드', 'AWS', 'DevOps'],
    },
  ]

  const techStacks = useMemo(() => Array.from(new Set(selectedStacks)), [selectedStacks])

  const startSearch = () => {
    const params = new URLSearchParams()
    techStacks.forEach((skill) => params.append('skills', skill))
    if (selectedSource !== 'all') params.set('source', selectedSource)
    if (selectedCareerLevelId) params.set('careerLevelId', selectedCareerLevelId.toString())
    if (selectedExperienceRangeId) params.set('experienceRangeId', selectedExperienceRangeId.toString())
    navigate(`/search?${params.toString()}`)
  }

  return (
    <div className="bg-white">
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_25%_20%,rgba(45,109,255,0.08),transparent_30%),radial-gradient(circle_at_80%_10%,rgba(245,159,0,0.08),transparent_20%)]" />
        <div className="relative mx-auto grid max-w-6xl grid-cols-1 items-center gap-10 px-4 py-16 md:px-6 lg:grid-cols-2 lg:py-20">
          <div className="space-y-6">
            <div className="inline-flex items-center gap-2 rounded-full bg-primary-50 px-4 py-2 text-sm font-semibold text-primary-700">
              맞춤 추천
            </div>
            <div className="space-y-4">
              <h1 className="text-3xl font-bold leading-tight text-slate-950 sm:text-4xl lg:text-5xl">
                기술 커리어에 딱 맞는 채용과 부트캠프를 한번에
              </h1>
              <p className="max-w-xl text-lg text-slate-600">
                기술 스택과 커리어 정보를 입력하면 즉시 맞춤 추천을 제공합니다. 방문 계획이 없다면 이메일로 결과를 받아보세요.
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
                <p className="text-xs text-slate-500">부트캠프 모음</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">94%</p>
                <p className="text-xs text-slate-500">추천 만족도</p>
              </div>
              <div>
                <p className="text-2xl font-bold text-slate-950">24시간</p>
                <p className="text-xs text-slate-500">데이터 업데이트 주기</p>
              </div>
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-x-6 top-8 h-full rounded-3xl bg-gradient-to-b from-primary-100/80 to-white blur-2xl" />
            <div className="relative rounded-3xl border border-slate-100 bg-white/90 p-6 shadow-soft">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-primary-700">추천 미리보기</p>
                  <h3 className="text-xl font-bold text-slate-900">오늘의 매칭</h3>
                  <p className="text-sm text-slate-500">프로필을 업데이트하면 바로 최신으로 보여드립니다.</p>
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
                  <p className="text-xs text-primary-700">보유 기술과 경력을 자동으로 반영해 추천해 드립니다.</p>
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
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">몇 가지 정보만 입력하면 바로 추천</h2>
              <p className="mt-2 text-sm text-slate-600">보유 기술과 커리어 정보를 선택하면 맞춤 추천을 보여드립니다.</p>
            </div>
            <button
              onClick={() => {
                if (selectedSource === 'bootcamps' && selectedStacks.length === 0) {
                  window.alert('부트캠프 추천은 기술 스택을 최소 1개 선택해 주세요.')
                  return
                }
                startSearch()
              }}
              className="inline-flex w-fit items-center justify-center rounded-full bg-slate-900 px-5 py-3 text-sm font-semibold text-white shadow-soft transition hover:bg-slate-800"
            >
              30초 만에 시작하기
            </button>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-2">
            <StepCard
              step={{
                title: '기술 스택 선택',
                description: '주력 기술을 선택하면 관련 채용과 부트캠프를 우선 추천합니다.',
              }}
              index={1}
              className="relative overflow-visible"
            >
              <div className="mt-3">
                <SkillSelector onChange={setSelectedStacks} initial={selectedStacks} />
              </div>
            </StepCard>

            <StepCard
              step={{
                title: '커리어 정보 선택',
                description: '경력 단계와 원하는 소스를 알려주시면 정확도를 높입니다.',
              }}
              index={2}
            >
              <div className="mt-3 grid gap-3 sm:grid-cols-3">
                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-600">소스</label>
                  <select
                    value={selectedSource}
                    onChange={(e) => setSelectedSource(e.target.value as 'all' | 'jobs' | 'bootcamps')}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-primary-600"
                  >
                    <option value="all">전체</option>
                    <option value="jobs">채용공고</option>
                    <option value="bootcamps">부트캠프</option>
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-600">커리어 레벨</label>
                  <select
                    value={selectedCareerLevelId ?? ''}
                    onChange={(e) => setSelectedCareerLevelId(e.target.value ? Number(e.target.value) : null)}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-primary-600"
                  >
                    {loadingMeta ? (
                      <option value="">불러오는 중...</option>
                    ) : careerLevels.length === 0 ? (
                      <option value="">옵션 없음</option>
                    ) : (
                      careerLevels.map((c: any) => {
                        const id = c.id ?? c.CareerLevelID ?? c.careerlevelid
                        const name = c.name ?? c.CareerName ?? c.careername
                        return (
                          <option key={id} value={id}>
                            {name}
                          </option>
                        )
                      })
                    )}
                  </select>
                </div>

                <div>
                  <label className="mb-1 block text-xs font-semibold text-slate-600">경력 구간</label>
                  <select
                    value={selectedExperienceRangeId ?? ''}
                    onChange={(e) => setSelectedExperienceRangeId(e.target.value ? Number(e.target.value) : null)}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:ring-2 focus:ring-primary-600"
                  >
                    {loadingMeta ? (
                      <option value="">불러오는 중...</option>
                    ) : experienceRanges.length === 0 ? (
                      <option value="">옵션 없음</option>
                    ) : (
                      experienceRanges.map((r: any) => {
                        const id = r.id ?? r.RangeID ?? r.rangeid
                        const label = r.name ?? r.RangeName ?? r.rangename ?? r.label ?? r.range
                        return (
                          <option key={id} value={id}>
                            {label}
                          </option>
                        )
                      })
                    )}
                  </select>
                </div>
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
              <h2 className="text-2xl font-bold text-slate-950 sm:text-3xl">샘플 추천 채용 · 부트캠프</h2>
              <p className="mt-2 text-sm text-slate-600">비슷한 내용으로 곧 반영될 공고와 프로그램을 보여드립니다.</p>
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
