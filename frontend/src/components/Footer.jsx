export default function Footer() {
    return (
        <footer className="bg-white border-t border-gray-200 mt-auto">
            <div className="mx-auto max-w-7xl px-6 py-6 lg:px-8">
                <p className="text-center text-xs leading-5 text-gray-500">
                    &copy; {new Date().getFullYear()} Peganyx, Inc. All rights reserved.
                </p>
            </div>
        </footer>
    );
}
