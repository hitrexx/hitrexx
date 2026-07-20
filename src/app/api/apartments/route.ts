import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { z } from "zod";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

const apartmentSchema = z.object({
  title: z.string().min(3),
  description: z.string().min(10),
  city: z.string().min(2),
  address: z.string().min(3),
  pricePerNight: z.number().positive(),
  rooms: z.number().int().positive(),
  area: z.number().positive(),
  images: z.array(z.string().url()).default([]),
});

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: "Требуется вход в аккаунт" }, { status: 401 });
  }
  if (session.user.role !== "OWNER") {
    return NextResponse.json(
      { error: "Только владельцы могут размещать квартиры" },
      { status: 403 }
    );
  }

  const parsed = apartmentSchema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Некорректные данные" }, { status: 400 });
  }

  const apartment = await prisma.apartment.create({
    data: { ...parsed.data, ownerId: session.user.id },
  });

  return NextResponse.json(apartment, { status: 201 });
}
