import Image from "next/image";
import Link from "next/link";

type ApartmentCardProps = {
  id: string;
  title: string;
  city: string;
  address: string;
  pricePerNight: number;
  rooms: number;
  area: number;
  image?: string;
};

export default function ApartmentCard({
  id,
  title,
  city,
  address,
  pricePerNight,
  rooms,
  area,
  image,
}: ApartmentCardProps) {
  return (
    <Link
      href={`/apartments/${id}`}
      className="block overflow-hidden rounded-lg border border-gray-200 bg-white transition hover:shadow-md"
    >
      <div className="relative h-48 w-full bg-gray-100">
        {image ? (
          <Image src={image} alt={title} fill className="object-cover" />
        ) : (
          <div className="flex h-full items-center justify-center text-gray-400">
            Нет фото
          </div>
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold">{title}</h3>
        <p className="text-sm text-gray-500">
          {city}, {address}
        </p>
        <p className="mt-1 text-sm text-gray-500">
          {rooms} комн. · {area} м²
        </p>
        <p className="mt-2 text-lg font-semibold text-brand-600">
          {pricePerNight.toLocaleString("ru-RU")} ₽ / ночь
        </p>
      </div>
    </Link>
  );
}
