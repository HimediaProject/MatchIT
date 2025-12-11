import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchJobDetail, type JobPost } from '../api/jobposts'

const JobDetail = () => {
  const { jobId } = useParams()

  const navigate = useNavigate()

  if (!jobId) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-red-600">잘못된 공고 ID입니다.</p>
      </div>
    )
  }

  const id = Number(jobId)

  const {
    data: job, 
    isLoading,
    isError, 
    error,  
  } = useQuery({
    queryKey: ['jobDetail', id],  
    queryFn: () => fetchJobDetail(id),  
    enabled: !!id,  
  })

  if (isLoading) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-slate-700">공고 정보를 불러오는 중입니다...</p>
      </div>
    )
  }

  if (isError) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-red-600">
          공고 로딩 실패: {(error as any)?.message ?? '알 수 없는 에러'}
        </p>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-slate-700">해당 공고를 찾을 수 없습니다.</p>
      </div>
    )
  }

  // 최근 열람 공고 로컬 저장 (최신 3개 유지)
  useEffect(() => {
    try {
      const key = 'recentViews'
      const raw = localStorage.getItem(key)
      const arr: string[] = raw ? JSON.parse(raw) : []
      const title = job.Title || `${job.CompanyName} ${job.Title}`
      // remove existing
      const filtered = arr.filter((t) => t !== title)
      filtered.unshift(title)
      const limited = filtered.slice(0, 3)
      localStorage.setItem(key, JSON.stringify(limited))
    } catch (e) {
      // ignore storage errors
    }
  }, [job])

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-4xl px-4 py-12 md:px-6">
        {/* 뒤로 가기 */}
        <div className="mb-6">
          <Link
            to="/jobs"
            className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 transition"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            채용공고 목록으로
          </Link>
        </div>

        {/* 헤더 섹션 */}
        <div className="mb-8 space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-sm text-slate-500">
              조회수 {job.ViewCount.toLocaleString()}
            </span>
          </div>

          <p className="text-sm font-semibold text-primary-700">
            {job.CompanyName}
          </p>

          <h1 className="mt-1 text-3xl font-bold text-slate-900">
            {job.Title}
          </h1>
        </div>

        {/* 기본 정보 카드 */}
        <div className="mb-6 rounded-2xl border border-slate-100 bg-slate-50/80 p-6 shadow-soft">
          <h2 className="mb-4 text-lg font-bold text-slate-900">기본 정보</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            {job.Location && (
              <div>
                <p className="text-sm font-semibold text-slate-700 mb-1">근무지역</p>
                <p className="text-sm text-slate-600">{job.Location}</p>
              </div>
            )}
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-1">경력</p>
              <p className="text-sm text-slate-600">{job.ExperienceRequirement ?? '경력 무관'}</p>
            </div>
            {job.EmploymentType && (
              <div>
                <p className="text-sm font-semibold text-slate-700 mb-1">고용 형태</p>
                <p className="text-sm text-slate-600">{job.EmploymentType}</p>
              </div>
            )}
          </div>
          <div className="mt-6 flex items-center gap-3">
            {/* 스크랩 버튼 */}
            <button 
              type="button"
              className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border border-slate-200 bg-white text-slate-400 transition hover:bg-slate-50 hover:text-slate-600"
              aria-label="스크랩"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
              </svg>
            </button>

            {/* 공유하기 버튼 */}
            <button 
              type="button"
              className="h-12 flex-1 rounded-xl bg-primary-50 text-base font-bold text-primary-700 transition hover:bg-primary-100"
            >
              공유하기
            </button>

            {/* 지원하기 버튼 */}
            <a
              href={job.Url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex h-12 flex-1 items-center justify-center rounded-xl bg-primary-600 text-base font-bold text-white shadow-sm transition hover:bg-primary-700"
            >
              지원하기
            </a>
          </div>
        </div>

        {/* 스킬 태그 */}
        <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
          <h2 className="mb-4 text-lg font-bold text-slate-900">기술 스택</h2>
          <div className="flex flex-wrap gap-2">
            {job.Skills.length > 0 ? (
              job.Skills.map((skill) => (
                <span
                  key={skill}
                  className="rounded-full bg-primary-50 px-3 py-1 text-sm font-semibold text-primary-700"
                >
                  {skill}
                </span>
              ))
            ) : (
              <p className="text-sm text-slate-500">기술 스택 정보가 없습니다.</p>
            )}
          </div>
        </div>

        {/* 본문 정보 섹션들 */}
        <div className="space-y-6">
          {/* 주요 업무 */}
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">주요 업무</h2>
            <div className="prose prose-sm max-w-none">
              {job.MainTasks ? (
                <div className="space-y-2 text-sm text-slate-600 leading-relaxed">
                  {job.MainTasks.split(/[-•*\u2022]/)
                    .filter(item => item.trim())
                    .map((item, index) => (
                      <div key={index} className="break-keep">
                        {item.trim()}
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">주요 업무 정보가 없습니다.</p>
              )}
            </div>
          </div>

          {/* 자격 요건 */}
          <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">자격 요건</h2>
            <div className="prose prose-sm max-w-none">
              {job.Qualifications ? (
                <div className="space-y-2 text-sm text-slate-600 leading-relaxed">
                  {job.Qualifications.split(/[-•*\u2022]/)
                    .filter(item => item.trim())
                    .map((item, index) => (
                      <div key={index} className="break-keep">
                        {item.trim()}
                      </div>
                    ))}
                </div>
              ) : (
                <p className="text-sm text-slate-500">자격 요건 정보가 없습니다.</p>
              )}
            </div>
          </div>

          {/* 우대 사항 */}
          {job.Preferences && (
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
              <h2 className="mb-4 text-lg font-bold text-slate-900">우대 사항</h2>
              <div className="prose prose-sm max-w-none">
                <div className="space-y-2 text-sm text-slate-600 leading-relaxed">
                  {job.Preferences.split(/[-•*\u2022]/)
                    .filter(item => item.trim())
                    .map((item, index) => (
                      <div key={index} className="break-keep">
                        {item.trim()}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}

          {/* 복지 / 혜택 */}
          {job.Benefits && (
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
              <h2 className="mb-4 text-lg font-bold text-slate-900">복지 / 혜택</h2>
              <div className="prose prose-sm max-w-none">
                <div className="space-y-2 text-sm text-slate-600 leading-relaxed">
                  {job.Benefits.split(/[-•*\u2022]/)
                    .filter(item => item.trim())
                    .map((item, index) => (
                      <div key={index} className="break-keep">
                        {item.trim()}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default JobDetail
