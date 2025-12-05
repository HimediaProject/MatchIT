import { useEffect, useMemo, useState } from 'react'
import { bootcampApi, type BootcampItem } from '../services/bootcampApi'
import { useNavigate } from 'react-router-dom'

type Bootcamp = {
  id: string
  name: string
  provider: string
  field: string
  mode: '온라인' | '오프라인' | '혼합'
  price: string
  funding: '국비지원' | '본인부담'
  duration: string
  // level: '입문' | '중급' | '고급'
  curriculum: string[]
}

// 날짜 차이 계산 (주 단위)
const calculateDuration = (startDate: string | null, closeDate: string | null): string => {
  if (!startDate || !closeDate) return '-'

  const start = new Date(startDate)
  const close = new Date(closeDate)

  if (isNaN(start.getTime()) || isNaN(close.getTime())) return '-'

  const diffTime = Math.abs(close.getTime() - start.getTime())
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  const diffWeeks = Math.ceil(diffDays / 7)

  return `${diffWeeks}주`
}

/**
 * 백엔드 데이터를 프론트엔드 형식으로 변환
 *
 * @param item - 백엔드 API에서 받은 부트캠프 데이터
 * @returns 프론트엔드에서 사용할 Bootcamp 타입 객체
 *
 * 주의: DB 제약조건과 일치하도록 매핑
 * - OnlineOffline: '온라인', '오프라인', '혼합형' (DB에 '혼합형'으로 저장됨)
 * - CostSupportType: '국비지원', '본인부담'
 */
const mapBackendToFrontend = (item: BootcampItem): Bootcamp => {
  // OnlineOffline 변환: DB의 '혼합형'을 '혼합'으로 변환
  let mode: Bootcamp['mode'] = '혼합'
  if (item.OnlineOffline === '온라인') mode = '온라인'
  else if (item.OnlineOffline === '오프라인') mode = '오프라인'
  else if (item.OnlineOffline === '혼합형') mode = '혼합'

  return {
    id: String(item.BootcampID),
    name: item.Title,
    provider: item.InstituteName,
    field: item.CategoryName,  // DB의 CategoryName을 그대로 사용
    mode: mode,
    price: item.CostSupportType === '국비지원' ? '국비지원' : '본인부담',
    funding: item.CostSupportType === '국비지원' ? '국비지원' : '본인부담',
    duration: calculateDuration(item.StartDate, item.CloseDate),
    // level: '입문',
    curriculum: item.EducationContent?.split(',').map(s => s.trim()) || [],
  }
}

/**
 * 필터 옵션 (하드코딩)
 *
 * 주의: 이 값들은 실제 DB 데이터와 일치해야 필터가 작동합니다.
 * 만약 모든 항목이 같은 값으로 표시된다면, 아래 두 가지를 확인하세요:
 * 1. DB에 저장된 실제 CategoryName 값
 * 2. mapBackendToFrontend 함수의 매핑 로직
 *
 * 대안: 동적 필터 생성 (useMemo로 bootcamps에서 실제 값 추출)
 */
const fields = [
  'Backend Developer', 'Frontend Developer', 'Full Stack Developer',
  'AI/ML Engineer', 'Database Engineer', 'Data Engineer'
]
const modes: Bootcamp['mode'][] = ['온라인', '오프라인', '혼합']
const fundings: Bootcamp['funding'][] = ['국비지원', '본인부담']
// const levels: Bootcamp['level'][] = ['입문', '중급', '고급']

const BootcampsPage = () => {
  const [bootcamps, setBootcamps] = useState<Bootcamp[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set())
  const [selectedModes, setSelectedModes] = useState<Set<Bootcamp['mode']>>(new Set())
  const [selectedFunding, setSelectedFunding] = useState<Set<Bootcamp['funding']>>(new Set())
  // const [selectedLevels, setSelectedLevels] = useState<Set<Bootcamp['level']>>(new Set())

  /**
   * 페이지네이션 상태
   *
   * currentPage: 현재 보고 있는 페이지 번호 (1부터 시작)
   * itemsPerPage: 한 페이지에 표시할 부트캠프 개수
   *
   * 페이지당 항목 수를 변경하려면 itemsPerPage 값을 수정하세요.
   * 예: const itemsPerPage = 20
   */
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10 // 페이지당 표시할 아이템 수

  /**
   * 백엔드에서 데이터 가져오기
   *
   * 컴포넌트가 마운트될 때 한 번만 실행됩니다.
   * 현재는 size: 100으로 설정하여 최대 100개의 부트캠프를 가져옵니다.
   *
   * 서버 사이드 페이지네이션으로 변경하려면:
   * - useEffect 의존성에 currentPage 추가
   * - API 호출에 page: currentPage 전달
   */
  useEffect(() => {
    const fetchBootcamps = async () => {
      try {
        setLoading(true)
        const response = await bootcampApi.getBootcamps({ page: 1, size: 100 })
        const mapped = response.items.map(mapBackendToFrontend)
        setBootcamps(mapped)
        setError(null)

        // 🔍 디버깅: 실제 데이터 확인
        console.log('📊 첫 3개 부트캠프 데이터:', mapped.slice(0, 3))
        console.log('📊 실제 field 값들:', [...new Set(mapped.map(b => b.field))])
        console.log('📊 실제 mode 값들:', [...new Set(mapped.map(b => b.mode))])
        console.log('📊 실제 funding 값들:', [...new Set(mapped.map(b => b.funding))])
      } catch (err) {
        setError('부트캠프 데이터를 불러오는데 실패했습니다.')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchBootcamps()
  }, [])

  /**
   * 🔧 동적 필터 옵션 생성
   *
   * 실제 데이터에서 중복 제거하여 필터 옵션을 생성합니다.
   * 하드코딩된 필터 대신 이 값들을 사용하면 DB 데이터와 항상 일치합니다.
   *
   * 사용법:
   * - 아래 주석을 해제하고 하드코딩된 fields, modes, fundings를 주석 처리
   * - 필터 렌더링 부분에서 해당 변수를 사용
   */
  const dynamicFields = useMemo(() => {
    return Array.from(new Set(bootcamps.map(b => b.field))).sort()
  }, [bootcamps])

  const dynamicModes = useMemo(() => {
    return Array.from(new Set(bootcamps.map(b => b.mode)))
  }, [bootcamps])

  const dynamicFundings = useMemo(() => {
    return Array.from(new Set(bootcamps.map(b => b.funding)))
  }, [bootcamps])
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

  /**
   * 필터링된 부트캠프 목록
   *
   * useMemo를 사용하여 필터 조건이 변경될 때만 재계산합니다.
   *
   * 필터 로직:
   * - 필터가 하나도 선택되지 않았으면 모든 항목 표시 (true)
   * - 필터가 선택되었으면 해당 값을 가진 항목만 표시
   * - 모든 필터는 AND 조건 (모두 만족해야 함)
   *
   * 예: "온라인" + "국비지원" 선택 → 온라인이면서 국비지원인 항목만 표시
   */
  const filteredBootcamps = useMemo(() => {
    return bootcamps.filter((boot) => {
      const fieldMatch = selectedFields.size ? selectedFields.has(boot.field) : true
      const modeMatch = selectedModes.size ? selectedModes.has(boot.mode) : true
      const fundingMatch = selectedFunding.size ? selectedFunding.has(boot.funding) : true
      // const levelMatch = selectedLevels.size ? selectedLevels.has(boot.level) : true
      return fieldMatch && modeMatch && fundingMatch
    })
  }, [bootcamps, selectedFields, selectedFunding, selectedModes])

  /**
   * 필터가 변경되면 첫 페이지로 이동
   *
   * 사용자가 필터를 변경하면 결과가 달라지므로 1페이지로 리셋합니다.
   * 예: 3페이지에 있다가 필터를 변경했는데 결과가 10개밖에 없으면 빈 페이지가 표시될 수 있음
   */
  useEffect(() => {
    setCurrentPage(1)
  }, [selectedFields, selectedModes, selectedFunding])

  /**
   * 페이지네이션 계산
   *
   * totalPages: 전체 페이지 수 (올림)
   *   - 예: 25개 항목 / 10 = 2.5 → Math.ceil(2.5) = 3페이지
   *
   * startIndex: 현재 페이지의 첫 번째 항목 인덱스 (0부터 시작)
   *   - 예: 2페이지 → (2-1) * 10 = 10번 인덱스부터
   *
   * endIndex: 현재 페이지의 마지막 항목 인덱스 + 1
   *   - 예: 10 + 10 = 20 (slice는 endIndex 미포함이므로 10~19번 인덱스)
   *
   * currentBootcamps: 현재 페이지에 표시할 부트캠프 배열
   *   - slice(10, 20) → 10번~19번 인덱스의 항목 (총 10개)
   */
  const totalPages = Math.ceil(filteredBootcamps.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentBootcamps = filteredBootcamps.slice(startIndex, endIndex)

  /**
   * 페이지 번호 배열 생성
   *
   * 페이지가 많을 때 모든 번호를 표시하지 않고 스마트하게 축약합니다.
   * -1은 "..." (생략 표시)를 의미합니다.
   *
   * 표시 패턴:
   * - 전체 5페이지 이하: [1] 2 3 4 5
   * - 현재 페이지 1~3: [1] 2 3 4 ... 20
   * - 현재 페이지 중간: 1 ... 9 [10] 11 ... 20
   * - 현재 페이지 끝: 1 ... 17 18 19 [20]
   *
   * maxVisible을 변경하여 표시할 버튼 개수를 조절할 수 있습니다.
   */
  const getPageNumbers = () => {
    const pages: number[] = []
    const maxVisible = 5

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i)
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) pages.push(i)
        pages.push(-1) // ... 표시용
        pages.push(totalPages)
      } else if (currentPage >= totalPages - 2) {
        pages.push(1)
        pages.push(-1)
        for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        pages.push(-1)
        pages.push(currentPage - 1)
        pages.push(currentPage)
        pages.push(currentPage + 1)
        pages.push(-1)
        pages.push(totalPages)
      }
    }

    return pages
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">로딩 중...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-600">{error}</p>
      </div>
    )
  }

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
                </div>
              </div>
            </div>
          </aside>

          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">
                총 {filteredBootcamps.length}건
                {totalPages > 0 && <span className="text-slate-500"> (페이지 {currentPage}/{totalPages})</span>}
              </p>
            </div>

            <div className="space-y-4">
              {currentBootcamps.map((boot) => (
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

            {/* 페이지네이션 */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
                >
                  이전
                </button>

                {getPageNumbers().map((pageNum, idx) => {
                  if (pageNum === -1) {
                    return (
                      <span key={`ellipsis-${idx}`} className="px-2 text-slate-400">
                        ...
                      </span>
                    )
                  }
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`min-w-[40px] rounded-lg border px-3 py-2 text-sm font-medium transition ${
                        currentPage === pageNum
                          ? 'border-primary-600 bg-primary-600 text-white'
                          : 'border-slate-200 text-slate-700 hover:bg-slate-50'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}

                <button
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
                >
                  다음
                </button>
              </div>
            )}
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

