const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const authApi = {
  getSocialLoginUrl(provider: string) {
    return `${API_BASE_URL}/auth/${provider}/login?prompt=login`
  },

  async getCurrentUser() {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/kakao/me`, {
        method: 'GET',
        credentials: 'include',
      })

      if (!response.ok) {
        return { isLoggedIn: false, user: null }
      }

      return response.json()
    } catch (error) {
      console.error('getCurrentUser failed:', error)
      return { isLoggedIn: false, user: null }
    }
  },
}

export const searchApi = {
  async search(keyword: string) {
    const url = `${API_BASE_URL}/search?keyword=${encodeURIComponent(keyword)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Search request failed: ${res.status}`)
    return res.json()
  },

  async searchWithFilters(params: {
    keyword?: string
    skills?: string[]
    source?: '전체' | '채용' | '부트캠프'
    careerLevelId?: number
    experienceRangeId?: number
    limit?: number
    randomOrder?: boolean
  }) {
    const queryParams = new URLSearchParams()

    if (params.keyword) queryParams.append('keyword', params.keyword)
    if (params.skills && params.skills.length > 0) {
      params.skills.forEach((skill) => queryParams.append('skills', skill))
    }
    if (params.source && params.source !== '전체') {
      queryParams.append('source', params.source)
    }
    if (params.careerLevelId) queryParams.append('career_level_id', params.careerLevelId.toString())
    if (params.experienceRangeId) queryParams.append('experience_range_id', params.experienceRangeId.toString())
    if (params.limit) queryParams.append('limit', params.limit.toString())
    if (params.randomOrder) queryParams.append('random_order', 'true')

    const url = `${API_BASE_URL}/search?${queryParams.toString()}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Search request failed: ${res.status}`)
    return res.json()
  },
}

export const skillsApi = {
  async getAllSkills() {
    const url = `${API_BASE_URL}/skills/all`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Get all skills failed: ${res.status}`)
    return res.json()
  },

  async autocomplete(query: string) {
    const url = `${API_BASE_URL}/skills?query=${encodeURIComponent(query)}`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Skills autocomplete failed: ${res.status}`)
    return res.json()
  },
}

export const metaApi = {
  async getCareerLevels() {
    const url = `${API_BASE_URL}/careerlevels`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Get career levels failed: ${res.status}`)
    return res.json()
  },

  async getExperienceRanges() {
    const url = `${API_BASE_URL}/experienceranges`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Get experience ranges failed: ${res.status}`)
    return res.json()
  },

  async getDesiredJobs() {
    const url = `${API_BASE_URL}/desiredjobs`
    const res = await fetch(url)
    if (!res.ok) throw new Error(`Get desired jobs failed: ${res.status}`)
    return res.json()
  },
}

export const usersApi = {
  async getMyProfile() {
    const url = `${API_BASE_URL}/users/me`
    const res = await fetch(url, {
      method: 'GET',
      credentials: 'include',
    })
    if (!res.ok) throw new Error(`Get my profile failed: ${res.status}`)
    return res.json()
  },

  async updateMyProfile(data: any) {
    const url = `${API_BASE_URL}/users/me`
    const res = await fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!res.ok) throw new Error(`Update my profile failed: ${res.status}`)
    return res.json()
  },

  async getScraps(userId: number) {
    const url = `${API_BASE_URL}/users/${userId}/scraps`
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) throw new Error(`Get scraps failed: ${res.status}`)
    return res.json()
  },

  async getNotifications(userId: number) {
    const url = `${API_BASE_URL}/users/${userId}/notifications`
    const res = await fetch(url, { credentials: 'include' })
    if (!res.ok) throw new Error(`Get notifications failed: ${res.status}`)
    return res.json()
  },
}
