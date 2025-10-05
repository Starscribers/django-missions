(function (global, factory) {
    typeof exports === 'object' && typeof module !== 'undefined' ? factory(exports) :
    typeof define === 'function' && define.amd ? define(['exports'], factory) :
    (global = typeof globalThis !== 'undefined' ? globalThis : global || self, factory(global.Skellar = {}));
})(this, (function (exports) { 'use strict';

    class SkellarError extends Error {
        constructor(message, statusCode, responseData) {
            super(message);
            this.name = 'SkellarError';
            this.statusCode = statusCode;
            this.responseData = responseData;
            if (typeof Error.captureStackTrace === 'function') {
                Error.captureStackTrace(this, SkellarError);
            }
        }
    }
    class AuthenticationError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'AuthenticationError';
        }
    }
    class APIError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'APIError';
        }
    }
    class NotFoundError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'NotFoundError';
        }
    }
    class ValidationError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'ValidationError';
        }
    }
    class RateLimitError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'RateLimitError';
        }
    }
    class ConnectionError extends SkellarError {
        constructor(message, statusCode, responseData) {
            super(message, statusCode, responseData);
            this.name = 'ConnectionError';
        }
    }

    class SkellarClient {
        constructor(config = {}) {
            this.apiToken = config.apiToken || this.getApiTokenFromEnv();
            if (!this.apiToken) {
                throw new AuthenticationError('API token is required. Provide it in config or set SKELLAR_API_TOKEN environment variable.');
            }
            this.baseUrl = config.baseUrl || this.getBaseUrlFromEnv() || 'https://api.skellar.ai';
            this.timeout = config.timeout || 30000;
            this.maxRetries = config.maxRetries || 3;
        }
        getApiTokenFromEnv() {
            var _a;
            if (typeof window === 'undefined' && typeof globalThis !== 'undefined') {
                const processEnv = (_a = globalThis.process) === null || _a === void 0 ? void 0 : _a.env;
                if (processEnv) {
                    return processEnv.SKELLAR_API_TOKEN || '';
                }
            }
            return '';
        }
        getBaseUrlFromEnv() {
            var _a;
            if (typeof window === 'undefined' && typeof globalThis !== 'undefined') {
                const processEnv = (_a = globalThis.process) === null || _a === void 0 ? void 0 : _a.env;
                if (processEnv) {
                    return processEnv.SKELLAR_BASE_URL || '';
                }
            }
            return '';
        }
        async sleep(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
        async makeRequest(config) {
            const url = `${this.baseUrl}${config.url}`;
            const headers = {
                'Authorization': this.apiToken,
                'Content-Type': 'application/json',
                'User-Agent': 'skellar-js-sdk/0.1.0',
                ...config.headers,
            };
            let attempt = 0;
            while (attempt <= this.maxRetries) {
                try {
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), this.timeout);
                    const fetchConfig = {
                        method: config.method,
                        headers,
                        signal: controller.signal,
                        mode: 'cors',
                    };
                    if (config.data && config.method !== 'GET') {
                        fetchConfig.body = JSON.stringify(config.data);
                    }
                    let requestUrl = url;
                    if (config.params) {
                        const searchParams = new URLSearchParams();
                        Object.entries(config.params).forEach(([key, value]) => {
                            if (value !== undefined && value !== null) {
                                searchParams.append(key, String(value));
                            }
                        });
                        const queryString = searchParams.toString();
                        if (queryString) {
                            requestUrl += `?${queryString}`;
                        }
                    }
                    const response = await fetch(requestUrl, fetchConfig);
                    clearTimeout(timeoutId);
                    if (response.status === 429) {
                        const retryAfter = parseInt(response.headers.get('Retry-After') || '60', 10);
                        throw new RateLimitError(`Rate limit exceeded. Retry after ${retryAfter} seconds.`, 429, await this.safeParseJSON(response));
                    }
                    if (response.status === 401) {
                        throw new AuthenticationError('Authentication failed. Check your API token.', 401, await this.safeParseJSON(response));
                    }
                    if (response.status === 404) {
                        throw new NotFoundError('Resource not found.', 404, await this.safeParseJSON(response));
                    }
                    if (response.status === 400) {
                        const errorData = await this.safeParseJSON(response);
                        throw new ValidationError(`Validation error: ${(errorData === null || errorData === void 0 ? void 0 : errorData.detail) || 'Bad request'}`, 400, errorData);
                    }
                    if (!response.ok) {
                        const errorData = await this.safeParseJSON(response);
                        throw new APIError(`API request failed: ${response.status} ${response.statusText}`, response.status, errorData);
                    }
                    const data = await this.safeParseJSON(response);
                    const responseHeaders = {};
                    response.headers.forEach((value, key) => {
                        responseHeaders[key] = value;
                    });
                    return {
                        data,
                        status: response.status,
                        statusText: response.statusText,
                        headers: responseHeaders,
                    };
                }
                catch (error) {
                    if (error instanceof SkellarError) {
                        throw error;
                    }
                    if (error instanceof Error && error.name === 'AbortError') {
                        throw new ConnectionError(`Request timed out after ${this.timeout}ms`);
                    }
                    if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
                        if (attempt < this.maxRetries) {
                            attempt++;
                            await this.sleep(Math.pow(2, attempt) * 1000);
                            continue;
                        }
                        throw new ConnectionError('Failed to connect to Skellar API');
                    }
                    throw new SkellarError(`Request failed: ${error}`);
                }
            }
            throw new ConnectionError('Max retries exceeded');
        }
        async safeParseJSON(response) {
            try {
                const text = await response.text();
                return text ? JSON.parse(text) : {};
            }
            catch (_a) {
                return {};
            }
        }
        async getUserProfile() {
            const response = await this.makeRequest({
                method: 'GET',
                url: '/api/v1/users/profile/',
            });
            return response.data;
        }
        async completeStarNode(starbookSlug, chapterSlug, nodeSlug) {
            const response = await this.makeRequest({
                method: 'POST',
                url: `/api/v1/public/starbooks/${starbookSlug}/chapters/${chapterSlug}/nodes/${nodeSlug}/user-check-complete/`,
            });
            return response.data;
        }
        async getUserProgress(chapterSlug, userId) {
            const response = await this.makeRequest({
                method: 'GET',
                url: `/api/v1/starscriber/chapters/${chapterSlug}/progress/`,
                params: { user_id: userId },
            });
            return response.data.results;
        }
    }

    const VERSION = '0.1.0';

    exports.APIError = APIError;
    exports.AuthenticationError = AuthenticationError;
    exports.ConnectionError = ConnectionError;
    exports.NotFoundError = NotFoundError;
    exports.RateLimitError = RateLimitError;
    exports.SkellarClient = SkellarClient;
    exports.SkellarError = SkellarError;
    exports.VERSION = VERSION;
    exports.ValidationError = ValidationError;

}));
//# sourceMappingURL=skellar.umd.js.map
