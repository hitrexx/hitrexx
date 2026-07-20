"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";

export default function BookingForm({
  apartmentId,
  pricePerNight,
}: {
  apartmentId: string;
  pricePerNight: number;
}) {
  const { data: session, status } = useSession();
  const router = useRouter();
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const nights =
    startDate && endDate
      ? Math.max(
          0,
          Math.round(
            (new Date(endDate).getTime() - new Date(startDate).getTime()) /
              (1000 * 60 * 60 * 24)
          )
        )
      : 0;
  const total = nights * pricePerNight;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (status !== "authenticated") {
      router.push("/login");
      return;
    }

    if (nights <= 0) {
      setError("Выберите корректные даты заезда и выезда");
      return;
    }

    setLoading(true);

    const res = await fetch("/api/bookings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apartmentId, startDate, endDate }),
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      setError(data.error ?? "Не удалось создать бронирование");
      return;
    }

    if (data.checkoutUrl) {
      window.location.href = data.checkoutUrl;
    } else {
      router.push("/dashboard");
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-4 rounded-lg border border-gray-200 bg-white p-5"
    >
      <h3 className="font-semibold">Забронировать квартиру</h3>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="mb-1 block text-sm font-medium">Заезд</label>
          <input
            type="date"
            required
            value={startDate}
            min={new Date().toISOString().split("T")[0]}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Выезд</label>
          <input
            type="date"
            required
            value={endDate}
            min={startDate || new Date().toISOString().split("T")[0]}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full rounded border border-gray-300 px-3 py-2 text-sm"
          />
        </div>
      </div>
      {nights > 0 && (
        <p className="text-sm text-gray-600">
          {nights} ноч. × {pricePerNight.toLocaleString("ru-RU")} ₽ ={" "}
          <span className="font-semibold">{total.toLocaleString("ru-RU")} ₽</span>
        </p>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={loading}
        className="w-full rounded bg-brand-500 px-4 py-2 text-white hover:bg-brand-600 disabled:opacity-50"
      >
        {loading ? "Обработка..." : "Забронировать и оплатить"}
      </button>
    </form>
  );
}
