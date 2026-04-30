import { create } from 'zustand'
import { persist } from 'zustand/middleware'

// Matches exactly what the backend /auth/me returns (CurrentUserResponse)
export interface AuthUser {
  user_id: string        // backend field name
  email: string
  full_name: string | null
  is_superuser: boolean
  active_org_id: string  // backend field name
  memberships: string[]
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  activeOrgId: string | null
  orgs: Array<{ id: string; name: string; slug: string }>
  setAuth: (token: string, user: AuthUser) => void
  setActiveOrg: (orgId: string) => void
  setOrgs: (orgs: AuthState['orgs']) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      activeOrgId: null,
      orgs: [],
      // Store token AND derive activeOrgId from user.active_org_id in one call
      setAuth: (token, user) => set({ token, user, activeOrgId: user.active_org_id }),
      setActiveOrg: (orgId) => set({ activeOrgId: orgId }),
      setOrgs: (orgs) => set({ orgs }),
      logout: () => set({ token: null, user: null, activeOrgId: null, orgs: [] }),
    }),
    { name: 'nexiss-auth' }
  )
)
