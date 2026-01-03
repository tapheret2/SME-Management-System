import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';
import { toDisplayMessage } from '../utils/toDisplayMessage';

export default function Login() {
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const { register, handleSubmit, formState: { errors } } = useForm();

    const onSubmit = async (data) => {
        setLoading(true);
        try {
            await login(data.email, data.password);
            toast.success('Đăng nhập thành công!');
        } catch (error) {
            console.error('Login error:', error);
            const message = toDisplayMessage(error);
            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-500 to-primary-700 px-4">
            <div className="max-w-md w-full">
                <div className="bg-white rounded-2xl shadow-2xl p-8">
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-gray-900">SME System</h1>
                        <p className="mt-2 text-gray-600">Đăng nhập để tiếp tục</p>
                    </div>

                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
                        <div>
                            <label htmlFor="email" className="form-label">
                                Email
                            </label>
                            <input
                                id="email"
                                type="email"
                                {...register('email', {
                                    required: 'Vui lòng nhập email',
                                    pattern: {
                                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                                        message: 'Email không hợp lệ'
                                    }
                                })}
                                className="form-input"
                                placeholder="name@company.com"
                            />
                            {errors.email && <p className="form-error">{errors.email.message}</p>}
                        </div>

                        <div>
                            <label htmlFor="password" className="form-label">
                                Mật khẩu
                            </label>
                            <input
                                id="password"
                                type="password"
                                {...register('password', {
                                    required: 'Vui lòng nhập mật khẩu',
                                    minLength: {
                                        value: 8,
                                        message: 'Mật khẩu phải có ít nhất 8 ký tự'
                                    },
                                    pattern: {
                                        value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/,
                                        message: 'Mật khẩu phải có chữ hoa, chữ thường và số'
                                    }
                                })}
                                className="form-input"
                                placeholder="••••••••"
                            />
                            {errors.password && <p className="form-error">{errors.password.message}</p>}
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn-primary py-3"
                        >
                            {loading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                    </svg>
                                    Đang đăng nhập...
                                </span>
                            ) : (
                                'Đăng nhập'
                            )}
                        </button>
                    </form>

                    <div className="mt-6 text-center text-sm text-gray-500">
                        <p>Demo accounts:</p>
                        <p className="mt-1">admin@sme.com / Admin123!</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
