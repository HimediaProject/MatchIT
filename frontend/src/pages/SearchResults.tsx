import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { searchApi } from '../services/apiService'

function useQuery() {
  return new URLSearchParams(useLocation().search)
}

const SearchResultsPage = () => {
  const query = useQuery()
  const keyword = query.get('keyword') || ''

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jobs, setJobs] = useState<any[]>([])
  const [bootcamps, setBootcamps] = useState<any[]>([])

  useEffect(() => {
    if (!keyword) return
    setLoading(true)
    setError(null)
    searchApi
      .search(keyword)
      .then((data) => {
        setJobs(data.jobs || [])
        setBootcamps(data.bootcamps || [])
      })
      .catch((err) => setError(err.message || '검색 중 오류가 발생했습니다'))
      .finally(() => setLoading(false))
  }, [keyword])

  return (
    <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">검색 결과</h1>
        <p className="text-sm text-slate-600">키워드: <strong>{keyword}</strong></p>
      </div>

      {loading && <p>검색 중...</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}

      <section className="mb-8">
        <h2 className="text-lg font-semibold">채용공고 ({jobs.length})</h2>
        <div className="mt-4 space-y-3">
          {jobs.map((j, idx) => (
            <div key={idx} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-primary-700">{j.provider}</p>
                  <h3 className="text-lg font-bold">{j.title}</h3>
                  <p className="text-sm text-slate-600">{j.company_name} • {j.location}</p>
                </div>
                <div className="text-sm text-slate-500">{j.posted_date ? new Date(j.posted_date).toLocaleDateString() : ''}</div>
              </div>
              <p className="mt-2 text-sm text-slate-700">{j.main_tasks ? j.main_tasks.slice(0, 200) + (j.main_tasks.length > 200 ? '...' : '') : ''}</p>
            </div>
          ))}
          {!jobs.length && !loading && <p className="text-sm text-slate-600">채용공고가 없습니다.</p>}
        </div>
      </section>

      <section>
        <h2 className="text-lg font-semibold">부트캠프 ({bootcamps.length})</h2>
        <div className="mt-4 space-y-3">
          {bootcamps.map((b, idx) => (
            <div key={idx} className="rounded-lg border p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-primary-700">{b.institute_name}</p>
                  <h3 className="text-lg font-bold">{b.title}</h3>
                  <p className="text-sm text-slate-600">{b.location}</p>
                </div>
                <div className="text-sm text-slate-500">{b.start_date ? new Date(b.start_date).toLocaleDateString() : ''}</div>
              </div>
              <p className="mt-2 text-sm text-slate-700">{b.education_content ? b.education_content.slice(0, 200) + (b.education_content.length > 200 ? '...' : '') : ''}</p>
            </div>
          ))}
          {!bootcamps.length && !loading && <p className="text-sm text-slate-600">부트캠프가 없습니다.</p>}
        </div>
      </section>
    </div>
  )
}

export default SearchResultsPage
