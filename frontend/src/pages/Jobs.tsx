import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchCategories, fetchJobList, fetchSkills, type JobPost } from '../api/jobposts'

const experienceFilters = ['신입', '1~3년', '3~5년', '5년 이상']

const JobsPage = () => {
  const [selectedCategories, setSelectedCategories] = useState<Set<number>>(new Set())
  const [selectedStacks, setSelectedStacks] = useState<Set<string>>(new Set())
  const [selectedExperience, setSelectedExperience] = useState<string>('')

  const [sort, setSort] = useState<'created' | 'deadline' | 'views'>('created')

  const [page, setPage] = useState<number>(1)
  const size = 10

  const getInitialCompare = () => {
    try {
      if (typeof window === 'undefined') return []
      const raw = localStorage.getItem('compare_jobs')
      return raw ? (JSON.parse(raw) as JobPost[]) : []
    } catch {
      return []
    }
  }

  const [compareList, setCompareList] = useState<JobPost[]>(getInitialCompare)

  useEffect(() => {
    try {
      localStorage.setItem('compare_jobs', JSON.stringify(compareList))
    } catch {}
  }, [compareList])

  const navigate = useNavigate()

  const { data: categories } = useQuery({
    queryKey: ['jobCategories'],
    queryFn: fetchCategories,
  })

  const { data: skills } = useQuery({
    queryKey: ['jobSkills'],
    queryFn: fetchSkills,
  })

  const skillList = Array.isArray(skills) ? skills : []

  const categoryOptions = useMemo(
    () => categories?.map((c) => ({ id: c.CategoryID, name: c.CategoryName })) ?? [],
    [categories],
  )

  const categoryIds = useMemo(
    () => Array.from(selectedCategories).sort((a, b) => a - b),
    [selectedCategories],
  )

  const experienceParams = useMemo(() => {
    switch (selectedExperience) {
      case experienceFilters[0]:
        return { experience_requirement: '신입', experience_min: 0, experience_max: 0 }
      case experienceFilters[1]:
        return { experience_requirement: '경력', experience_min: 1, experience_max: 3 }
      case experienceFilters[2]:
        return { experience_requirement: '경력', experience_min: 3, experience_max: 5 }
      case experienceFilters[3]:
        return { experience_requirement: '경력', experience_min: 5, experience_max: null }
      default:
        return { experience_requirement: undefined, experience_min: undefined, experience_max: undefined }
    }
  }, [selectedExperience])

  const { data, isLoading, isError, error } = useQuery({
    queryKey: [
      'jobList',
      page,
      sort,
      categoryIds,
      experienceParams.experience_requirement,
      experienceParams.experience_min,
      experienceParams.experience_max,
    ],
    queryFn: () =>
      fetchJobList({
        page,
        size,
        sort,
        category_ids: categoryIds.length ? categoryIds : undefined,
        experience_requirement: experienceParams.experience_requirement,
        experience_min: experienceParams.experience_min,
        experience_max: experienceParams.experience_max,
      }),
    keepPreviousData: true,
  })

  const jobs = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.max(1, Math.ceil(total / size))
  const chunkStart = Math.floor((page - 1) / 5) * 5 + 1
  const chunkEnd = Math.min(chunkStart + 4, totalPages)

  const toggleSet = <T,>(value: T, setter: React.Dispatch<React.SetStateAction<Set<T>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  const addToCompare = (job: JobPost) => {
    setCompareList((prev) => {
      if (prev.find((j) => j.PostID === job.PostID)) {
        window.alert('이미 비교 목록에 있는 채용입니다.')
        return prev
      }
      if (prev.length >= 3) {
        window.alert('최대 3개까지만 비교할 수 있습니다.')
        return prev
      }
      return [...prev, job]
    })
  }

  const removeFromCompare = (id: number) => {
    setCompareList((prev) => prev.filter((j) => j.PostID !== id))
  }

  const clearCompare = () => setCompareList([])

  const parseDateValue = (value?: string | null) => {
    if (!value) return null
    const ts = Date.parse(value)
    return Number.isNaN(ts) ? null : ts
  }

  const parseSalaryValue = (salary?: string | null) => {
    if (!salary) return null
    const matches = salary.match(/\d+/g)
    if (!matches) return null
    const nums = matches.map((n) => parseInt(n, 10)).filter((n) => !Number.isNaN(n))
    if (!nums.length) return null
    return Math.max(...nums)
  }

  const compareWithNulls = (a: number | null, b: number | null, direction: 'asc' | 'desc') => {
    if (a === null && b === null) return 0
    if (a === null) return 1
    if (b === null) return -1
    return direction === 'asc' ? a - b : b - a
  }

  const filteredJobs = useMemo(() => {
    return jobs.filter((job) => {
      const categoryMatch = selectedCategories.size ? selectedCategories.has(job.JobCategoryID) : true

      const stackMatch = selectedStacks.size
        ? job.Skills.some((s) => selectedStacks.has(s))
        : true

      const { experience_requirement, experience_min, experience_max } = experienceParams
      const expMatch = selectedExperience
        ? (() => {
            if (experience_requirement === '신입') {
              return job.ExperienceRequirement === '신입'
            }
            const meetsRequirement = job.ExperienceRequirement === '경력'
            const minYears = job.MinExperienceYears
            const minOk =
              experience_min === undefined || experience_min === null || minYears === null || minYears === undefined
                ? true
                : minYears >= experience_min
            const maxOk =
              experience_max === undefined || experience_max === null || minYears === null || minYears === undefined
                ? true
                : minYears <= experience_max
            return meetsRequirement && minOk && maxOk
          })()
        : true

      return categoryMatch && stackMatch && expMatch
    })
  }, [jobs, selectedCategories, selectedStacks, selectedExperience, experienceParams])

  const sortedJobs = useMemo(() => {
    const list = [...filteredJobs]
    list.sort((a, b) => {
      if (sort === 'created') {
        const aTs = parseDateValue(a.PostedDate) ?? parseDateValue(a.CreatedAt)
        const bTs = parseDateValue(b.PostedDate) ?? parseDateValue(b.CreatedAt)
        return compareWithNulls(aTs, bTs, 'desc')
      }

      if (sort === 'deadline') {
        const aDeadline = parseDateValue(a.CloseDate)
        const bDeadline = parseDateValue(b.CloseDate)
        return compareWithNulls(aDeadline, bDeadline, 'asc')
      }

      const aViews = a.ViewCount ?? null
      const bViews = b.ViewCount ?? null
      return compareWithNulls(aViews, bViews, 'desc')
    })
    return list
  }, [filteredJobs, sort])

  if (isLoading) {
    return <div className="flex justify-center py-10">채용을 불러오는 중입니다...</div>
  }

  if (isError) {
    return <div className="py-10 text-red-500">API 오류: {(error as any)?.message}</div>
  }

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">실시간 채용 목록</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">맞춤 수집된 테크 채용</h1>
          <p className="text-sm text-slate-600">빠른 쿼리는 곧 FastAPI /jobs 엔드포인트와 연결될 예정입니다.</p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[260px_1fr]">
          {/* 필터 */}
          <aside className="rounded-2xl border border-slate-100 bg-slate-50/80 p-5 shadow-soft">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">분야</h3>
                <div className="mt-3 space-y-2">
                  {categoryOptions.map((cat) => (
                    <label key={cat.id} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedCategories.has(cat.id)}
                        onChange={() => toggleSet(cat.id, setSelectedCategories)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600"
                      />
                      {cat.name}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">스택</h3>
                <div className="mt-3 space-y-2">
                  {skillList.map((skill) => (
                    <label key={skill} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedStacks.has(skill)}
                        onChange={() => toggleSet(skill, setSelectedStacks)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600"
                      />
                      {skill}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">경력</h3>
                <div className="mt-3 space-y-2">
                  {experienceFilters.map((exp) => (
                    <label key={exp} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="radio"
                        name="exp"
                        value={exp}
                        checked={selectedExperience === exp}
                        onChange={() => setSelectedExperience(exp)}
                        className="h-4 w-4 border-slate-300 text-primary-600"
                      />
                      {exp}
                    </label>
                  ))}
                  <button
                    onClick={() => setSelectedExperience('')}
                    className="mt-2 text-xs font-semibold text-primary-700 underline"
                  >
                    경력 필터 초기화
                  </button>
                </div>
              </div>
            </div>
          </aside>

          {/* 목록 */}
          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">결과 {filteredJobs.length}건</p>

              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as any)}
                className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
              >
                <option value="created">최신 등록순</option>
                <option value="deadline">마감일</option>
                <option value="views">조회수</option>
              </select>
            </div>

            <div className="space-y-4">
              {sortedJobs.map((job) => (
                <div
                  key={job.PostID}
                  className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-primary-700">{job.CompanyName}</p>
                    <h3
                      onClick={() => navigate(`/jobs/${job.PostID}`)}
                      className="text-lg font-bold text-slate-900 cursor-pointer hover:underline"
                    >
                      {job.Title}
                    </h3>

                    <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.Location}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">
                        {job.ExperienceRequirement ?? '경력 무관'}
                      </span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">조회수 {job.ViewCount}</span>
                    </div>

                    <div className="mt-2 flex flex-wrap gap-2">
                      {job.Skills.map((skill) => (
                        <span
                          key={skill}
                          className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        addToCompare(job)
                      }}
                      className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 hover:bg-primary-50 md:w-[140px] md:justify-center"
                    >
                      {compareList.find((j) => j.PostID === job.PostID) ? '추가됨' : '비교 담기'}
                    </button>
                  </div>
                </div>
              ))}

              {!filteredJobs.length && (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                  조건에 맞는 채용이 없습니다. 필터를 조정해 다시 확인해주세요.
                </div>
              )}
            </div>

            {/* 고급 페이지네이션: 1~5 / 6~10 단위 */}
            {totalPages > 1 && (
              <div className="mt-8 flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-100 bg-white p-4 shadow-soft">
                <div className="flex items-center gap-2">
                  <button
                    disabled={page === 1}
                    onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                    className="rounded-full border border-slate-200 px-3 py-1 text-sm font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50"
                  >
                    이전
                  </button>

                  <div className="flex items-center gap-1">
                    {Array.from({ length: chunkEnd - chunkStart + 1 }, (_, idx) => chunkStart + idx).map((p) => (
                      <button
                        key={p}
                        onClick={() => setPage(p)}
                        className={`h-9 w-9 rounded-full text-sm font-semibold ${
                          p === page
                            ? 'bg-primary-600 text-white shadow-soft'
                            : 'border border-slate-200 bg-white text-slate-700 hover:border-primary-200 hover:text-primary-700'
                        }`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>

                  <button
                    disabled={page === totalPages}
                    onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                    className="rounded-full border border-slate-200 px-3 py-1 text-sm font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50"
                  >
                    다음
                  </button>
                </div>

                <div className="flex items-center gap-2 text-xs text-slate-600">
                  <button
                    disabled={chunkStart === 1}
                    onClick={() => setPage((prev) => Math.max(1, prev - 5))}
                    className="rounded-full border border-slate-200 px-3 py-1 font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50"
                  >
                    ◀ 1~5
                  </button>
                  <span className="text-slate-500">|</span>
                  <button
                    disabled={chunkEnd === totalPages}
                    onClick={() => setPage((prev) => Math.min(totalPages, chunkStart + 5))}
                    className="rounded-full border border-slate-200 px-3 py-1 font-semibold text-slate-700 disabled:opacity-40 hover:bg-slate-50"
                  >
                    6~10 ▶
                  </button>
                  <span className="text-slate-500">총 {totalPages} 페이지</span>
                </div>
              </div>
            )}
          </section>
        </div>
      </div>

      {/* 비교함 */}
      {compareList.length > 0 && (
        <aside className="fixed right-6 top-24 z-50 w-80 max-h-[70vh] overflow-auto rounded-2xl border border-slate-100 bg-white p-4 shadow-lg">
          <div className="mb-3 flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-900">비교함 ({compareList.length}/3)</h4>
            <button onClick={clearCompare} className="text-xs font-semibold text-red-600 hover:underline">
              전체삭제
            </button>
          </div>

          <div className="space-y-3">
            {compareList.map((item) => (
              <div key={item.PostID} className="flex items-start justify-between gap-2 rounded-lg border p-2">
                <div>
                  <p className="text-xs font-semibold text-primary-700">{item.CompanyName}</p>
                  <p className="text-sm font-bold text-slate-900">{item.Title}</p>
                  <p className="text-xs text-slate-600">조회수 {item.ViewCount}</p>
                </div>

                <button
                  onClick={() => removeFromCompare(item.PostID)}
                  className="whitespace-nowrap text-xs font-semibold text-primary-700 hover:underline flex-shrink-0"
                >
                  삭제
                </button>
              </div>
            ))}
          </div>

          <div className="mt-3 flex justify-end">
            <button
              onClick={() => {
                const ids = compareList.map((j) => j.PostID).join(',')
                navigate(`/compare?mode=jobs&ids=${encodeURIComponent(ids)}`)
              }}
              className="rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white hover:bg-primary-700"
            >
              비교하기
            </button>
          </div>
        </aside>
      )}
    </div>
  )
}

export default JobsPage
