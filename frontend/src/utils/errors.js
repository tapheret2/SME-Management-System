/**
 * Safely extracts a string error message from an API error response.
 * Handles FastAPIs Pydantic validation errors (array/object) and generic HTTP errors.
 * 
 * @param {any} error - The error object from axios or elsewhere
 * @param {string} defaultMessage - Fallback message if no details found
 * @returns {string} A safe string message
 */
export const getErrorMessage = (error, defaultMessage = 'Có lỗi xảy ra') => {
    if (!error) return defaultMessage;

    // Log for debugging
    console.error('API Error:', error);

    const detail = error.response?.data?.detail;

    try {
        // 1. If detail is a simple string
        if (typeof detail === 'string') {
            return detail;
        }

        // 2. If detail is an array (Pydantic validation errors)
        if (Array.isArray(detail) && detail.length > 0) {
            const firstError = detail[0];
            if (typeof firstError === 'string') {
                return firstError;
            }
            if (typeof firstError === 'object' && firstError !== null) {
                // Ensure we return a string
                return String(firstError.msg || firstError.message || JSON.stringify(firstError));
            }
        }

        // 3. If detail is a single object
        if (typeof detail === 'object' && detail !== null) {
            return String(detail.msg || detail.message || JSON.stringify(detail));
        }
    } catch (e) {
        console.error('Error parsing error message:', e);
    }

    // 4. Fallback
    return defaultMessage;
};
