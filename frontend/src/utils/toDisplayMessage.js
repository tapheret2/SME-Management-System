import React from 'react';

const safeStringify = (value) => {
    try {
        return JSON.stringify(value);
    } catch {
        return String(value);
    }
};

const isPlainObject = (value) => value !== null && typeof value === 'object' && !Array.isArray(value);

const formatValidationItem = (item) => {
    if (!item) return '';
    if (typeof item === 'string' || typeof item === 'number') return String(item);

    if (isPlainObject(item)) {
        const loc = Array.isArray(item.loc) ? item.loc.filter((part) => part !== 'body') : [];
        const path = loc.length ? loc.join('.') : '';
        const prefix = path ? `${path}: ` : '';
        return `${prefix}${item.msg || item.message || item.detail || safeStringify(item)}`;
    }

    return safeStringify(item);
};

const formatValidationErrors = (errors) => errors.map(formatValidationItem).filter(Boolean).join('\n');

export const assertRenderable = (value) => (
    typeof value === 'string'
    || typeof value === 'number'
    || React.isValidElement(value)
    || value == null
);

export const warnIfNotRenderable = (value, context = 'render') => {
    if (import.meta?.env?.DEV && !assertRenderable(value)) {
        console.warn(`[${context}] Non-renderable content supplied:`, value);
    }
};

export const toDisplayMessage = (error) => {
    try {
        if (error == null) return 'Đã xảy ra lỗi không xác định.';
        if (typeof error === 'string' || typeof error === 'number') return String(error);
        if (error instanceof Error && typeof error.message === 'string') return error.message;
        if (Array.isArray(error)) return formatValidationErrors(error);

        const responseData = error.response?.data ?? error.data ?? error.body ?? null;
        const detail = responseData?.detail ?? error.detail;

        if (typeof detail === 'string' || typeof detail === 'number') return String(detail);
        if (Array.isArray(detail)) return formatValidationErrors(detail);
        if (isPlainObject(detail)) return detail.msg || detail.message || safeStringify(detail);

        if (Array.isArray(responseData)) return formatValidationErrors(responseData);
        if (typeof responseData === 'string' || typeof responseData === 'number') return String(responseData);
        if (isPlainObject(responseData)) {
            if (responseData.detail) {
                return formatValidationErrors(Array.isArray(responseData.detail) ? responseData.detail : [responseData.detail]);
            }
            if (responseData.msg || responseData.message) return String(responseData.msg || responseData.message);
            if (responseData.error) return String(responseData.error);
        }

        return safeStringify(responseData ?? error);
    } catch (e) {
        console.error('Error normalizing message:', e);
        return 'Lỗi hệ thống (parse error)';
    }
};
