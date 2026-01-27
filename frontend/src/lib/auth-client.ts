/**
 * Better Auth client configuration.
 *
 * This module provides authentication utilities for the frontend,
 * including session state management and authentication methods.
 */

// Types for auth state
export interface User {
  id: string;
  email: string;
}

export interface Session {
  token: string;
  expires_at: string;
}

export interface AuthState {
  user: User | null;
  session: Session | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}


// Mock auth state for MVP (to be replaced with Better Auth client)
let authState: AuthState = {
  user: null,
  session: null,
  isLoading: false,
  isAuthenticated: false,
};


/**
 * Get current authentication state.
 */
export function getAuthState(): AuthState {
  return authState;
}


/**
 * Save authentication state to localStorage (after sign in).
 */
export function saveAuthState(user: User, session: Session): void {
  authState = {
    user,
    session,
    isLoading: false,
    isAuthenticated: true,
  };

  // Store session in localStorage for persistence
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem('auth_user', JSON.stringify(user));
      localStorage.setItem('auth_session', JSON.stringify(session));
      console.log('Saved auth state:', { user, session }); // Debug log
    } catch (error) {
      console.error('Error saving auth state to localStorage:', error);
    }
  }
}


/**
 * Clear authentication state (after sign out).
 */
export function clearAuthState(): void {
  authState = {
    user: null,
    session: null,
    isLoading: false,
    isAuthenticated: false,
  };

  // Clear localStorage
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_user');
    localStorage.removeItem('auth_session');
  }
}


/**
 * Initialize auth state from localStorage.
 * Returns the initial auth state synchronously for SSR/initial render.
 */
export function initAuthState(): AuthState {
  if (typeof window === 'undefined') {
    return {
      user: null,
      session: null,
      isLoading: false,
      isAuthenticated: false,
    };
  }

  try {
    const storedUser = localStorage.getItem('auth_user');
    const storedSession = localStorage.getItem('auth_session');

    if (storedUser && storedSession) {
      try {
        const user = JSON.parse(storedUser);
        const session = JSON.parse(storedSession);

        // Check if session has expired
        if (session.expires_at && new Date(session.expires_at) <= new Date()) {
          clearAuthState();
          return {
            user: null,
            session: null,
            isLoading: false,
            isAuthenticated: false,
          };
        }

        authState = {
          user,
          session,
          isLoading: false,
          isAuthenticated: true,
        };
        return authState;
      } catch {
        clearAuthState();
      }
    }
  } catch (error) {
    console.error('Error initializing auth state from localStorage:', error);
  }

  return {
    user: null,
    session: null,
    isLoading: false,
    isAuthenticated: false,
  };
}


/**
 * Get authorization header for API requests.
 */
export function getAuthHeaders(): Record<string, string> {
  const state = getAuthState();
  if (state.session) {
    return {
      Authorization: `Bearer ${state.session.token}`,
    };
  }
  return {};
}
