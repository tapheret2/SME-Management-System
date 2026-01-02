/**
 * converts any error object into a user-friendly string to avoid React render crashes.
 * strict requirement: MUST RETURN A STRING.
 */
export const toDisplayMessage = (error) => {
    try {
        if (error === null || error === undefined) return 'Lỗi không xác định (null)';
        if (typeof error === 'string') return error;
        if (typeof error === 'number') return String(error);
        if (typeof error === 'boolean') return String(error);

        // 1. Check for Axios/API response error structure
        const detail = error.response?.data?.detail;
        if (detail) {
            // Case A: Detail is a simple string
            if (typeof detail === 'string') return detail;

            // Case B: Detail is an array (e.g. Pydantic validation errors)
            if (Array.isArray(detail)) {
                return detail.map(item => {
                    if (item === null || item === undefined) return '';
                    if (typeof item === 'string') return item;
                    if (typeof item === 'object') {
                        // Extract field path
                        let prefix = '';
                        if (item.loc && Array.isArray(item.loc)) {
                            // Filter out 'body' or other generic keywords if desired
                            const path = item.loc.filter(p => p !== 'body').join('.');
                            if (path) prefix = `${path}: `;
                        }
                        return `${prefix}${String(item.msg || item.message || JSON.stringify(item))}`;
                    }
                    return String(item);
                }).join('\n');
            }

            // Case C: Detail is a single object
            if (typeof detail === 'object') {
                return String(detail.msg || detail.message || JSON.stringify(detail));
            }
        }

        // 2. Check for Standard JS Error
        if (error.message && typeof error.message === 'string') {
            return error.message;
        }

        // 3. Last resort fallback
        // If it's a cyclic structure, JSON.stringify might throw.
        try {
            return JSON.stringify(error);
        } catch (jsonError) {
            return 'Lỗi chi tiết (không thể hiển thị)';
        }

    } catch (e) {
        console.error('Error normalizing message:', e);
        return 'Lỗi hệ thống (parse error)';
    }
};
