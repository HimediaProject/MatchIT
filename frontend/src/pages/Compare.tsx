import { useMemo, useState } from 'react'

type ComparedJob = {
  id: string
  company: string
  position: string
  stack: string
  salary: string
  workType: string
}

type ComparedBootcamp = {
  id: string
  provider: string
  course: string
  curriculum: string
  price: string
  mode: string
}

const jobSelections: ComparedJob[] = [
  {
    id: 'cj-1',
    company: '핀테크 스타트업',
    position: '백엔드 엔지니어',
    stack: 'Python · Django · PostgreSQL',
    salary: '연 4,500만~6,000만원',
    workType: '하이브리드',
  },
  {
    id: 'cj-2',
    company: '커머스 스케일업',
    position: '프론트엔드 엔지니어',
    stack: 'React · TypeScript · Node',
    salary: '연 5,000만~7,000만원',
    workType: '오피스',
  },
]

const bootcampSelections: ComparedBootcamp[] = [
  {
    id: 'cb-1',
    provider: '스쿨 A',
    course: '데이터 분석 입문',
    curriculum: 'Python · SQL · Tableau',
    price: '국비',
    mode: '온라인',
  },
  {
    id: 'cb-2',
    provider: '랩 B',
    course: 'AI 서비스 구축',
    curriculum: 'LLM · MLOps · RAG',
    price: '250만원',
    mode: '오프라인',
  },
]

const ComparePage = () => {
  const [mode, setMode] = useState<'jobs' | 'bootcamps'>('jobs')

  const currentSelections = useMemo(
    () => (mode === 'jobs' ? jobSelections : bootcampSelections),
    [mode],
  )

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">비교 페이지</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">채용/부트캠프 나란히 비교</h1>
          <p className="text-sm text-slate-600">
            리스트에서 선택한 항목을 테이블로 비교하세요. 지금은 더미 데이터로 예시를 제공합니다.
          </p>
        </div>

        <div className="mt-6 flex items-center gap-3">
          <button
            onClick={() => setMode('jobs')}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              mode === 'jobs'
                ? 'bg-primary-600 text-white shadow-soft'
                : 'border border-slate-200 bg-white text-slate-800'
            }`}
          >
            채용 비교
          </button>
          <button
            onClick={() => setMode('bootcamps')}
            className={`rounded-full px-4 py-2 text-sm font-semibold ${
              mode === 'bootcamps'
                ? 'bg-primary-600 text-white shadow-soft'
                : 'border border-slate-200 bg-white text-slate-800'
            }`}
          >
            부트캠프 비교
          </button>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-100 bg-slate-50/70 p-4 text-sm text-slate-600">
          리스트에서 채용/부트캠프를 선택하면 이곳에서 나란히 비교할 수 있습니다.
        </div>

        <div className="mt-6 space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            {currentSelections.map((item) => (
              <span
                key={item.id}
                className="rounded-full bg-white px-3 py-1 text-xs font-semibold text-slate-800 ring-1 ring-slate-200"
              >
                {mode === 'jobs' ? (item as ComparedJob).position : (item as ComparedBootcamp).course}
              </span>
            ))}
          </div>

          {!currentSelections.length && (
            <div className="rounded-2xl border border-dashed border-slate-200 bg-white p-6 text-sm text-slate-600">
              선택된 항목이 없습니다. 리스트에서 항목을 추가해주세요.
            </div>
          )}

          {currentSelections.length > 0 && (
            <div className="overflow-x-auto rounded-2xl border border-slate-100 bg-white shadow-soft">
              <table className="min-w-full divide-y divide-slate-100 text-sm">
                <thead className="bg-slate-50/80">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold text-slate-900">항목</th>
                    {currentSelections.map((item) => (
                      <th key={item.id} className="px-4 py-3 text-left font-semibold text-slate-900">
                        {mode === 'jobs'
                          ? (item as ComparedJob).position
                          : (item as ComparedBootcamp).course}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {mode === 'jobs' ? (
                    <>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">회사</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 font-semibold text-slate-900">
                            {(item as ComparedJob).company}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">기술 스택</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedJob).stack}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">연봉</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedJob).salary}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">근무 형태</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedJob).workType}
                          </td>
                        ))}
                      </tr>
                    </>
                  ) : (
                    <>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">기관</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 font-semibold text-slate-900">
                            {(item as ComparedBootcamp).provider}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">커리큘럼</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedBootcamp).curriculum}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">수강료</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedBootcamp).price}
                          </td>
                        ))}
                      </tr>
                      <tr>
                        <td className="px-4 py-3 text-slate-600">수업 형태</td>
                        {currentSelections.map((item) => (
                          <td key={item.id} className="px-4 py-3 text-slate-800">
                            {(item as ComparedBootcamp).mode}
                          </td>
                        ))}
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ComparePage
