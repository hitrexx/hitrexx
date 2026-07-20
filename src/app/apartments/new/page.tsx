"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";

export default function NewApartmentPage() {
  const router = useRouter();
  const { data: session, status } = useSession();
  const [form, setForm] = useState({
    title: "",
    description: "",
    city: "",
    address: "",
    pricePerNight: "",
    rooms: "1",
    area: "",
    image: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (status === "authenticated" && session.user.role !== "OWNER") {
    return (
      <p className="text-gray-600">
        Размещать квартиры могут только пользователи с ролью «Владелец».
      </p>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    const res = await fetch("/api/apartments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: form.title,
        description: form.description,
        city: form.city,
        address: form.address,
        pricePerNight: Number(form.pricePerNight),
        rooms: Number(form.rooms),
        area: Number(form.area),
        images: form.image ? [form.image] : [],
      }),
    });

    const data = await res.json();
    setLoading(false);

    if (!res.ok) {
      setError(data.error ?? "Не удалось создать объявление");
      return;
    }

    router.push(`/apartments/${data.id}`);
  }

  return (
    <div className="mx-auto max-w-xl">
      <h1 className="mb-6 text-2xl font-semibold">Разместить квартиру</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Название</label>
          <input
            required
            value={form.title}
            onChange={(e) => setForm({ ...form, title: e.target.value })}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Описание</label>
          <textarea
            required
            rows={4}
            value={form.description}
            onChange={(e) => setForm({ ...form, description: e.target.value })}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium">Город</label>
            <input
              required
              value={form.city}
              onChange={(e) => setForm({ ...form, city: e.target.value })}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Адрес</label>
            <input
              required
              value={form.address}
              onChange={(e) => setForm({ ...form, address: e.target.value })}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="mb-1 block text-sm font-medium">Цена/ночь ₽</label>
            <input
              type="number"
              required
              min={1}
              value={form.pricePerNight}
              onChange={(e) => setForm({ ...form, pricePerNight: e.target.value })}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Комнат</label>
            <input
              type="number"
              required
              min={1}
              value={form.rooms}
              onChange={(e) => setForm({ ...form, rooms: e.target.value })}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Площадь м²</label>
            <input
              type="number"
              required
              min={1}
              value={form.area}
              onChange={(e) => setForm({ ...form, area: e.target.value })}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Ссылка на фото (необязательно)</label>
          <input
            value={form.image}
            onChange={(e) => setForm({ ...form, image: e.target.value })}
            placeholder="https://..."
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded bg-brand-500 px-4 py-2 text-white hover:bg-brand-600 disabled:opacity-50"
        >
          {loading ? "Публикация..." : "Опубликовать объявление"}
        </button>
      </form>
    </div>
  );
}
