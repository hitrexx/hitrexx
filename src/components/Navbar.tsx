"use client";

import Link from "next/link";
import { signOut, useSession } from "next-auth/react";

export default function Navbar() {
  const { data: session, status } = useSession();

  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
        <Link href="/" className="text-lg font-semibold text-brand-600">
          КвартираРент
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="hover:text-brand-600">
            Каталог
          </Link>
          {status === "authenticated" ? (
            <>
              {session.user.role === "OWNER" && (
                <Link href="/apartments/new" className="hover:text-brand-600">
                  Разместить квартиру
                </Link>
              )}
              <Link href="/dashboard" className="hover:text-brand-600">
                Личный кабинет
              </Link>
              <span className="text-gray-500">{session.user.name}</span>
              <button
                onClick={() => signOut({ callbackUrl: "/" })}
                className="rounded bg-gray-100 px-3 py-1.5 hover:bg-gray-200"
              >
                Выйти
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-brand-600">
                Войти
              </Link>
              <Link
                href="/register"
                className="rounded bg-brand-500 px-3 py-1.5 text-white hover:bg-brand-600"
              >
                Регистрация
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
