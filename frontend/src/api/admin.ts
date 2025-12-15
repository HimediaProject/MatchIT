const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// 회원 관리 API
export const adminApi = {
  // ========== 회원 관리 ==========
  async getUsers() {
    const response = await fetch(`${API_BASE_URL}/admin/users`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to get users: ${response.status}`)
    return response.json()
  },

  async deleteUser(userId: number) {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to delete user: ${response.status}`)
    return response.json()
  },

  async updateUserRole(userId: number, role: 'user' | 'admin') {
    const response = await fetch(`${API_BASE_URL}/admin/users/${userId}/role`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ role }),
    })
    if (!response.ok) throw new Error(`Failed to update user role: ${response.status}`)
    return response.json()
  },

  // ========== 채용 공고 관리 ==========
  async getJobPosts() {
    const response = await fetch(`${API_BASE_URL}/admin/jobposts`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to get job posts: ${response.status}`)
    return response.json()
  },

  async deleteJobPost(jobId: number) {
    const response = await fetch(`${API_BASE_URL}/admin/jobposts/${jobId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to delete job post: ${response.status}`)
    return response.json()
  },

  async updateJobPost(jobId: number, data: { jobtitle?: string; jobdescription?: string }) {
    const response = await fetch(`${API_BASE_URL}/admin/jobposts/${jobId}`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error(`Failed to update job post: ${response.status}`)
    return response.json()
  },

  // ========== 부트캠프 관리 ==========
  async getBootcamps() {
    const response = await fetch(`${API_BASE_URL}/admin/bootcamps`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to get bootcamps: ${response.status}`)
    return response.json()
  },

  async deleteBootcamp(bootcampId: number) {
    const response = await fetch(`${API_BASE_URL}/admin/bootcamps/${bootcampId}`, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) throw new Error(`Failed to delete bootcamp: ${response.status}`)
    return response.json()
  },

  async updateBootcamp(bootcampId: number, data: { bootcampname?: string; description?: string }) {
    const response = await fetch(`${API_BASE_URL}/admin/bootcamps/${bootcampId}`, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error(`Failed to update bootcamp: ${response.status}`)
    return response.json()
  },
}
