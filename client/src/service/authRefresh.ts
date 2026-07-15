/**
 * Shared silent-refresh logic for the reporting login flow.
 *
 * Both ApiService.js and httpService.ts hit this so a single in-flight
 * refresh call is ever made, even if several requests 401 at once
 * (the backend rotates the refresh token on every use, so a second
 * concurrent call with the same token would otherwise fail).
 */
import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

let refreshPromise: Promise<string | null> | null = null;

export function getRefreshToken(): string | null {
    const t = localStorage.getItem('_ihris_refresh_token');
    return t && t !== 'undefined' && t !== 'null' ? t : null;
}

export function storeTokens(token: string, refreshToken?: string | null): void {
    localStorage.setItem('_ihris_token', token);
    if (refreshToken) {
        localStorage.setItem('_ihris_refresh_token', refreshToken);
    }
}

export function clearAuthTokens(): void {
    localStorage.removeItem('_ihris_token');
    localStorage.removeItem('_ihris_refresh_token');
}

/**
 * Exchanges the stored refresh token for a new access token (and a
 * rotated refresh token). Resolves to null if there is no refresh
 * token available or the exchange fails, in which case the caller
 * should fall back to forcing a fresh login.
 */
export function refreshAccessToken(): Promise<string | null> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) {
        return Promise.resolve(null);
    }

    if (!refreshPromise) {
        const baseURL = import.meta.env.VITE_SERVER_URL;
        refreshPromise = axios
            .post(`${baseURL}users/reporting/refresh`, { refresh_token: refreshToken })
            .then((res) => {
                const { token, refresh_token: newRefreshToken } = res.data;
                storeTokens(token, newRefreshToken);
                return token as string;
            })
            .catch(() => {
                clearAuthTokens();
                return null;
            })
            .finally(() => {
                refreshPromise = null;
            });
    }

    return refreshPromise;
}

/**
 * Runs an arbitrary axios request config; on a 401, tries a single
 * silent token refresh and retries once with the new token before
 * giving up. Shared by every call site that talks to the API directly
 * with axios rather than through one of the ApiService wrappers.
 */
export async function withAuthRetry(config: AxiosRequestConfig): Promise<AxiosResponse> {
    try {
        return await axios(config);
    } catch (error: any) {
        if (error?.response?.status === 401 && !(config as any).__isRetry) {
            const newToken = await refreshAccessToken();
            if (newToken) {
                const retryConfig: AxiosRequestConfig = {
                    ...config,
                    headers: {
                        ...config.headers,
                        'x-access-token': newToken,
                        Authorization: `Bearer ${newToken}`,
                    },
                };
                (retryConfig as any).__isRetry = true;
                return axios(retryConfig);
            }
        }
        throw error;
    }
}
