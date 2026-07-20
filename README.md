# КвартираРент

Сайт для поиска и аренды квартир: каталог с фильтрами, карточки квартир,
бронирование с оплатой через Stripe Checkout, личные кабинеты для
арендаторов и владельцев.

## Стек

- Next.js 15 (App Router) + TypeScript
- PostgreSQL + Prisma
- NextAuth (email/пароль)
- Stripe Checkout (оплата бронирований)
- Tailwind CSS

## Запуск локально

1. Установите зависимости:

   ```bash
   npm install
   ```

2. Создайте `.env` на основе `.env.example` и укажите строку подключения к
   своей PostgreSQL:

   ```bash
   cp .env.example .env
   ```

3. Примените миграции и заполните базу тестовыми данными:

   ```bash
   npx prisma migrate dev
   npm run prisma:seed
   ```

   Тестовые аккаунты после сидирования:
   - `owner@example.com` / `owner12345` — владелец, видит свои объявления и брони
   - `renter@example.com` / `renter12345` — арендатор, видит свои брони

4. Запустите dev-сервер:

   ```bash
   npm run dev
   ```

   Сайт будет доступен на http://localhost:3000

## Оплата (Stripe)

Оплата опциональна: без `STRIPE_SECRET_KEY` бронирование создаётся сразу
в статусе «Ожидает оплаты» без перенаправления на оплату. Чтобы включить
реальную оплату:

1. Добавьте `STRIPE_SECRET_KEY` в `.env`.
2. Настройте вебхук на `checkout.session.completed` (в проде — на
   `/api/stripe/webhook`), укажите его секрет как `STRIPE_WEBHOOK_SECRET`.
   Локально удобно использовать `stripe listen --forward-to localhost:3000/api/stripe/webhook`.
3. После успешной оплаты вебхук переводит бронирование в статус
   «Подтверждено».

## Структура

- `src/app` — страницы и API-роуты (App Router)
- `src/components` — переиспользуемые UI-компоненты
- `src/lib` — Prisma-клиент, конфигурация NextAuth, Stripe
- `prisma/schema.prisma` — модели User / Apartment / Booking
- `prisma/seed.ts` — тестовые данные

## Известные предупреждения аудита

`next-auth@4` тянет устаревший `uuid@8` (умеренная уязвимость, нет фикса
в ветке v4 без перехода на v5-beta). Остальные критические/высокие
уязвимости устранены обновлением Next.js до патч-версии 15.5.16+.

Локфайл `package-lock.json` не хранится в репозитории — сгенерируйте его
командой `npm install` (версии зависимостей зафиксированы в `package.json`).
