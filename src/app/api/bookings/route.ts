import { NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { z } from "zod";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { stripe } from "@/lib/stripe";

const bookingSchema = z.object({
  apartmentId: z.string(),
  startDate: z.string(),
  endDate: z.string(),
});

export async function POST(request: Request) {
  const session = await getServerSession(authOptions);
  if (!session?.user) {
    return NextResponse.json({ error: "Требуется вход в аккаунт" }, { status: 401 });
  }

  const parsed = bookingSchema.safeParse(await request.json());
  if (!parsed.success) {
    return NextResponse.json({ error: "Некорректные данные" }, { status: 400 });
  }

  const { apartmentId, startDate, endDate } = parsed.data;
  const start = new Date(startDate);
  const end = new Date(endDate);
  const nights = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24));

  if (nights <= 0) {
    return NextResponse.json({ error: "Некорректные даты" }, { status: 400 });
  }

  const apartment = await prisma.apartment.findUnique({ where: { id: apartmentId } });
  if (!apartment) {
    return NextResponse.json({ error: "Квартира не найдена" }, { status: 404 });
  }

  const totalPrice = nights * apartment.pricePerNight;

  const booking = await prisma.booking.create({
    data: {
      apartmentId,
      renterId: session.user.id,
      startDate: start,
      endDate: end,
      totalPrice,
      status: "PENDING",
    },
  });

  if (!process.env.STRIPE_SECRET_KEY) {
    return NextResponse.json({ bookingId: booking.id, checkoutUrl: null });
  }

  const checkoutSession = await stripe.checkout.sessions.create({
    mode: "payment",
    payment_method_types: ["card"],
    line_items: [
      {
        price_data: {
          currency: "rub",
          product_data: { name: `Аренда: ${apartment.title}` },
          unit_amount: totalPrice * 100,
        },
        quantity: 1,
      },
    ],
    success_url: `${process.env.NEXTAUTH_URL}/dashboard?booking=success`,
    cancel_url: `${process.env.NEXTAUTH_URL}/apartments/${apartmentId}?booking=cancelled`,
    metadata: { bookingId: booking.id },
  });

  await prisma.booking.update({
    where: { id: booking.id },
    data: { stripeSessionId: checkoutSession.id },
  });

  return NextResponse.json({ bookingId: booking.id, checkoutUrl: checkoutSession.url });
}
