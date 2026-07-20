import { prisma } from "@/lib/prisma";
import ApartmentCard from "@/components/ApartmentCard";
import Filters from "@/components/Filters";
import type { Prisma } from "@prisma/client";

type HomePageProps = {
  searchParams: Promise<{
    city?: string;
    minPrice?: string;
    maxPrice?: string;
    rooms?: string;
  }>;
};

export default async function HomePage({ searchParams }: HomePageProps) {
  const { city, minPrice, maxPrice, rooms } = await searchParams;

  const where: Prisma.ApartmentWhereInput = {};

  if (city) where.city = { contains: city, mode: "insensitive" };
  if (minPrice || maxPrice) {
    where.pricePerNight = {};
    if (minPrice) where.pricePerNight.gte = Number(minPrice);
    if (maxPrice) where.pricePerNight.lte = Number(maxPrice);
  }
  if (rooms) {
    where.rooms = rooms === "4" ? { gte: 4 } : Number(rooms);
  }

  const apartments = await prisma.apartment.findMany({
    where,
    orderBy: { createdAt: "desc" },
  });

  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Квартиры для аренды</h1>
      <Filters />
      {apartments.length === 0 ? (
        <p className="text-gray-500">Ничего не найдено по вашим фильтрам.</p>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {apartments.map((apartment) => (
            <ApartmentCard
              key={apartment.id}
              id={apartment.id}
              title={apartment.title}
              city={apartment.city}
              address={apartment.address}
              pricePerNight={apartment.pricePerNight}
              rooms={apartment.rooms}
              area={apartment.area}
              image={apartment.images[0]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
