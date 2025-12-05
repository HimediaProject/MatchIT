import { useEffect, useState } from 'react'
// import { XCircle, ChevronRight } from 'lucide-react' // 아이콘 라이브러리 예시 (없으면 텍스트나 다른 아이콘으로 대체 가능)

// 백엔드 스키마와 매칭되는 타입 정의 (화면 표시용)
type ComparedJob = {
  id: string
  provider: string // 플랫폼 (wanted, remember 등)
  title: string
  company: string
  location: string
  experience: string
  education: string
  salary: string
  deadlines: string
}
type ComparedBootcamp = {
  id: string
  provider: string
  title: string
  period: string
  schedule: string
  time: string
  mode: string
  location: string
}

const formatDate = (d?: string | null) => {
  if (!d) return ''
  try {
    const dt = new Date(d)
    if (isNaN(dt.getTime())) return d
    return dt.toLocaleDateString('ko-KR')
  } catch {
    return d
  }
}

const ComparePage = () => {
  const [mode, setMode] = useState<'jobs' | 'bootcamps'>('bootcamps')
  const [items, setItems] = useState<Array<ComparedJob | ComparedBootcamp>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Parse ids from URL query param `ids=1,2,3` and optional `mode=jobs|bootcamps`
  const parseIdsFromSearch = () => {
    try {
      const params = new URLSearchParams(window.location.search)
      const qMode = params.get('mode')
      if (qMode === 'jobs' || qMode === 'bootcamps') setMode(qMode)
      const idsParam = params.get('ids')
      if (!idsParam) return [] as number[]
      return idsParam
        .split(',')
        .map((s) => parseInt(s.trim(), 10))
        .filter((n) => !isNaN(n))
    } catch {
      return [] as number[]
    }
  }

  const mapJob = (j: any, idx: number): ComparedJob => {
    return {
      id: j.PostID ? String(j.PostID) : `job-${idx}`,
      provider: j.provider || j.platform || '',
      title: j.title || j.Title || '',
      company: j.company_name || j.CompanyName || '',
      location: j.location || j.Location || '',
      experience: j.experience_requirement || j.ExperienceRequirement || '',
      education: j.education_requirement || j.EducationRequirement || '',
      salary: j.salary || j.Salary || '',
      deadlines: j.close_date ? formatDate(j.close_date) : j.posted_date ? formatDate(j.posted_date) : '',
    }
  }

  const mapBootcamp = (b: any, idx: number): ComparedBootcamp => {
    const reg = b.registration_date || b.RegistrationDate || null
    const close = b.close_date || b.CloseDate || null
    const start = b.start_date || b.StartDate || null
    return {
      id: b.BootcampID ? String(b.BootcampID) : `boot-${idx}`,
      provider: b.institute_name || b.InstituteName || '',
      title: b.title || b.Title || '',
      period: reg || close ? `${formatDate(reg)} ~ ${formatDate(close)}` : '',
      schedule: start ? formatDate(start) : '',
      time: b.time || '',
      mode: b.online_offline || b.OnlineOffline || '',
      location: b.location || b.Location || '',
    }
  }

  const fetchCompare = async (ids: number[], modeToFetch: 'jobs' | 'bootcamps') => {
    if (!ids || ids.length === 0) {
      setItems([])
      return
    }
    setLoading(true)
    setError(null)
    try {
      const endpoint = modeToFetch === 'jobs' ? '/comparison/jobs' : '/comparison/bootcamps'
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(ids),
      })
      if (!res.ok) {
        const text = await res.text()
        throw new Error(text || `Request failed ${res.status}`)
      }
      const data = await res.json()
      if (modeToFetch === 'jobs') {
        setItems((data || []).map((d: any, i: number) => mapJob(d, i)))
      } else {
        setItems((data || []).map((d: any, i: number) => mapBootcamp(d, i)))
      }
    } catch (e: any) {
      setError(e?.message || String(e))
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const ids = parseIdsFromSearch()
    if (ids.length > 0) fetchCompare(ids, mode)
    else setItems([])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode])

  // 항목 삭제 핸들러: 로컬 상태에서 제거
  const handleRemove = (id: string) => {
    setItems((prev) => prev.filter((it) => it.id !== id))
  }

  return (
    <div className="bg-white min-h-screen">
      <div className="mx-auto max-w-7xl px-4 py-12 md:px-6">
        
        {/* 헤더 섹션 */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-slate-900 mb-6">
            {mode === 'jobs' ? '채용공고 비교해 볼까요?' : '부트캠퍼 비교해 볼까요?'}
          </h1>
          
          {/* 탭 전환 버튼 */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMode('jobs')}
              className={`rounded-full px-5 py-2 text-sm font-semibold transition-colors ${
                mode === 'jobs'
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              채용 비교
            </button>
            <button
              onClick={() => setMode('bootcamps')}
              className={`rounded-full px-5 py-2 text-sm font-semibold transition-colors ${
                mode === 'bootcamps'
                  ? 'bg-primary-600 text-white shadow-md'
                  : 'border border-slate-200 bg-white text-slate-600 hover:bg-slate-50'
              }`}
            >
              부트캠프 비교
            </button>
          </div>
        </div>

              {/* 메인 콘텐츠 영역: 선택된 항목이 없을 때 */}
              {loading ? (
                <div className="flex h-64 w-full items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 text-slate-500">
                  불러오는 중...
                </div>
              ) : error ? (
                <div className="flex h-64 w-full items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-rose-50 text-rose-700">
                  에러: {error}
                </div>
              ) : items.length === 0 ? (
           <div className="flex h-64 w-full items-center justify-center rounded-2xl border border-dashed border-slate-300 bg-slate-50 text-slate-500">
             비교할 항목을 리스트에서 선택해주세요.
           </div>
              ) : (
                <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {/* 카드 렌더링 (Loop) */}
                  {items.map((item) => {
                    const isJob = mode === 'jobs'
                    const job = item as ComparedJob
                    const camp = item as ComparedBootcamp

                    return (
                      <div key={item.id} className="flex flex-col">
                        {/* 상단 카드 영역 */}
                        <div className="relative flex flex-col justify-between rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md">
                          {/* 삭제 버튼 */}
                          <button
                            onClick={() => handleRemove(item.id)}
                            className="absolute right-4 top-4 text-slate-300 hover:text-red-500 transition-colors"
                          >
                            <XCircle size={24} />
                          </button>

                          <div className="mb-6">
                            <p className="mb-2 text-xs font-medium text-slate-500">
                              {isJob ? job.provider : camp.provider}
                            </p>
                            <h3 className="line-clamp-2 min-h-[3.5rem] text-lg font-bold leading-snug text-slate-900">
                              {isJob ? job.title : camp.title}
                            </h3>
                            {isJob && (
                              <p className="mt-1 text-sm font-semibold text-primary-600">
                                {job.company}
                              </p>
                            )}
                          </div>

                          <div className="flex gap-2 mt-auto">
                            <button className="flex-1 rounded-lg border border-primary-600 py-2.5 text-sm font-bold text-primary-600 transition hover:bg-primary-50">
                              자세히 보기
                            </button>
                            <button className="flex-1 rounded-lg bg-primary-600 py-2.5 text-sm font-bold text-white shadow-sm transition hover:bg-primary-700">
                              교육 신청
                            </button>
                          </div>
                        </div>

                      </div>
                    )
                  })}
                </div>
        )}

        {/* 상세 정보 섹션 타이틀 */}
        {items.length > 0 && (
          <div className="mt-12 mb-8 border-b border-slate-100 pb-4">
            <h2 className="text-xl font-bold text-primary-600">어떤 과정인가요?</h2>
          </div>
        )}

        {/* 상세 정보 그리드 (위 카드와 1:1 매칭) */}
        {items.length > 0 && (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {items.map((item) => {
              const isJob = mode === 'jobs';
              const job = item as ComparedJob;
              const camp = item as ComparedBootcamp;

              return (
                <div key={`${item.id}-details`} className="flex flex-col gap-6 px-1">
                  
                  {/* 부트캠프 모드일 때 상세 정보 */}
                  {!isJob && (
                    <>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">모집일정</span>
                        <p className="text-sm font-bold text-slate-900 leading-relaxed">
                          {camp.period}
                        </p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">교육일정</span>
                        <p className="text-sm font-bold text-slate-900 leading-relaxed">
                          {camp.schedule}
                        </p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">수업시간</span>
                        <p className="text-sm font-bold text-slate-900 leading-relaxed">
                          {camp.time}
                        </p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">수업방식</span>
                        <p className="text-sm font-bold text-slate-900">
                          {camp.mode}
                        </p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">교육장소</span>
                         {/* JSON 문자열 등 파싱이 필요할 수 있으나 단순 표시 */}
                        <p className="text-sm font-bold text-slate-900 break-keep">
                          {camp.location.replace(/["{}]/g, '').replace('district:', '')}
                        </p>
                      </div>
                    </>
                  )}

                  {/* 채용 모드일 때 상세 정보 */}
                  {isJob && (
                    <>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">마감일</span>
                        <p className="text-sm font-bold text-slate-900">{job.deadlines}</p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">연봉</span>
                        <p className="text-sm font-bold text-slate-900">{job.salary}</p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">근무지</span>
                        <p className="text-sm font-bold text-slate-900">{job.location}</p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">경력요건</span>
                        <p className="text-sm font-bold text-slate-900">{job.experience}</p>
                      </div>
                      <div>
                        <span className="mb-1 block text-xs text-slate-500">학력</span>
                        <p className="text-sm font-bold text-slate-900">{job.education}</p>
                      </div>
                    </>
                  )}
                  
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}

export default ComparePage