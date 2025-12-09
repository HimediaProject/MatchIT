import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { bootcampApi, type BootcampItem } from '../services/bootcampApi'

type Bootcamp = {
  id: string
  name: string
  provider: string
  field: string
  mode: 'Online' | 'Offline' | 'Hybrid'
  price: string
  funding: 'Government' | 'Private'
  duration: string
  curriculum: string[]
}

const mapBackendToFrontend = (item: BootcampItem): Bootcamp => {
  const onlineOffline = (item.OnlineOffline || '').toLowerCase()
  let mode: Bootcamp['mode'] = 'Hybrid'
  if (onlineOffline.includes('online')) mode = 'Online'
  else if (onlineOffline.includes('offline')) mode = 'Offline'

  const funding: Bootcamp['funding'] = item.CostSupportType?.includes('국비') ? 'Government' : 'Private'

  const duration = item.StartDate && item.CloseDate
    ? `${item.StartDate} ~ ${item.CloseDate}`
    : item.StartDate || item.CloseDate || '-'

  return {
    id: String(item.BootcampID),
    name: item.Title,
    provider: item.InstituteName,
    field: item.CategoryName || '기타',
    mode,
    price: item.CostSupportType || '-',
    funding,
    duration,
    curriculum: item.EducationContent ? item.EducationContent.split(',').map((s) => s.trim()).filter(Boolean) : [],
  }
}

const BootcampsPage = () => {
  const [bootcamps, setBootcamps] = useState<Bootcamp[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set())
  const [selectedModes, setSelectedModes] = useState<Set<Bootcamp['mode']>>(new Set())
  const [selectedFunding, setSelectedFunding] = useState<Set<Bootcamp['funding']>>(new Set())
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 10

  const navigate = useNavigate()

  const getInitialCompare = () => {
    try {
      const raw = localStorage.getItem('compare_bootcamps')
      return raw ? (JSON.parse(raw) as Bootcamp[]) : []
    } catch {
      return []
    }
  }

  const [compareList, setCompareList] = useState<Bootcamp[]>(getInitialCompare)

  useEffect(() => {
    localStorage.setItem('compare_bootcamps', JSON.stringify(compareList))
  }, [compareList])

  useEffect(() => {
    const fetchBootcamps = async () => {
      try {
        setLoading(true)
        const response = await bootcampApi.getBootcamps({ page: 1, size: 100 })
        setBootcamps(response.items.map(mapBackendToFrontend))
        setError(null)
      } catch (err: any) {
        setError(err?.message || '부트캠프를 불러오지 못했습니다.')
      } finally {
        setLoading(false)
      }
    }

    fetchBootcamps()
  }, [])

  const toggleSet = <T,>(value: T, setter: React.Dispatch<React.SetStateAction<Set<T>>>) => {
    setter((prev) => {
      const next = new Set(prev)
      next.has(value) ? next.delete(value) : next.add(value)
      return next
    })
  }

  const fields = useMemo(() => Array.from(new Set(bootcamps.map((b) => b.field))).sort(), [bootcamps])
  const modes: Bootcamp['mode'][] = ['Online', 'Offline', 'Hybrid']
  const fundings: Bootcamp['funding'][] = ['Government', 'Private']

  const filteredBootcamps = useMemo(() => {
    return bootcamps.filter((boot) => {
      const fieldMatch = selectedFields.size ? selectedFields.has(boot.field) : true
      const modeMatch = selectedModes.size ? selectedModes.has(boot.mode) : true
      const fundingMatch = selectedFunding.size ? selectedFunding.has(boot.funding) : true
      return fieldMatch && modeMatch && fundingMatch
    })
  }, [bootcamps, selectedFields, selectedModes, selectedFunding])

  useEffect(() => {
    setCurrentPage(1)
  }, [selectedFields, selectedModes, selectedFunding])

  const totalPages = Math.ceil(filteredBootcamps.length / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentBootcamps = filteredBootcamps.slice(startIndex, endIndex)

  const addToCompare = (boot: Bootcamp) => {
    setCompareList((prev) => {
      if (prev.find((b) => b.id === boot.id)) {
        window.alert('이미 비교 목록에 있습니다.')
        return prev
      }
      if (prev.length >= 3) {
        window.alert('최대 3개까지 비교할 수 있습니다.')
        return prev
      }
      return [...prev, boot]
    })
  }

  const removeFromCompare = (id: string) => setCompareList((prev) => prev.filter((b) => b.id !== id))

  const clearCompare = () => setCompareList([])

  const getPageNumbers = () => {
    const pages: number[] = []
    const maxVisible = 5

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) pages.push(i)
    } else if (currentPage <= 3) {
      pages.push(1, 2, 3, 4, -1, totalPages)
    } else if (currentPage >= totalPages - 2) {
      pages.push(1, -1, totalPages - 3, totalPages - 2, totalPages - 1, totalPages)
    } else {
      pages.push(1, -1, currentPage - 1, currentPage, currentPage + 1, -1, totalPages)
    }

    return pages
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-slate-600">불러오는 중입니다...</p>
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
          <p className="text-sm font-semibold text-primary-700">부트캠프 추천</p>
          <h1 className="text-2xl font-bold text-slate-950 sm:text-3xl">내게 맞는 부트캠프 찾기</h1>
          <p className="text-sm text-slate-600">분야, 운영 형태, 지원 유형으로 원하는 부트캠프를 골라보세요.</p>
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
                <h3 className="text-sm font-semibold text-slate-900">지원 유형</h3>
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
                  <p className="text-xs text-slate-500">정부 지원 여부에 따라 분류합니다.</p>
                </div>
              </div>
            </div>
          </aside>

          <section className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="text-sm font-semibold text-slate-800">
                총 {filteredBootcamps.length}개
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
                  <div className="flex w-full flex-col gap-2 md:w-auto">
                    <button className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto">
                      자세히 보기
                    </button>
                    <button
                      onClick={() => addToCompare(boot)}
                      className="w-full rounded-xl border border-primary-200 px-4 py-2 text-sm font-semibold text-primary-700 transition hover:bg-primary-50 md:w-auto"
                    >
                      {compareList.find((b) => b.id === boot.id) ? '추가됨' : '비교 추가'}
                    </button>
                  </div>
                </div>
              ))}
              {!filteredBootcamps.length && (
                <div className="rounded-2xl border border-dashed border-slate-200 bg-slate-50 p-6 text-sm text-slate-600">
                  조건에 맞는 부트캠프가 없습니다. 필터를 조정해 주세요.
                </div>
              )}
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-center gap-2 pt-4">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-50 disabled:hover:bg-white"
                >
                  이전
                </button>

                {getPageNumbers().map((pageNum, idx) =>
                  pageNum === -1 ? (
                    <span key={`ellipsis-${idx}`} className="px-2 text-slate-400">
                      ...
                    </span>
                  ) : (
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
                  ),
                )}

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
