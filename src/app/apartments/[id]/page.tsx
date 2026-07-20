import Image from "next/image";
import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import BookingForm from "@/components/BookingForm";

export default async function ApartmentPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const apartment = await prisma.apartment.findUnique({
    where: { id },
    include: { owner: { select: { name: true } } },
  });

  if (!apartment) notFound();

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <div className="relative mb-4 h-80 w-full overflow-hidden rounded-lg bg-gray-100">
          {apartment.images[0] ? (
            <Image
              src={apartment.images[0]}
              alt={apartment.title}
              fill
              className="object-cover"
            />
          ) : (
            <div className="flex h-full items-center justify-center text-gray-400">
              Нет фото
            </div>
          )}
        </div>
        <h1 className="text-2xl font-semibold">{apartment.title}</h1>
        <p className="mt-1 text-gray-500">
          {apartment.city}, {apartment.address}
        </p>
        <p className="mt-1 text-gray-500">
          {apartment.rooms} комн. · {apartment.area} м² · Владелец: {apartment.owner.name}
        </p>
        <p className="mt-4 text-gray-700">{apartment.description}</p>
        <p className="mt-4 text-xl font-semibold text-brand-600">
          {apartment.pricePerNight.toLocaleString("ru-RU")} ₽ / ночь
        </p>
      </div>
      <div>
        <BookingForm apartmentId={apartment.id} pricePerNight={apartment.pricePerNight} />
      </div>
    </div>
  );
}
