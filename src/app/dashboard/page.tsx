import Link from "next/link";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const statusLabels: Record<string, string> = {
  PENDING: "Ожидает оплаты",
  CONFIRMED: "Подтверждено",
  CANCELLED: "Отменено",
};

export default async function DashboardPage() {
  const session = await getServerSession(authOptions);
  if (!session?.user) redirect("/login");

  if (session.user.role === "OWNER") {
    const apartments = await prisma.apartment.findMany({
      where: { ownerId: session.user.id },
      include: { bookings: { include: { renter: true }, orderBy: { createdAt: "desc" } } },
      orderBy: { createdAt: "desc" },
    });

    return (
      <div>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Мои квартиры</h1>
          <Link
            href="/apartments/new"
            className="rounded bg-brand-500 px-4 py-2 text-sm text-white hover:bg-brand-600"
          >
            + Разместить квартиру
          </Link>
        </div>
        {apartments.length === 0 ? (
          <p className="text-gray-500">У вас пока нет объявлений.</p>
        ) : (
          <div className="space-y-6">
            {apartments.map((apartment) => (
              <div key={apartment.id} className="rounded-lg border border-gray-200 bg-white p-5">
                <div className="flex items-center justify-between">
                  <Link href={`/apartments/${apartment.id}`} className="font-semibold hover:text-brand-600">
                    {apartment.title}
                  </Link>
                  <span className="text-sm text-gray-500">
                    {apartment.city}, {apartment.address}
                  </span>
                </div>
                <p className="mt-2 text-sm text-gray-500">Бронирования:</p>
                {apartment.bookings.length === 0 ? (
                  <p className="text-sm text-gray-400">Пока нет бронирований</p>
                ) : (
                  <ul className="mt-1 space-y-1 text-sm">
                    {apartment.bookings.map((booking) => (
                      <li key={booking.id} className="flex justify-between">
                        <span>
                          {booking.renter.name} ·{" "}
                          {new Date(booking.startDate).toLocaleDateString("ru-RU")} —{" "}
                          {new Date(booking.endDate).toLocaleDateString("ru-RU")}
                        </span>
                        <span className="font-medium">{statusLabels[booking.status]}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  const bookings = await prisma.booking.findMany({
    where: { renterId: session.user.id },
    include: { apartment: true },
    orderBy: { createdAt: "desc" },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Мои бронирования</h1>
      {bookings.length === 0 ? (
        <p className="text-gray-500">
          У вас пока нет бронирований.{" "}
          <Link href="/" className="text-brand-600">
            Найти квартиру
          </Link>
        </p>
      ) : (
        <div className="space-y-4">
          {bookings.map((booking) => (
            <div key={booking.id} className="rounded-lg border border-gray-200 bg-white p-5">
              <div className="flex items-center justify-between">
                <Link
                  href={`/apartments/${booking.apartment.id}`}
                  className="font-semibold hover:text-brand-600"
                >
                  {booking.apartment.title}
                </Link>
                <span className="text-sm font-medium">{statusLabels[booking.status]}</span>
              </div>
              <p className="mt-1 text-sm text-gray-500">
                {booking.apartment.city}, {booking.apartment.address}
              </p>
              <p className="mt-1 text-sm text-gray-500">
                {new Date(booking.startDate).toLocaleDateString("ru-RU")} —{" "}
                {new Date(booking.endDate).toLocaleDateString("ru-RU")}
              </p>
              <p className="mt-1 font-semibold text-brand-600">
                {booking.totalPrice.toLocaleString("ru-RU")} ₽
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
