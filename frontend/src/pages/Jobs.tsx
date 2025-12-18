import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchCategories, fetchJobList, fetchSkills, type JobPost } from '../api/jobposts'
import { SortOption } from '../api/sortoption'
import { usersApi } from '../api/users'

const experienceFilters = ['신입', '1~3년', '3~5년', '5년 이상']

const JobsPage = () => {
  const [selectedCategories, setSelectedCategories] = useState<Set<number>>(new Set())
  const [selectedStacks, setSelectedStacks] = useState<Set<string>>(new Set())
  const [selectedExperience, setSelectedExperience] = useState<string>('')

  const [sort, setSort] = useState<SortOption>('created')

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
  const [scrappedIds, setScrappedIds] = useState<Set<number>>(new Set())
  const [scrapLoadingIds, setScrapLoadingIds] = useState<Set<number>>(new Set())

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

  // Bootcamps.tsx와 동일한 페이지 번호 계산 (ellipsis 스타일)
  const getPageNumbers = () => {
    const pages: number[] = []
    const maxVisible = 5

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else {
      if (page <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push(-1 as unknown as number) // ... 표시용
        pages.push(totalPages)
      } else if (page >= totalPages - 2) {
        pages.push(1)
        pages.push(-1 as unknown as number)
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push(-1 as unknown as number)
        pages.push(page - 1)
        pages.push(page)
        pages.push(page + 1)
        pages.push(-1 as unknown as number)
        pages.push(totalPages)
      }
    }
    return pages
  }

  const toggleSet = <T,>(value: T, setter: React.Dispatch<React.SetStateAction<Set<T>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  const resetAllFilters = () => {
    setSelectedCategories(new Set())
    setSelectedStacks(new Set())
    setSelectedExperience('')
    setPage(1)
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

  useEffect(() => {
    let mounted = true
    const load = async () => {
      try {
        const scraps = await usersApi.getMyScraps()
        if (!Array.isArray(scraps)) return
        const ids = new Set<number>()
        scraps.forEach((s: any) => {
          if (s?.post_type === 'Job' && s?.job_post_id) ids.add(Number(s.job_post_id))
        })
        if (mounted) setScrappedIds(ids)
      } catch {
        // ignore
      }
    }
    load()
    return () => { mounted = false }
  }, [])

  const toggleScrapForJob = async (jobId: number) => {
    if (scrapLoadingIds.has(jobId)) return
    setScrapLoadingIds((prev) => new Set(prev).add(jobId))
    try {
      if (scrappedIds.has(jobId)) {
        await usersApi.removeMyScrap('Job', jobId)
        setScrappedIds((prev) => {
          const next = new Set(prev)
          next.delete(jobId)
          return next
        })
      } else {
        await usersApi.addMyScrap('Job', jobId)
        setScrappedIds((prev) => new Set(prev).add(jobId))
      }
    } catch (e) {
      const msg = String((e as any)?.message ?? e)
      if (msg.includes('401') || msg.includes('403')) {
        if (window.confirm('로그인이 필요합니다. 로그인 페이지로 이동할까요?')) {
          navigate('/login')
        }
      } else {
        window.alert('스크랩 처리에 실패했습니다.')
      }
    } finally {
      setScrapLoadingIds((prev) => {
        const next = new Set(prev)
        next.delete(jobId)
        return next
      })
    }
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
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">내게 맞는 채용공고 찾아보기</h1>
          <p className="text-sm text-slate-600">기술 스택과 경력에 맞춰 전국의 핫한 테크 채용 공고를 한 번에 확인하세요.</p>
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
                    onClick={resetAllFilters}
                    className="mt-2 text-xs font-semibold text-primary-700 underline"
                  >
                    필터 전체 초기화
                  </button>
                </div>
              </div>
            </div>
          </aside>

          {/* 목록 */}
          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">
                총 {total}건
              </p>
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
                    <h3 className="text-lg font-bold text-slate-900 hover:text-primary-600 transition-colors">
                      <a
                        href={`/jobs/${job.PostID}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="cursor-pointer"
                      >
                        {job.Title}
                      </a>
                    </h3>

                    <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.Location}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">
                        {job.ExperienceRequirement ?? '경력 무관'}
                      </span>
                      {(job.Skills ?? []).map((skill: string) => (
                        <span key={skill} className="rounded-full bg-slate-100 px-3 py-1">{skill}</span>
                      ))}
                    </div>
                    {(
                      job.MainTasks || job.Qualifications || job.Preferences || job.Benefits || job.Process
                    ) && (
                      <div className="mt-2">
                        <span className="text-xs text-slate-600">
                          <strong>마감일: {(job.CloseDate && job.CloseDate.split('T')[0]) || '상시'}</strong>
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="flex flex-col gap-2 md:flex-row md:items-center md:gap-3">
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleScrapForJob(job.PostID)
                      }}
                      disabled={scrapLoadingIds.has(job.PostID)}
                      className={`flex h-9 w-9 items-center justify-center rounded-md border transition ${scrappedIds.has(job.PostID) ? 'border-primary-200 bg-primary-50 text-primary-700' : 'border-slate-200 bg-white text-slate-400 hover:bg-slate-50 hover:text-slate-600'}`}
                      aria-label="스크랩"
                    >
                      <svg className="h-4 w-4" fill={scrappedIds.has(job.PostID) ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>
                    </button>

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

            {/* 페이지네이션 (Bootcamps.tsx 스타일) */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                  disabled={page === 1}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
                >
                  이전
                </button>

                {getPageNumbers().map((pageNum, idx) => {
                  if (pageNum === ( -1 as unknown as number)) {
                    return (
                      <span key={`ellipsis-${idx}`} className="px-2 text-slate-400">
                        ...
                      </span>
                    )
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`min-w-[40px] rounded-lg border px-3 py-2 text-sm font-medium transition ${
                        page === pageNum
                          ? 'border-primary-600 bg-primary-600 text-white'
                          : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}

                <button
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={page === totalPages}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
                >
                  다음
                </button>
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
