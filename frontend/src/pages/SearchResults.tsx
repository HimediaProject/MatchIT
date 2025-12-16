import { useEffect, useState } from 'react'
import { useLocation, Link } from 'react-router-dom'
import { searchApi } from '../services/apiService'

function useQuery() {
  return new URLSearchParams(useLocation().search)
}

const SearchResultsPage = () => {
  const query = useQuery()
  const location = useLocation()
  const keyword = query.get('keyword') || ''
  const skills = query.getAll('skills')
  const source = query.get('source') as '전체' | '채용' | '부트캠프' | null
  const careerLevelId = query.get('careerLevelId') ? Number(query.get('careerLevelId')) : undefined
  const experienceRangeId = query.get('experienceRangeId') ? Number(query.get('experienceRangeId')) : undefined
  const view = query.get('view') as 'jobs' | 'bootcamps' | null

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobs, setJobs] = useState<any[]>([])
  const [bootcamps, setBootcamps] = useState<any[]>([])

  useEffect(() => {
    // 필터가 하나라도 있으면 검색 실행
    const hasFilters = keyword || skills.length > 0 || source || careerLevelId || experienceRangeId
    
    if (!hasFilters) {
      setJobs([])
      setBootcamps([])
      return
    }

    setLoading(true)
    setError(null)
    
    searchApi
      .searchWithFilters({
        keyword: keyword || undefined,
        skills: skills.length > 0 ? skills : undefined,
        source: source || undefined,
        careerLevelId,
        experienceRangeId,
        limit: 50,
      })
      .then((data) => {
        setJobs(data.jobs || [])
        setBootcamps(data.bootcamps || [])
      })
      .catch((err) => setError(err.message || '검색 중 오류가 발생했습니다'))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [keyword, source, careerLevelId, experienceRangeId, skills.length, ...skills])

  const displayedJobs = view === 'jobs' ? jobs : jobs.slice(0, 5)
  const displayedBootcamps = view === 'bootcamps' ? bootcamps : bootcamps.slice(0, 5)

  const buildViewUrl = (target: 'jobs' | 'bootcamps') => {
    const params = new URLSearchParams(location.search)
    params.set('view', target)
    return `/search?${params.toString()}`
  }

  const showJobsSection = view !== 'bootcamps'
  const showBootcampSection = view !== 'jobs'

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">검색 결과</h1>
      </div>

      {loading && <p>검색 중...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      {showJobsSection && (
        <section className="mb-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">채용공고 ({jobs.length})</h2>
            {jobs.length > 5 && view !== 'jobs' && (
              <Link
                to={buildViewUrl('jobs')}
                className="text-sm font-semibold text-primary-700 hover:text-primary-800"
              >
                전체보기
              </Link>
            )}
          </div>
          <div className="mt-4 space-y-3">
            {displayedJobs.map((j, idx) => (
              <div
                key={idx}
                className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
              >
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-primary-700">{j.company_name ?? j.provider}</p>
                  <h3 className="text-lg font-bold text-slate-900 hover:underline">
                    <Link to={`/jobs/${j.id}`}>{j.title}</Link>
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                    {j.location && <span className="rounded-full bg-slate-100 px-3 py-1">{j.location}</span>}
                    {j.provider && <span className="rounded-full bg-slate-100 px-3 py-1">{j.provider}</span>}
                    {j.posted_date && (
                      <span className="rounded-full bg-slate-100 px-3 py-1">
                        {new Date(j.posted_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {!jobs.length && !loading && <p className="text-sm text-slate-600">채용공고가 없습니다.</p>}
          </div>
        </section>
      )}

      {showBootcampSection && (
        <section>
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">부트캠프 ({bootcamps.length})</h2>
            {bootcamps.length > 5 && view !== 'bootcamps' && (
              <Link
                to={buildViewUrl('bootcamps')}
                className="text-sm font-semibold text-primary-700 hover:text-primary-800"
              >
                전체보기
              </Link>
            )}
          </div>
          <div className="mt-4 space-y-3">
            {displayedBootcamps.map((b, idx) => (
              <div
                key={idx}
                className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
              >
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-primary-700">{b.institute_name}</p>
                  <h3 className="text-lg font-bold text-slate-900 hover:underline">
                    <Link to={`/bootcamps/${b.id}`}>{b.title}</Link>
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                    {b.location && <span className="rounded-full bg-slate-100 px-3 py-1">{b.location}</span>}
                    {b.start_date && (
                      <span className="rounded-full bg-slate-100 px-3 py-1">
                        {new Date(b.start_date).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {!bootcamps.length && !loading && <p className="text-sm text-slate-600">부트캠프가 없습니다.</p>}
          </div>
        </section>
      )}
    </div>
  )
}

export default SearchResultsPage
