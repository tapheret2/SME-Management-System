import { toDisplayMessage } from './toDisplayMessage';

/**
 * LEGACY ADAPTER
 * Redirects all calls to the new safe `toDisplayMessage` utility.
 * This ensures any file still importing `getErrorMessage` gets the safe logic.
 */
export const getErrorMessage = (error, defaultMessage = 'Có lỗi xảy ra') => {
    const msg = toDisplayMessage(error);
    if (msg === 'Đã xảy ra lỗi không xác định.' && defaultMessage) {
        return defaultMessage;
    }
    return msg;
};
