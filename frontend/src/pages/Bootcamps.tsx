import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

type Bootcamp = {
  id: string
  name: string
  provider: string
  field: string
  mode: '온라인' | '오프라인' | '혼합'
  price: string
  funding: '국비' | '비국비'
  duration: string
  level: '입문' | '중급' | '고급'
  curriculum: string[]
}

const fields = ['백엔드', '데이터', 'AI', '풀스택', '클라우드']
const modes: Bootcamp['mode'][] = ['온라인', '오프라인', '혼합']
const fundings: Bootcamp['funding'][] = ['국비', '비국비']
const levels: Bootcamp['level'][] = ['입문', '중급', '고급']

const bootcampsSeed: Bootcamp[] = [
  {
    id: 'boot-1',
    name: '데이터 분석 입문 캠프',
    provider: '스쿨 A',
    field: '데이터',
    mode: '온라인',
    price: '국비',
    funding: '국비',
    duration: '12주',
    level: '입문',
    curriculum: ['Python', 'SQL', '시각화'],
  },
  {
    id: 'boot-2',
    name: 'AI 서비스 구축 부트캠프',
    provider: '랩 B',
    field: 'AI',
    mode: '오프라인',
    price: '250만원',
    funding: '비국비',
    duration: '10주',
    level: '중급',
    curriculum: ['LLM', 'MLOps', 'RAG'],
  },
  {
    id: 'boot-3',
    name: '풀스택 웹 데브',
    provider: '아카데미 C',
    field: '풀스택',
    mode: '혼합',
    price: '180만원',
    funding: '비국비',
    duration: '14주',
    level: '입문',
    curriculum: ['React', 'Node.js', 'Deploy'],
  },
  {
    id: 'boot-4',
    name: '클라우드 백엔드 실무반',
    provider: '스쿨 D',
    field: '백엔드',
    mode: '온라인',
    price: '220만원',
    funding: '비국비',
    duration: '16주',
    level: '고급',
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
        window.alert('이미 비교함에 담긴 부트캠프입니다.')
        return prev
      }
      if (prev.length >= 3) {
        window.alert('비교함은 최대 3개까지 담을 수 있습니다.')
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
          <p className="text-sm font-semibold text-primary-700">부트캠프 리스트</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">내게 맞는 부트캠프 찾아보기</h1>
          <p className="text-sm text-slate-600">
            분야, 수강 형태, 가격대를 선택해 원하는 과정을 빠르게 탐색하세요.
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
                <h3 className="text-sm font-semibold text-slate-900">수강 형태</h3>
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
                <h3 className="text-sm font-semibold text-slate-900">가격/지원</h3>
                <div className="mt-3 space-y-2">
                  {fundings.map((fund) => (
                    <label key={fund} className="flex items-center gap-2 text-sm text-slate-700">
                      <input
                        type="checkbox"
                        checked={selectedFunding.has(fund)}
                        onChange={() => toggleSet(fund, setSelectedFunding)}
                        className="h-4 w-4 rounded border-slate-300 text-primary-600 focus:ring-primary-500"
                      />
                      {fund}
                    </label>
                  ))}
                  <p className="text-xs text-slate-500">가격대/국비는 추후 상세 필터로 확장</p>
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
                      {level}
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </aside>

          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">총 {filteredBootcamps.length}건</p>
              <div className="text-xs text-slate-500">정렬 옵션은 추후 API 연동 시 적용</div>
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
                    상세 보기
                  </button>
                  <button
                    onClick={() => addToCompare(boot)}
                    className="w-full rounded-x2 border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto"
                  >
                    {compareList.find((b) => b.id === boot.id) ? '담겼음' : '비교함 담기'}
                  </button>
                </div>
              ))}
              {!filteredBootcamps.length && (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                  조건에 맞는 부트캠프가 없습니다. 필터를 조정하거나 초기화해주세요.
                </div>
              )}
            </div>
          </section>
        </div>
      </div>
              {compareList.length > 0 && (
                <aside className="fixed right-6 top-24 w-80 max-h-[70vh] overflow-auto bg-white border border-slate-100 rounded-2xl p-4 shadow-lg z-50">
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="text-sm font-semibold text-slate-900">비교함 ({compareList.length}/3)</h4>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={clearCompare}
                          className="text-xs font-semibold text-red-600 hover:underline"
                        >
                          전체삭제
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
                            <div key={item.id} className="flex items-start justify-between gap-2 p-2 border rounded-lg">
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

                        <div className="mt-3 flex justify-end">
                          <button
                            onClick={() => {
                              const ids = compareList.map((b) => b.id).join(',')
                              navigate(`/compare?mode=bootcamps&ids=${encodeURIComponent(ids)}`)
                            }}
                            className="text-sm font-semibold text-white bg-primary-600 px-3 py-2 rounded-md hover:bg-primary-700"
                          >
                            비교하기
                          </button>
                        </div>
                      </aside>
                    )}

            </div>
  )
}

export default BootcampsPage
