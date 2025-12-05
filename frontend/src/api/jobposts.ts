import apiClient from './axios'

export interface JobPost {
  PostID: number
  PlatformID: number
  Title: string
  CompanyName: string
  JobCategoryID: number
  EmploymentType: string | null
  ExperienceRequirement: string | null
  MinExperienceYears: number | null
  EducationRequirement: string | null
  Location: string | null
  MainTasks: string | null
  Qualifications: string | null
  Preferences: string | null
  Benefits: string | null
  Process: string | null
  Salary: string | null
  PostedDate: string | null
  CloseDate: string | null
  ViewCount: number
  Url: string | null
  IsActive: boolean
  CreatedAt: string
  UpdatedAt: string | null
  Skills: string[]
}


export interface PaginatedJobPostResponse {
  total: number
  page: number
  size: number
  items: JobPost[]
}

export interface JobListParams {
  page?: number
  size?: number
  keyword?: string
  category_id?: number
  location?: string
  experience_requirement?: string
}

export async function fetchJobList(
  params: JobListParams = {},
): Promise<PaginatedJobPostResponse> {
  const {
    page = 1,
    size = 10,
    keyword,
    category_id,
    location,
    experience_requirement,
  } = params

  const response = await apiClient.get<PaginatedJobPostResponse>('/jobs/', {
    page,
    size,
    keyword,
    category_id,
    location,
    experience_requirement,
  })

  return response
}

export async function fetchJobDetail(
  jobId: number,
): Promise<JobPost> {
  const response = await apiClient.get<JobPost>(`/jobs/${jobId}/`)
  return response
}
