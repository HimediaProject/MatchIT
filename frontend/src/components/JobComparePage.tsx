import { useEffect, useState } from 'react';
type NavigateFunction = (page: any, params?: any) => void;

interface JobComparePageProps {
  onNavigate: NavigateFunction;
  selectedJobs: number[];
}

export default function JobComparePage({ onNavigate, selectedJobs }: JobComparePageProps) {
  const [jobs, setJobs] = useState<any[]>([]);
  useEffect(() => {
    if (!selectedJobs || selectedJobs.length === 0) {
      setJobs([]);
      return;
    }
    fetch('http://localhost:8000/api/jobs/compare', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(selectedJobs),
    })
      .then((res) => res.json())
      .then((data) => setJobs(data))
      .catch((e) => console.error('failed to fetch compare jobs', e));
  }, [selectedJobs]);

  // Keep an early empty array if no jobs

  return (
    <div className="max-w-[1400px] mx-auto px-6 py-8">
      {/* Back Button */}
      <button
        onClick={() => onNavigate('jobList')}
        className="mb-6 px-4 py-2 border border-gray-900 text-sm"
      >
        ← 목록으로
      </button>

      <h1 className="mb-8">채용공고 비교</h1>

      {/* Summary Headers - Horizontal Scroll Cards */}
      <div className="flex gap-4 mb-8 overflow-x-auto pb-4 items-stretch">
        {jobs.map((job) => (
          <div
            key={job.PostID ?? job.id}
            className="min-w-[320px] border border-gray-400 bg-white p-5 flex-shrink-0 h-full flex flex-col justify-between"
          >
            <div className="flex items-start gap-3 mb-3">
              <div className="w-14 h-14 border border-gray-500 flex items-center justify-center bg-gray-50">
                <span className="text-lg text-gray-400">×</span>
              </div>
                <div className="flex-1">
                <div className="text-xs text-gray-600 mb-1">[{job.CompanyName ?? job.company}]</div>
                <div className="text-sm mb-2">{job.Title ?? job.title}</div>
                <div className="inline-block px-2 py-1 border border-gray-900 text-xs">
                  매칭 {job.matching ?? 0}%
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Sections */}
      <div className="space-y-6">
        {/* Basic Info Comparison */}
          <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">기본 정보 비교</div>
          <div className="flex gap-4 overflow-x-auto items-stretch">
            {jobs.map((job) => (
              <div key={job.PostID ?? job.id} className="min-w-[320px] flex-shrink-0 space-y-2 h-full flex flex-col justify-between">
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">연봉</div>
                  <div className="text-sm">{job.Salary ?? job.salary ?? '-'}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">경력</div>
                  <div className="text-sm">{job.ExperienceRequirement ?? job.exp ?? '-'}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">근무지</div>
                  <div className="text-sm">{job.Location ?? job.location ?? '-'}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">고용형태</div>
                  <div className="text-sm">{job.EmploymentType ?? job.type ?? '-'}</div>
                </div>
                <div className="border border-gray-400 p-3 bg-gray-50">
                  <div className="text-xs text-gray-600 mb-1">마감일</div>
                  <div className="text-sm">{job.CloseDate ?? job.deadline ?? '-'}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skills Comparison */}
          <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">기술 스택 비교</div>
          <div className="flex gap-4 overflow-x-auto items-stretch">
            {jobs.map((job) => (
              <div key={job.PostID ?? job.id} className="min-w-[320px] flex-shrink-0 h-full">
                <div className="mb-4">
                  <div className="text-xs text-gray-600 mb-2">필수 기술</div>
                  <div className="flex flex-wrap gap-2">
                    {(job.requiredSkills ?? job.Skills ?? []).map((skill) => (
                      <span key={skill} className="px-2 py-1 border-2 border-gray-900 text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-600 mt-2">총 {(job.requiredSkills ?? job.Skills ?? []).length}개</div>
                </div>
                <div>
                  <div className="text-xs text-gray-600 mb-2">우대 기술</div>
                  <div className="flex flex-wrap gap-2">
                    {(job.preferredSkills ?? []).map((skill) => (
                      <span key={skill} className="px-2 py-1 border border-gray-500 text-xs bg-gray-50">
                        {skill}
                      </span>
                    ))}
                  </div>
                  <div className="text-xs text-gray-600 mt-2">총 {(job.preferredSkills ?? []).length}개</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Benefits Comparison */}
          <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">복지 및 혜택 비교</div>
          <div className="flex gap-4 overflow-x-auto items-stretch">
            {jobs.map((job) => (
              <div key={job.PostID ?? job.id} className="min-w-[320px] flex-shrink-0 h-full">
                <div className="space-y-2">
                  {(job.benefits ?? job.Benefits ?? []).map((benefit: string, idx: number) => (
                    <div key={idx} className="flex items-center gap-2 text-sm">
                      <span className="w-4 h-4 border border-gray-900 flex items-center justify-center text-xs">
                        ✓
                      </span>
                      <span>{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Company Info */}
          <div className="border border-gray-400 bg-white p-6">
          <div className="text-sm mb-4 pb-3 border-b border-gray-300">회사 정보</div>
          <div className="flex gap-4 overflow-x-auto items-stretch">
            {jobs.map((job) => (
              <div key={job.PostID ?? job.id} className="min-w-[320px] flex-shrink-0 h-full">
                <div className="border border-gray-400 p-4 bg-gray-50">
                  <div className="text-sm mb-2">{job.CompanyName ?? job.company}</div>
                  <div className="text-xs text-gray-600 space-y-1">
                    <div>업종: IT 서비스</div>
                    <div>설립: 2015년</div>
                    <div>직원수: 150명</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mt-8">
        {jobs.map((job) => (
          <div key={job.id} className="flex-1">
            <button className="w-full py-3 border-2 border-gray-900 bg-gray-900 text-white text-sm">
              {job.company} 지원하기
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
