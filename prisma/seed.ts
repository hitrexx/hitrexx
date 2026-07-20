import { PrismaClient } from "@prisma/client";
import bcrypt from "bcryptjs";

const prisma = new PrismaClient();

async function main() {
  const ownerPassword = await bcrypt.hash("owner12345", 10);
  const renterPassword = await bcrypt.hash("renter12345", 10);

  const owner = await prisma.user.upsert({
    where: { email: "owner@example.com" },
    update: {},
    create: {
      email: "owner@example.com",
      password: ownerPassword,
      name: "Иван Владелец",
      role: "OWNER",
    },
  });

  await prisma.user.upsert({
    where: { email: "renter@example.com" },
    update: {},
    create: {
      email: "renter@example.com",
      password: renterPassword,
      name: "Мария Арендатор",
      role: "RENTER",
    },
  });

  const apartments = [
    {
      title: "Уютная студия в центре",
      description: "Светлая студия рядом с метро, свежий ремонт, вся техника.",
      city: "Москва",
      address: "ул. Тверская, 12",
      pricePerNight: 3500,
      rooms: 1,
      area: 32,
      images: ["https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800"],
    },
    {
      title: "Просторная 2-комнатная квартира",
      description: "Квартира с видом на парк, два балкона, подземная парковка.",
      city: "Санкт-Петербург",
      address: "Невский пр., 45",
      pricePerNight: 5200,
      rooms: 2,
      area: 58,
      images: ["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800"],
    },
    {
      title: "Однушка у моря",
      description: "5 минут пешком до пляжа, кондиционер, есть Wi-Fi.",
      city: "Сочи",
      address: "ул. Приморская, 8",
      pricePerNight: 4100,
      rooms: 1,
      area: 40,
      images: ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800"],
    },
    {
      title: "Семейная 3-комнатная квартира",
      description: "Тихий двор, рядом школа и детский сад, вся мебель.",
      city: "Казань",
      address: "ул. Баумана, 3",
      pricePerNight: 4800,
      rooms: 3,
      area: 75,
      images: ["https://images.unsplash.com/photo-1560185127-6ed189bf02f4?w=800"],
    },
  ];

  for (const apartment of apartments) {
    await prisma.apartment.create({
      data: { ...apartment, ownerId: owner.id },
    });
  }

  console.log("Сид данные загружены. Тестовые аккаунты:");
  console.log("  owner@example.com / owner12345 (владелец)");
  console.log("  renter@example.com / renter12345 (арендатор)");
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
