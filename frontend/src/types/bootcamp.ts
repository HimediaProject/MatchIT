// 공통 Bootcamp 타입 선언

// Admin 페이지에서 사용하는 부트캠프 목록 항목 타입
export interface AdminBootcamp {
  bootcampid: number;
  bootcampname: string;
  institution?: string;
  description?: string;
}

// Admin 부트캠프 수정 요청 페이로드 타입
export type BootcampUpdatePayload = {
  bootcampname?: string;
  institution?: string;
  description?: string;
};
