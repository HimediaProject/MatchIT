import { useMemo, useState } from 'react'

type Job = {
  id: string
  company: string
  position: string
  category: string
  skills: string[]
  location: string
  salary: string
  experience: '신입' | '1~3년' | '3~5년' | '5년+'
}

const jobCategories = ['백엔드', '프론트엔드', '데이터', 'AI', '모바일']
const jobStacks = ['Python', 'React', 'TypeScript', 'SQL', 'Java', 'Node.js']
const experienceFilters: Job['experience'][] = ['신입', '1~3년', '3~5년', '5년+']

const jobsSeed: Job[] = [
  {
    id: 'job-1',
    company: '핀테크 스타트업',
    position: '백엔드 엔지니어',
    category: '백엔드',
    skills: ['Python', 'Django', 'SQL'],
    location: '서울 · 송파',
    salary: '연 4,500만~6,000만원',
    experience: '1~3년',
  },
  {
    id: 'job-2',
    company: '커머스 스케일업',
    position: '프론트엔드 엔지니어',
    category: '프론트엔드',
    skills: ['React', 'TypeScript', 'Node.js'],
    location: '서울 · 강남',
    salary: '연 5,000만~7,000만원',
    experience: '3~5년',
  },
  {
    id: 'job-3',
    company: '데이터 플랫폼사',
    position: '데이터 분석가',
    category: '데이터',
    skills: ['Python', 'SQL', 'Tableau'],
    location: '전국 · 리모트',
    salary: '연 4,000만~5,500만원',
    experience: '신입',
  },
  {
    id: 'job-4',
    company: 'AI 리서치랩',
    position: '머신러닝 엔지니어',
    category: 'AI',
    skills: ['Python', 'PyTorch', 'LLM'],
    location: '서울 · 성수',
    salary: '연 6,000만~8,500만원',
    experience: '5년+',
  },
]

const JobsPage = () => {
  const [selectedCategories, setSelectedCategories] = useState<Set<string>>(new Set())
  const [selectedStacks, setSelectedStacks] = useState<Set<string>>(new Set())
  const [selectedExperience, setSelectedExperience] = useState<Job['experience'] | ''>('')
  const [sort, setSort] = useState<'latest' | 'deadline' | 'salary'>('latest')

  const toggleSet = (value: string, setter: React.Dispatch<React.SetStateAction<Set<string>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  const filteredJobs = useMemo(() => {
    const sorted = [...jobsSeed].sort((a, b) => {
      if (sort === 'salary') return b.salary.localeCompare(a.salary)
      return a.id.localeCompare(b.id)
    })

    return sorted.filter((job) => {
      const categoryMatch = selectedCategories.size ? selectedCategories.has(job.category) : true
      const stackMatch = selectedStacks.size ? job.skills.some((skill) => selectedStacks.has(skill)) : true
      const expMatch = selectedExperience ? job.experience === selectedExperience : true
      return categoryMatch && stackMatch && expMatch
    })
  }, [selectedCategories, selectedExperience, selectedStacks, sort])

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">채용 리스트</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">맞춤 채용공고 모아보기</h1>
          <p className="text-sm text-slate-600">
            필터를 조합해 원하는 포지션을 빠르게 찾으세요. 추후 API 연동으로 실제 데이터가 노출됩니다.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[260px_1fr]">
          <aside className="rounded-2xl border border-slate-100 bg-slate-50/80 p-5 shadow-soft">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">직무 카테고리</h3>
                <div className="mt-3 space-y-2">
                  {jobCategories.map((cat) => (
                    <label key={cat} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedCategories.has(cat)}
                        onChange={() => toggleSet(cat, setSelectedCategories)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {cat}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">기술 스택</h3>
                <div className="mt-3 space-y-2">
                  {jobStacks.map((stack) => (
                    <label key={stack} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedStacks.has(stack)}
                        onChange={() => toggleSet(stack, setSelectedStacks)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {stack}
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
                        className="h-4 w-4 border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {exp}
                    </label>
                  ))}
                  <button
                    onClick={() => setSelectedExperience('')}
                    className="mt-2 text-xs font-semibold text-primary-700 underline underline-offset-2"
                  >
                    경력 필터 초기화
                  </button>
                </div>
              </div>
            </div>
          </aside>

          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">
                총 {filteredJobs.length}건 · 정렬
              </p>
              <div className="flex items-center gap-2 text-sm text-slate-700">
                <select
                  value={sort}
                  onChange={(e) => setSort(e.target.value as typeof sort)}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-primary-300 focus:outline-none focus:ring-2 focus:ring-primary-100"
                >
                  <option value="latest">최신순</option>
                  <option value="deadline">마감임박</option>
                  <option value="salary">연봉 높은 순</option>
                </select>
              </div>
            </div>

            <div className="space-y-4">
              {filteredJobs.map((job) => (
                <div
                  key={job.id}
                  className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-primary-700">{job.company}</p>
                    <h3 className="text-lg font-bold text-slate-900">{job.position}</h3>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.category}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.location}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.salary}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{job.experience}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {job.skills.map((skill) => (
                        <span
                          key={skill}
                          className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto">
                    상세 보기
                  </button>
                </div>
              ))}
              {!filteredJobs.length && (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                  조건에 맞는 공고가 없습니다. 필터를 조정하거나 초기화해주세요.
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
    </div>
  )
}

export default JobsPage
