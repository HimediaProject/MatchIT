import { useState } from "react";

export default function EditJobs({ job, onClose, onSave }: any) {
  const [title, setTitle] = useState(job.title);
  const [company, setCompany] = useState(job.company);
  const [url, setUrl] = useState(job.url);

  const handleSave = () => {
    onSave({
      ...job,
      title,
      company,
      url,
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-[400px] shadow-lg">
        <h2 className="text-xl font-semibold mb-4">공고 수정</h2>

        <label className="block text-sm font-medium text-gray-700 mb-1">제목</label>
        <input
          className="w-full border p-2 rounded mb-3"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">기업명</label>
        <input
          className="w-full border p-2 rounded mb-3"
          value={company}
          onChange={(e) => setCompany(e.target.value)}
        />

        <label className="block text-sm font-medium text-gray-700 mb-1">URL</label>
        <input
          className="w-full border p-2 rounded mb-5"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
        />

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded-md"
          >
            취소
          </button>

          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md"
          >
            저장
          </button>
        </div>
      </div>
    </div>
  );
}
