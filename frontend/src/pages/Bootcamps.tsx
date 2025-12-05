import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

type Bootcamp = {
  id: string
  name: string
  provider: string
  field: string
  mode: 'Online' | 'Offline' | 'Hybrid'
  price: string
  funding: 'Government' | 'Private'
  duration: string
  level: 'Beginner' | 'Intermediate' | 'Advanced'
  curriculum: string[]
}

const fields = ['백엔드', '데이터', 'AI', '프론트엔드', '클라우드']
const modes: Bootcamp['mode'][] = ['Online', 'Offline', 'Hybrid']
const fundings: Bootcamp['funding'][] = ['Government', 'Private']
const levels: Bootcamp['level'][] = ['Beginner', 'Intermediate', 'Advanced']

const bootcampsSeed: Bootcamp[] = [
  {
    id: 'boot-1',
    name: '데이터 분석 입문 캠프',
    provider: 'Campus A',
    field: '데이터',
    mode: 'Online',
    price: '무료',
    funding: 'Government',
    duration: '12주',
    level: 'Beginner',
    curriculum: ['Python', 'SQL', 'Tableau'],
  },
  {
    id: 'boot-2',
    name: 'AI 서비스 프로토타이핑',
    provider: 'Institute B',
    field: 'AI',
    mode: 'Offline',
    price: '250만원',
    funding: 'Private',
    duration: '10주',
    level: 'Intermediate',
    curriculum: ['LLM', 'MLOps', 'RAG'],
  },
  {
    id: 'boot-3',
    name: '풀스택 빌더 부트캠프',
    provider: 'CodeCamp C',
    field: '프론트엔드',
    mode: 'Hybrid',
    price: '180만원',
    funding: 'Private',
    duration: '14주',
    level: 'Beginner',
    curriculum: ['React', 'Node.js', 'Deploy'],
  },
  {
    id: 'boot-4',
    name: '클라우드 백엔드 인텐시브',
    provider: 'Campus D',
    field: '백엔드',
    mode: 'Online',
    price: '220만원',
    funding: 'Private',
    duration: '16주',
    level: 'Advanced',
    curriculum: ['Spring', 'AWS', 'CI/CD'],
  },
]

const BootcampsPage = () => {
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set())
  const [selectedModes, setSelectedModes] = useState<Set<Bootcamp['mode']>>(new Set())
  const [selectedFunding, setSelectedFunding] = useState<Set<Bootcamp['funding']>>(new Set())
  const [selectedLevels, setSelectedLevels] = useState<Set<Bootcamp['level']>>(new Set())

  const getInitialCompare = () => {
    try {
      if (typeof window === 'undefined') return []
      const raw = localStorage.getItem('compare_bootcamps')
      return raw ? (JSON.parse(raw) as Bootcamp[]) : []
    } catch {
      return []
    }
  }

  const [compareList, setCompareList] = useState<Bootcamp[]>(getInitialCompare)

  useEffect(() => {
    try {
      localStorage.setItem('compare_bootcamps', JSON.stringify(compareList))
    } catch {}
  }, [compareList])

  const navigate = useNavigate()

  const addToCompare = (boot: Bootcamp) => {
    setCompareList((prev) => {
      if (prev.find((b) => b.id === boot.id)) {
        window.alert('이미 비교 목록에 있는 부트캠프입니다.')
        return prev
      }
      if (prev.length >= 3) {
        window.alert('최대 3개까지만 비교할 수 있습니다.')
        return prev
      }
      return [...prev, boot]
    })
  }

  const removeFromCompare = (id: string) => setCompareList((prev) => prev.filter((b) => b.id !== id))

  const clearCompare = () => setCompareList([])

  const toggleSet = <T,>(value: T, setter: React.Dispatch<React.SetStateAction<Set<T>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  const filteredBootcamps = useMemo(() => {
    return bootcampsSeed.filter((boot) => {
      const fieldMatch = selectedFields.size ? selectedFields.has(boot.field) : true
      const modeMatch = selectedModes.size ? selectedModes.has(boot.mode) : true
      const fundingMatch = selectedFunding.size ? selectedFunding.has(boot.funding) : true
      const levelMatch = selectedLevels.size ? selectedLevels.has(boot.level) : true
      return fieldMatch && modeMatch && fundingMatch && levelMatch
    })
  }, [selectedFields, selectedFunding, selectedLevels, selectedModes])

  return (
    <div className="bg-white">
      <div className="mx-auto max-w-6xl px-4 py-12 md:px-6">
        <div className="flex flex-col gap-2">
          <p className="text-sm font-semibold text-primary-700">부트캠프 추천</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">나에게 맞는 부트캠프 찾기</h1>
          <p className="text-sm text-slate-600">
            분야, 운영 형태, 지원금, 난이도로 필터링해 계획에 맞는 프로그램을 빠르게 찾으세요.
          </p>
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-[260px_1fr]">
          <aside className="rounded-2xl border border-slate-100 bg-slate-50/80 p-5 shadow-soft">
            <div className="space-y-6">
              <div>
                <h3 className="text-sm font-semibold text-slate-900">분야</h3>
                <div className="mt-3 space-y-2">
                  {fields.map((field) => (
                    <label key={field} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedFields.has(field)}
                        onChange={() => toggleSet(field, setSelectedFields)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {field}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">운영 형태</h3>
                <div className="mt-3 space-y-2">
                  {modes.map((mode) => (
                    <label key={mode} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedModes.has(mode)}
                        onChange={() => toggleSet(mode, setSelectedModes)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {mode}
                    </label>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">지원 형태</h3>
                <div className="mt-3 space-y-2">
                  {fundings.map((fund) => (
                    <label key={fund} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedFunding.has(fund)}
                        onChange={() => toggleSet(fund, setSelectedFunding)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {fund === 'Government' ? '국비/지원' : '사비'}
                    </label>
                  ))}
                  <p className="text-xs text-slate-500">학비 지원 여부에 따라 구분됩니다.</p>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-slate-900">난이도</h3>
                <div className="mt-3 space-y-2">
                  {levels.map((level) => (
                    <label key={level} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedLevels.has(level)}
                        onChange={() => toggleSet(level, setSelectedLevels)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {level === 'Beginner' ? '입문' : level === 'Intermediate' ? '중급' : '고급'}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">결과 {filteredBootcamps.length}개</p>
              <div className="text-xs text-slate-500">정렬과 서버 연동은 추후 추가됩니다.</div>
            </div>

            <div className="space-y-4">
              {filteredBootcamps.map((boot) => (
                <div
                  key={boot.id}
                  className="flex flex-col gap-3 rounded-2xl border border-slate-100 bg-white p-5 shadow-soft md:flex-row md:items-center md:justify-between"
                >
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-primary-700">{boot.provider}</p>
                    <h3 className="text-lg font-bold text-slate-900">{boot.name}</h3>
                    <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-slate-600">
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.field}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.mode}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.price}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.funding}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.duration}</span>
                      <span className="rounded-full bg-slate-100 px-3 py-1">{boot.level}</span>
                    </div>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {boot.curriculum.map((item) => (
                        <span
                          key={item}
                          className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700"
                        >
                          {item}
                        </span>
                      ))}
                    </div>
                  </div>
                  <button className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto">
                    상세보기
                  </button>
                  <button
                    onClick={() => addToCompare(boot)}
                    className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto"
                  >
                    {compareList.find((b) => b.id === boot.id) ? '추가됨' : '비교 담기'}
                  </button>
                </div>
              ))}
              {!filteredBootcamps.length && (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                  조건에 맞는 부트캠프가 없습니다. 필터를 조정해 다시 확인해주세요.
                </div>
              )}
            </div>
          </section>
        </div>
      </div>

      {compareList.length > 0 && (
        <aside className="fixed right-6 top-24 z-50 w-80 max-h-[70vh] overflow-auto rounded-2xl border border-slate-100 bg-white p-4 shadow-lg">
          <div className="mb-3 flex items-center justify-between">
            <h4 className="text-sm font-semibold text-slate-900">비교 ({compareList.length}/3)</h4>
            <div className="flex items-center gap-2">
              <button onClick={clearCompare} className="text-xs font-semibold text-red-600 hover:underline">
                전체 삭제
              </button>
              <button
                onClick={() => {
                  const ids = compareList.map((b) => b.id).join(',')
                  navigate(`/compare?mode=bootcamps&ids=${encodeURIComponent(ids)}`)
                }}
                className="text-xs font-semibold text-white bg-primary-600 px-3 py-1 rounded-md hover:bg-primary-700"
              >
                비교하기
              </button>
            </div>
          </div>

          <div className="space-y-3">
            {compareList.map((item) => (
              <div key={item.id} className="flex items-start justify-between gap-2 rounded-lg border p-2">
                <div>
                  <p className="text-xs font-semibold text-primary-700">{item.provider}</p>
                  <p className="text-sm font-bold text-slate-900">{item.name}</p>
                  <p className="text-xs text-slate-600">{item.price}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <button
                    onClick={() => removeFromCompare(item.id)}
                    className="text-xs font-semibold text-primary-700 hover:underline"
                  >
                    삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        </aside>
      )}
    </div>
  )
}

export default BootcampsPage
