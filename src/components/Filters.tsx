"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export default function Filters() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [city, setCity] = useState(searchParams.get("city") ?? "");
  const [minPrice, setMinPrice] = useState(searchParams.get("minPrice") ?? "");
  const [maxPrice, setMaxPrice] = useState(searchParams.get("maxPrice") ?? "");
  const [rooms, setRooms] = useState(searchParams.get("rooms") ?? "");

  function applyFilters(e: React.FormEvent) {
    e.preventDefault();
    const params = new URLSearchParams();
    if (city) params.set("city", city);
    if (minPrice) params.set("minPrice", minPrice);
    if (maxPrice) params.set("maxPrice", maxPrice);
    if (rooms) params.set("rooms", rooms);
    router.push(`/?${params.toString()}`);
  }

  function reset() {
    setCity("");
    setMinPrice("");
    setMaxPrice("");
    setRooms("");
    router.push("/");
  }

  return (
    <form
      onSubmit={applyFilters}
      className="mb-8 grid grid-cols-2 gap-3 rounded-lg border border-gray-200 bg-white p-4 sm:grid-cols-5"
    >
      <input
        placeholder="Город"
        value={city}
        onChange={(e) => setCity(e.target.value)}
        className="rounded border border-gray-300 px-3 py-2 text-sm"
      />
      <input
        type="number"
        placeholder="Цена от"
        value={minPrice}
        onChange={(e) => setMinPrice(e.target.value)}
        className="rounded border border-gray-300 px-3 py-2 text-sm"
      />
      <input
        type="number"
        placeholder="Цена до"
        value={maxPrice}
        onChange={(e) => setMaxPrice(e.target.value)}
        className="rounded border border-gray-300 px-3 py-2 text-sm"
      />
      <select
        value={rooms}
        onChange={(e) => setRooms(e.target.value)}
        className="rounded border border-gray-300 px-3 py-2 text-sm"
      >
        <option value="">Комнат</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4+</option>
      </select>
      <div className="flex gap-2">
        <button
          type="submit"
          className="w-full rounded bg-brand-500 px-3 py-2 text-sm text-white hover:bg-brand-600"
        >
          Найти
        </button>
        <button
          type="button"
          onClick={reset}
          className="rounded bg-gray-100 px-3 py-2 text-sm hover:bg-gray-200"
        >
          Сброс
        </button>
      </div>
    </form>
  );
}
