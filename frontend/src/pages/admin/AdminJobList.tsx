import AdminLayout from "./AdminLayout";
import { useEffect, useState } from "react";
import { adminApi } from "../../api/admin";

interface JobPost {
  jobid: number;
  jobtitle: string;
  company?: string;
  jobdescription?: string;
}

export default function AdminJobList() {
  const [jobPosts, setJobPosts] = useState<JobPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [editingJob, setEditingJob] = useState<JobPost | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editedTitle, setEditedTitle] = useState("");
  const [editedDescription, setEditedDescription] = useState("");

  const loadJobPosts = async () => {
    try {
      setLoading(true);
      const data = await adminApi.getJobPosts();
      setJobPosts(data);
    } catch (error) {
      console.error("Failed to load job posts:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobPosts();
  }, []);

  const handleDeleteJobPost = async (jobId: number) => {
    if (!window.confirm("정말 이 공고를 삭제하시겠습니까?")) return;

    try {
      await adminApi.deleteJobPost(jobId);
      setJobPosts(jobPosts.filter((j) => j.jobid !== jobId));
      alert("공고가 삭제되었습니다.");
    } catch (error) {
      console.error("Failed to delete job post:", error);
      alert("공고 삭제에 실패했습니다.");
    }
  };

  const handleOpenEditModal = (job: JobPost) => {
    setEditingJob(job);
    setEditedTitle(job.jobtitle);
    setEditedDescription(job.jobdescription || "");
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    if (!editingJob) return;

    try {
      await adminApi.updateJobPost(editingJob.jobid, {
        jobtitle: editedTitle,
        jobdescription: editedDescription,
      });

      setJobPosts(
        jobPosts.map((j) =>
          j.jobid === editingJob.jobid
            ? {
                ...j,
                jobtitle: editedTitle,
                jobdescription: editedDescription,
              }
            : j
        )
      );
      setShowEditModal(false);
      alert("공고가 수정되었습니다.");
    } catch (error) {
      console.error("Failed to update job post:", error);
      alert("공고 수정에 실패했습니다.");
    }
  };

  return (
    <AdminLayout>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">채용 공고 관리</h1>
        <p className="text-gray-600 mt-2">전체 공고 조회, 수정, 삭제</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <p className="text-gray-600">로딩 중...</p>
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    제목
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    기업
                  </th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">
                    작업
                  </th>
                </tr>
              </thead>

              <tbody>
                {jobPosts.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-8 text-center text-gray-500">
                      채용 공고가 없습니다.
                    </td>
                  </tr>
                ) : (
                  jobPosts.map((job) => (
                    <tr
                      key={job.jobid}
                      className="border-b border-gray-200 hover:bg-gray-50"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {job.jobid}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {job.jobtitle}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {job.company || "-"}
                      </td>
                      <td className="px-6 py-4 text-sm space-x-2 flex">
                        <button
                          onClick={() => handleOpenEditModal(job)}
                          className="px-3 py-1 bg-blue-500 text-white rounded text-xs font-medium hover:bg-blue-600"
                        >
                          수정
                        </button>
                        <button
                          onClick={() => handleDeleteJobPost(job.jobid)}
                          className="px-3 py-1 bg-red-500 text-white rounded text-xs font-medium hover:bg-red-600"
                        >
                          삭제
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* 수정 모달 */}
      {showEditModal && editingJob && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-xl">
            <h2 className="text-xl font-bold mb-4">공고 수정</h2>

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목
              </label>
              <input
                type="text"
                value={editedTitle}
                onChange={(e) => setEditedTitle(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                설명
              </label>
              <textarea
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowEditModal(false)}
                className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
              >
                취소
              </button>
              <button
                onClick={handleSaveEdit}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-medium"
              >
                저장
              </button>
            </div>
          </div>
        </div>
      )}
    </AdminLayout>
  );
}
