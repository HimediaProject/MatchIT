export default function DeleteJobs({ job, onClose, onDelete }: any) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex justify-center items-center z-50">
      <div className="bg-white p-6 rounded-lg w-[350px] shadow-lg">
        <h2 className="text-xl font-semibold mb-4">정말 삭제할까요?</h2>

        <p className="text-gray-700 mb-6">
          <span className="font-medium text-red-600">{job.title}</span> 공고가 영구 삭제됩니다.
        </p>

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded-md"
          >
            취소
          </button>

          <button
            onClick={() => onDelete(job.id)}
            className="px-4 py-2 bg-red-600 text-white rounded-md"
          >
            삭제
          </button>
        </div>
      </div>
    </div>
  );
}
