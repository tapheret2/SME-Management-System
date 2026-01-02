/**
 * Cleans form data before sending to API.
 * Converts empty strings to null or undefined.
 * 
 * @param {Object} data - The form data object
 * @returns {Object} Cleaned data object
 */
export const cleanFormData = (data) => {
    const cleaned = { ...data };
    Object.keys(cleaned).forEach(key => {
        if (typeof cleaned[key] === 'string' && cleaned[key].trim() === '') {
            cleaned[key] = null;
        }
    });
    return cleaned;
};
