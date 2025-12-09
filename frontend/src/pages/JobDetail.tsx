import React from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { fetchJobDetail, type JobPost } from '../api/jobposts'

const JobDetail: React.FC = () => {
  const { jobId } = useParams()

  const navigate = useNavigate()

  if (!jobId) {
    return (
      <div className="flex justify-center py-10">
        <p className="text-red-600">잘못된 공고 ID입니다.</p>
      </div>
    )
  }

  const id = Number(jobId)

  const {
    data: job, 
    isLoading,
    isError, 
    error,  
  } = useQuery({
    queryKey: ['jobDetail', id],  
    queryFn: () => fetchJobDetail(id),  
    enabled: !!id,  
  })

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
        <p className="text-red-600">
          공고 로딩 실패: {(error as any)?.message ?? '알 수 없는 에러'}
        </p>
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
    <div className="mx-auto max-w-4xl px-4 py-8">

      {/* 뒤로가기 버튼 */}
      <button
        onClick={() => navigate(-1)}
        className="mb-6 text-sm text-primary-600 hover:underline"
      >
        ← 목록으로 돌아가기
      </button>

      {/* 회사명 */}
      <p className="text-sm font-semibold text-primary-700">
        {job.CompanyName}
      </p>

      {/* 공고 제목 */}
      <h1 className="mt-1 text-3xl font-bold text-slate-900">
        {job.Title}
      </h1>

      {/* 위치, 경력, 고용 형태 정보 */}
      <div className="mt-2 flex flex-wrap gap-3 text-sm text-slate-600">
        <span>{job.Location ?? '지역 정보 없음'}</span>
        <span>·</span>
        <span>{job.ExperienceRequirement ?? '경력 정보 없음'}</span>
        {job.EmploymentType && (
          <>
            <span>·</span>
            <span>{job.EmploymentType}</span>
          </>
        )}
      </div>

      {/* 스킬 태그 */}
      <div className="mt-4 flex flex-wrap gap-2">
        {job.Skills.length > 0 ? (
          job.Skills.map((skill) => (
            <span
              key={skill}
              className="rounded-full bg-primary-50 px-3 py-1 text-xs font-semibold text-primary-700"
            >
              {skill}
            </span>
          ))
        ) : (
          <span className="text-xs text-slate-400">스킬 정보 없음</span>
        )}
      </div>

      {/* 본문 정보 섹션들 */}
      <div className="mt-10 space-y-6">

        {/* 주요 업무 */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="mb-2 text-lg font-semibold text-slate-900">주요 업무</h2>
          <p className="whitespace-pre-line text-sm text-slate-700">
            {job.MainTasks ?? '주요 업무 정보 없음'}
          </p>
        </section>

        {/* 자격 요건 */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="mb-2 text-lg font-semibold text-slate-900">자격 요건</h2>
          <p className="whitespace-pre-line text-sm text-slate-700">
            {job.Qualifications ?? '자격 요건 정보 없음'}
          </p>
        </section>

        {/* 우대 사항 */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="mb-2 text-lg font-semibold text-slate-900">우대 사항</h2>
          <p className="whitespace-pre-line text-sm text-slate-700">
            {job.Preferences ?? '우대 사항 정보 없음'}
          </p>
        </section>

        {/* 복지 / 혜택 */}
        <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-soft">
          <h2 className="mb-2 text-lg font-semibold text-slate-900">복지 / 혜택</h2>
          <p className="whitespace-pre-line text-sm text-slate-700">
            {job.Benefits ?? '복지 / 혜택 정보 없음'}
          </p>
        </section>

      </div>

      {/* 게시일 / 마감일 / 원문 링크 */}
      <div className="mt-10 flex flex-wrap items-center justify-between text-xs text-slate-500">

        <div className="space-x-3">
          <span>
            게시일:{' '}
            {job.PostedDate
              ? new Date(job.PostedDate).toLocaleDateString()
              : '정보 없음'}
          </span>

          <span>
            마감일:{' '}
            {job.CloseDate
              ? new Date(job.CloseDate).toLocaleDateString()
              : '정보 없음'}
          </span>
        </div>

        {job.Url && (
          <a
            href={job.Url}
            target="_blank"
            rel="noreferrer"
            className="rounded-full border border-primary-500 px-3 py-1 text-xs font-semibold text-primary-600 hover:bg-primary-50"
          >
            원본 공고 보기
          </a>
        )}

      </div>
    </div>
  )
}


export default JobDetail
