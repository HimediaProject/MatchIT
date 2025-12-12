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
  category_ids?: number[]
  skill_ids?: number[]
  location?: string
  experience_requirement?: string
  experience_min?: number | null
  experience_max?: number | null
  sort?: 'created' | 'deadline' | 'views'
}

export async function fetchJobList(
  params: JobListParams = {},
): Promise<PaginatedJobPostResponse> {
  const {
    page = 1,
    size = 10,
    keyword,
    category_id,
    category_ids,
    skill_ids,
    location,
    experience_requirement,
    experience_min,
    experience_max,
    sort,
  } = params

  const response = await apiClient.get<PaginatedJobPostResponse>('/jobs/', {
    page,
    size,
    keyword,
    category_id,
    category_ids,
    skill_ids,
    location,
    experience_requirement,
    experience_min,
    experience_max,
    sort,
  })

  return response
}

export async function fetchJobDetail(
  jobId: number,
): Promise<JobPost> {
  const response = await apiClient.get<JobPost>(`/jobs/${jobId}/`)
  return response
}

export interface JobCategory {
  CategoryID: number
  CategoryName: string
}

export async function fetchSkills(): Promise<string[]> {
  const res = await apiClient.get<{ skills?: string[] } | string[]>('/skills/')
  if (Array.isArray(res)) {
    return res as string[]
  }
  if (Array.isArray(res?.skills)) {
    return res.skills
  }
  return []
}

export async function fetchCategories(): Promise<JobCategory[]> {
  const res = await apiClient.get<{ categories?: JobCategory[] } | JobCategory[]>('/jobcategories/')
  if (Array.isArray(res)) return res
  return res?.categories ?? []
}
