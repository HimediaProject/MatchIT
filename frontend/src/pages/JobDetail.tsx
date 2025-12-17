import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchJobDetail } from '../api/jobposts'
import { usersApi } from "../api/users";

const JobDetail = () => {
  const { jobId } = useParams()
  const navigate = useNavigate()

  const [isScrapped, setIsScrapped] = useState(false)
  const [scrapLoading, setScrapLoading] = useState(false)
  const [showCopied, setShowCopied] = useState(false)
  const [showCopyFail, setShowCopyFail] = useState(false)
  const [showScrapError, setShowScrapError] = useState(false)

  const id = Number(jobId)
  const isValidId = Number.isFinite(id) && id > 0

  const { data: job, isLoading, isError, error } = useQuery({
    queryKey: ['jobDetail', id],
    queryFn: () => fetchJobDetail(id),
    enabled: isValidId,
  })

  useEffect(() => {
    if (!isValidId) return
    let mounted = true
    const load = async () => {
      try {
        const scraps = await usersApi.getMyScraps()
        const found = Array.isArray(scraps)
          ? scraps.some((s: any) => s?.post_type === 'Job' && Number(s?.job_post_id) === id)
          : false
        if (mounted) setIsScrapped(found)
      } catch {
        // ignore
      }
    }
    load()
    return () => { mounted = false }
  }, [id, isValidId])

  const toggleScrap = async () => {
    if (!isValidId) return
    if (scrapLoading) return
    setScrapLoading(true)
    try {
      if (isScrapped) {
        await usersApi.removeMyScrap('Job', id)
        setIsScrapped(false)
      } else {
        await usersApi.addMyScrap('Job', id)
        setIsScrapped(true)
      }
    } catch (e) {
      const msg = String((e as any)?.message ?? e)
      if (msg.includes('401') || msg.includes('403')) {
        if (window.confirm('로그인이 필요합니다. 로그인 페이지로 이동할까요?')) {
          navigate('/login')
        }
      } else {
        setShowScrapError(true)
        setTimeout(() => setShowScrapError(false), 3000)
      }
    } finally {
      setScrapLoading(false)
    }
  }

  const handleShareClick = async () => {
    const title = job?.Title ?? '채용공고'
    const text = job?.Title ?? ''
    const url = window.location.href

    const getMetaImage = () => {
      const og = document.querySelector('meta[property="og:image"]') as HTMLMetaElement | null
      if (og && og.content) return og.content
      const tw = document.querySelector('meta[name="twitter:image"]') as HTMLMetaElement | null
      if (tw && tw.content) return tw.content
      return null
    }

    const imageUrl = getMetaImage()

    if (imageUrl && navigator.canShare) {
      try {
        const res = await fetch(imageUrl, { mode: 'cors' })
        const blob = await res.blob()
        const ext = blob.type.split('/')[1] || 'jpg'
        const file = new File([blob], `share-image.${ext}`, { type: blob.type })
        if (navigator.canShare({ files: [file] })) {
          await navigator.share({ files: [file], title, text })
          return
        }
      } catch {
        // image share failed, fallback
      }
    }

    if (navigator.share) {
      try {
        await navigator.share({ title, text, url })
        return
      } catch {
        // cancel or fail
      }
    }

    try {
      await navigator.clipboard.writeText(url)
      setShowCopied(true)
      setTimeout(() => setShowCopied(false), 3000)
    } catch {
      setShowCopyFail(true)
      setTimeout(() => setShowCopyFail(false), 3000)
    }
  }

  if (!isValidId) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-red-600">잘못된 공고 ID입니다.</p>
      </div>
    )
  }

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
        <p className="text-red-600">공고 로딩 실패: {(error as any)?.message ?? '알 수 없는 에러'}</p>
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

  return (
    <>
      <div className="bg-white">
        <div className="mx-auto max-w-4xl px-4 py-12 md:px-6">
          <div className="mb-6">
            <Link to="/jobs" className="inline-flex items-center gap-2 text-sm text-slate-600 hover:text-slate-900 transition">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
              채용공고 목록으로
            </Link>
          </div>

          <div className="mb-8 space-y-4">
            <div className="flex items-center justify-between gap-3">
              <p className="text-sm font-semibold text-primary-700">{job.CompanyName}</p>
              <div className="flex items-center gap-3"><span className="text-sm text-slate-500">조회수 {job.ViewCount.toLocaleString()}</span></div>
            </div>
            <h1 className="mt-1 text-3xl font-bold text-slate-900">{job.Title}</h1>
          </div>

          <div className="mb-6 rounded-2xl border border-slate-100 bg-slate-50/80 p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">기본 정보</h2>
            <div className="grid gap-4 sm:grid-cols-2">
              {job.Location && (<div><p className="text-sm font-semibold text-slate-700 mb-1">근무지역</p><p className="text-sm text-slate-600">{job.Location}</p></div>)}
              <div><p className="text-sm font-semibold text-slate-700 mb-1">경력</p><p className="text-sm text-slate-600">{job.MinExperienceYears ? `${job.MinExperienceYears}년 이상` : '경력 무관'}</p></div>
              {job.EmploymentType && (<div><p className="text-sm font-semibold text-slate-700 mb-1">고용 형태</p><p className="text-sm text-slate-600">{job.EmploymentType}</p></div>)}
              {(job.CloseDate && (<div><p className="text-sm font-semibold text-slate-700 mb-1">마감일</p><p className="text-sm text-slate-600">{new Date(job.CloseDate).toLocaleDateString()}</p></div>)) || (<div><p className="text-sm font-semibold text-slate-700 mb-1">마감일</p><p className="text-sm text-slate-600">상시</p></div>)}
            </div>

            <div className="mt-6 flex items-center gap-3">
              <button type="button" onClick={toggleScrap} disabled={scrapLoading} className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl border transition ${isScrapped ? 'border-primary-200 bg-primary-50 text-primary-700 hover:bg-primary-100' : 'border-slate-200 bg-white text-slate-400 hover:bg-slate-50 hover:text-slate-600'}`} aria-label="스크랩">
                <svg className="h-6 w-6" fill={isScrapped ? 'currentColor' : 'none'} viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" /></svg>
              </button>

              <button type="button" onClick={handleShareClick} className="h-12 flex-1 rounded-xl bg-primary-50 text-base font-bold text-primary-700 transition hover:bg-primary-100">공유하기</button>

              <a href={job.Url} target="_blank" rel="noopener noreferrer" className="flex h-12 flex-1 items-center justify-center rounded-xl bg-primary-600 text-base font-bold text-white shadow-sm transition hover:bg-primary-700">지원하기</a>
            </div>
          </div>

          <div className="mb-6 rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
            <h2 className="mb-4 text-lg font-bold text-slate-900">기술 스택</h2>
            <div className="flex flex-wrap gap-2">{job.Skills.length > 0 ? job.Skills.map((skill) => (<span key={skill} className="rounded-full bg-primary-50 px-3 py-1 text-sm font-semibold text-primary-700">{skill}</span>)) : (<p className="text-sm text-slate-500">기술 스택 정보가 없습니다.</p>)}</div>
          </div>

          <div className="space-y-6">
            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
              <h2 className="mb-4 text-lg font-bold text-slate-900">주요 업무</h2>
              <div className="prose prose-sm max-w-none">{job.MainTasks ? (<div className="space-y-2 text-sm text-slate-600 leading-relaxed">{job.MainTasks.split(/[-•*\\u2022]/).filter(item => item.trim()).map((item, index) => (<div key={index} className="break-keep">{item.trim()}</div>))}</div>) : (<p className="text-sm text-slate-500">주요 업무 정보가 없습니다.</p>)}</div>
            </div>

            <div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft">
              <h2 className="mb-4 text-lg font-bold text-slate-900">자격 요건</h2>
              <div className="prose prose-sm max-w-none">{job.Qualifications ? (<div className="space-y-2 text-sm text-slate-600 leading-relaxed">{job.Qualifications.split(/[-•*\\u2022]/).filter(item => item.trim()).map((item, index) => (<div key={index} className="break-keep">{item.trim()}</div>))}</div>) : (<p className="text-sm text-slate-500">자격 요건 정보가 없습니다.</p>)}</div>
            </div>

            {job.Preferences && (<div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft"><h2 className="mb-4 text-lg font-bold text-slate-900">우대 사항</h2><div className="prose prose-sm max-w-none"><div className="space-y-2 text-sm text-slate-600 leading-relaxed">{job.Preferences.split(/[-•*\\u2022]/).filter(item => item.trim()).map((item, index) => (<div key={index} className="break-keep">{item.trim()}</div>))}</div></div></div>)}

            {job.Benefits && (<div className="rounded-2xl border border-slate-100 bg-white p-6 shadow-soft"><h2 className="mb-4 text-lg font-bold text-slate-900">복지 / 혜택</h2><div className="prose prose-sm max-w-none"><div className="space-y-2 text-sm text-slate-600 leading-relaxed">{job.Benefits.split(/[-•*\\u2022]/).filter(item => item.trim()).map((item, index) => (<div key={index} className="break-keep">{item.trim()}</div>))}</div></div></div>)}
          </div>
        </div>
      </div>

      {showCopied && (<div className="fixed bottom-6 right-6 z-50 rounded-lg bg-black/80 text-white px-4 py-2 text-sm">링크가 복사되었습니다.</div>)}
      {showCopyFail && (<div className="fixed bottom-6 right-6 z-50 rounded-lg bg-red-600 text-white px-4 py-2 text-sm">링크 복사에 실패했습니다. 수동으로 복사해주세요.</div>)}
      {showScrapError && (<div className="fixed bottom-6 right-6 z-50 mt-14 rounded-lg bg-red-600 text-white px-4 py-2 text-sm">스크랩 처리에 실패했습니다.</div>)}
    </>
  )
}

export default JobDetail
