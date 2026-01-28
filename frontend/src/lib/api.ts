/**
 * API client for communicating with the backend.
 *
 * This module provides a typed fetch wrapper for API calls with
 * automatic credentials inclusion for session management.
 */

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';


/**
 * API response wrapper with error handling.
 */
export interface ApiResponse<T> {
  data: T | null;
  error: string | null;
}


/**
 * Get authorization headers from auth client.
 */
function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') return {};

  try {
    const sessionStr = localStorage.getItem('auth_session');
    if (!sessionStr) {
      console.warn('No auth session found in localStorage');
      return {};
    }

    const session = JSON.parse(sessionStr);
    if (!session?.token) {
      console.warn('No token found in auth session');
      return {};
    }

    // Validate that the token is not expired
    if (session?.expires_at && new Date(session.expires_at) <= new Date()) {
      console.warn('Auth session has expired');
      localStorage.removeItem('auth_session');
      localStorage.removeItem('auth_user');
      return {};
    }

    console.log('Successfully retrieved auth token'); // Debug log
    return {
      Authorization: `Bearer ${session.token}`,
    };
  } catch (error) {
    console.error('Error parsing auth session:', error);
    return {};
  }
}


/**
 * Fetch wrapper that handles API responses and errors.
 *
 * @param endpoint - API endpoint path (e.g., '/todos')
 * @param options - Fetch options
 * @returns Promise resolving to response data
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  // Validate API URL
  if (!API_URL || API_URL.trim() === '') {
    console.error('API_URL is not configured');
    return { data: null, error: 'API_URL is not configured. Please check your environment variables.' };
  }

  const url = `${API_URL}${endpoint}`;

  const authHeaders = getAuthHeaders();
  if (typeof window !== 'undefined') {
    console.log('Auth headers:', authHeaders); // Debug log
  }

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
    ...authHeaders,
  };

  if (typeof window !== 'undefined') {
    console.log('Final headers for request:', { // Debug log
      endpoint,
      authHeaders,
      defaultHeaders,
      optionsHeaders: options.headers
    });
  }

  const config: RequestInit = {
    ...options,
    credentials: 'include', // Include credentials for CORS requests
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  };

  // Add timeout to prevent hanging requests
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout

  try {
    console.log(`Making request to: ${url}`); // Debug log
    const response = await fetch(url, {
      ...config,
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

      try {
        // Read the response body once
        const errorText = await response.text();
        if (errorText) {
          try {
            const errorData = JSON.parse(errorText);
            errorMessage = errorData.detail || errorData.message || errorData.error || errorMessage;
          } catch {
            // If not JSON, use the raw text
            errorMessage = errorText || errorMessage;
          }
        }
      } catch (parseError) {
        // Response might not be readable, use default message
        console.error('Error parsing error response:', parseError);
      }

      console.error(`API Error: ${errorMessage}`); // Debug log
      console.error(`Failed request details:`, { endpoint, method: options.method || 'GET', url }); // Additional debug info
      return { data: null, error: errorMessage };
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      return { data: null as T, error: null };
    }

    const data = await response.json();
    return { data, error: null };
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof Error && error.name === 'AbortError') {
      console.error('Request timed out'); // Debug log
      return { data: null, error: 'Request timed out. Please check your internet connection.' };
    }

    console.error('Network error:', error); // Debug log
    const errorMessage = error instanceof Error ? error.message : 'Network error';
    return { data: null, error: errorMessage };
  }
}


/**
 * HTTP method helpers for cleaner API calls.
 */
export const api = {
  get: <T>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    }),

  put: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    }),

  patch: <T>(endpoint: string, body?: unknown, options?: RequestInit) =>
    apiFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    }),

  delete: <T>(endpoint: string, options?: RequestInit) =>
    apiFetch<T>(endpoint, { ...options, method: 'DELETE' }),
};
