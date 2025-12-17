import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { usersApi } from '../api/users'

type ScrapItem = { postType: 'Job' | 'Bootcamp'; targetId: number; label: string }

const ScrapsPage = () => {
  const [items, setItems] = useState<ScrapItem[]>([])
  const [deleting, setDeleting] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const pageSize = 10
  const location = useLocation()
  const navigate = useNavigate()

  const search = new URLSearchParams(location.search)
  const type = (search.get('type') || '').toString()

  useEffect(() => {
    let mounted = true
    const fetch = async () => {
      setLoading(true)
      try {
        const res = await usersApi.getMyScraps()
        const arr = Array.isArray(res) ? res : (res?.items || [])
        const mapped = arr
          .map((s: any) => {
            const postType = String(s?.post_type ?? s?.postType ?? '')
            if (postType === 'Job') {
              const targetId = Number(s?.job_post_id ?? s?.jobPostId)
              const label = String(s?.job_post?.title ?? s?.job_post?.Title ?? s?.label ?? '')
              if (!Number.isFinite(targetId) || !label) return null
              return { postType: 'Job' as const, targetId, label }
            }
            if (postType === 'Bootcamp') {
              const targetId = Number(s?.bootcamp_post_id ?? s?.bootcampPostId)
              const label = String(s?.bootcamp_post?.title ?? s?.bootcamp_post?.Title ?? s?.label ?? '')
              if (!Number.isFinite(targetId) || !label) return null
              return { postType: 'Bootcamp' as const, targetId, label }
            }
            return null
          })
          .filter(Boolean) as ScrapItem[]

        if (!mounted) return
        if (type === 'Job') setItems(mapped.filter((m) => m.postType === 'Job'))
        else if (type === 'Bootcamp') setItems(mapped.filter((m) => m.postType === 'Bootcamp'))
        else setItems(mapped)
      } catch (e) {
        console.error('Failed to fetch scraps', e)
        setItems([])
      } finally {
        if (mounted) setLoading(false)
      }
    }
    fetch()
    return () => {
      mounted = false
    }
  }, [type])

  // 페이지 범위 보정: items 변경 시 현재 페이지가 초과하면 마지막 페이지로 이동
  useEffect(() => {
    const totalPages = Math.max(1, Math.ceil(items.length / pageSize))
    if (page > totalPages) setPage(totalPages)
  }, [items, page, pageSize])

  const totalPages = Math.max(1, Math.ceil(items.length / pageSize))
  const pagedItems = items.slice((page - 1) * pageSize, page * pageSize)

  const handleDelete = async (postType: 'Job' | 'Bootcamp', targetId: number, index: number) => {
    if (!window.confirm('정말 삭제하시겠습니까?')) return
    const key = `${postType}:${targetId}`
    try {
      setDeleting((d) => ({ ...d, [key]: true }))
      await usersApi.removeMyScrap(postType, targetId)
      setItems((prev) => {
        const copy = [...prev]
        copy.splice(index, 1)
        return copy
      })
    } catch (e) {
      console.error('스크랩 삭제 실패', e)
      alert('스크랩 삭제에 실패했습니다.')
    } finally {
      setDeleting((d) => {
        const next = { ...d }
        delete next[key]
        return next
      })
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">{type === 'Job' ? '채용공고 스크랩' : type === 'Bootcamp' ? '부트캠프 스크랩' : '내 스크랩'}</h1>
        <div className="flex gap-2">
          <button onClick={() => navigate('/profile')} className="text-sm text-slate-600 hover:underline">내 프로필</button>
        </div>
      </div>

      {loading ? (
        <div className="text-sm text-slate-600">불러오는 중...</div>
      ) : items.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-200 bg-white p-4 text-sm text-slate-600">스클랩 항목이 없습니다.</div>
      ) : (
        <>
          <div className="mb-3 text-sm text-slate-600">총 {items.length}개</div>
          <ul className="space-y-2">
            {pagedItems.map((s, i) => {
            const key = `${s.postType}:${s.targetId}`
              return (
                <li key={`${s.postType}:${s.targetId}:${i}`} className="rounded-md border border-slate-100 bg-white p-3 text-sm text-slate-800">
                  <div className="flex items-center justify-between gap-3">
                    <button
                      type="button"
                      onClick={() => navigate(s.postType === 'Job' ? `/jobs/${s.targetId}` : `/bootcamps/${s.targetId}`)}
                      className="flex-1 text-left"
                    >
                      {s.label}
                    </button>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        // 실제 items 배열에서의 인덱스를 계산하여 삭제
                        const globalIndex = (page - 1) * pageSize + i
                        void handleDelete(s.postType, s.targetId, globalIndex)
                      }}
                      disabled={!!deleting[key]}
                      className="ml-3 text-sm text-red-600 hover:underline disabled:opacity-50"
                      aria-label="스크랩 삭제"
                    >
                      {deleting[key] ? '삭제중...' : '삭제'}
                    </button>
                  </div>
                </li>
              )
            })}
          </ul>

          {/* 페이지네이션 컨트롤 */}
          <div className="mt-4 flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 rounded-md border bg-white text-sm disabled:opacity-50"
            >
              이전
            </button>

            <div className="flex gap-1">
              {Array.from({ length: totalPages }).map((_, idx) => {
                const p = idx + 1
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`px-3 py-1 rounded-md text-sm ${p === page ? 'bg-primary-600 text-white' : 'bg-white border'}`}
                  >
                    {p}
                  </button>
                )
              })}
            </div>

            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 rounded-md border bg-white text-sm disabled:opacity-50 ml-2"
            >
              다음
            </button>
          </div>
        </>
      )}
    </div>
  )
}

export default ScrapsPage
