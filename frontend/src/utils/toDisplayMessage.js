/**
 * converts any error object into a user-friendly string to avoid React render crashes.
 * strict requirement: MUST RETURN A STRING.
 */
export const toDisplayMessage = (error) => {
    try {
        if (!error) return 'Đã xảy ra lỗi không xác định.';
        if (typeof error === 'string') return error;

        // 1. Check for Axios/API response error structure
        const detail = error.response?.data?.detail;
        if (detail) {
            // Case A: Detail is a simple string
            if (typeof detail === 'string') return detail;

            // Case B: Detail is an array (e.g. Pydantic validation errors)
            if (Array.isArray(detail)) {
                return detail.map(item => {
                    if (typeof item === 'string') return item;
                    if (item && typeof item === 'object') {
                        return item.msg || item.message || JSON.stringify(item);
                    }
                    return String(item);
                }).join('; ');
            }

            // Case C: Detail is a single object
            if (typeof detail === 'object') {
                return detail.msg || detail.message || JSON.stringify(detail);
            }
        }

        // 2. Check for Standard JS Error
        if (error.message && typeof error.message === 'string') {
            return error.message;
        }

        // 3. Fallback for other objects
        return JSON.stringify(error);
    } catch (e) {
        console.error('Error normalizing message:', e);
        return 'Lỗi hệ thống (parse error)';
    }
};
