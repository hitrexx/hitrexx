# ЮДОМ — сайт на Java

Сайт группы строительных компаний «ЮДОМ»: каталог проектов домов, окно проекта с планировкой и площадями комнат, формы заявок.

Сервер на **Java 21 + Spring Boot**: он отдаёт страницу, данные проектов и принимает заявки.

## Как устроено

```
src/main/
├── java/ru/yudom/
│   ├── YudomApplication.java      — точка входа (запуск сервера)
│   ├── project/
│   │   ├── Project.java           — модель проекта; считает общую площадь и цену «от»
│   │   ├── ProjectService.java    — читает каталог из projects.json
│   │   └── ProjectController.java — GET /api/projects, GET /api/projects/{id}
│   └── lead/
│       ├── Lead.java              — заявка + проверка полей (имя, телефон)
│       ├── LeadService.java       — сохраняет заявку в CSV и шлёт в Telegram
│       └── LeadController.java    — POST /api/leads
└── resources/
    ├── application.properties     — настройки (порт, файл заявок, Telegram)
    ├── projects.json              — КАТАЛОГ ДОМОВ (редактировать тут)
    └── static/                    — то, что видит браузер
        ├── index.html             — разметка страницы
        ├── css/style.css          — оформление
        ├── js/app.js              — меню, слайдер, окно проекта, отправка форм
        └── img/                   — фото и планировки
```

Как это работает:

1. Браузер открывает `/` и получает `index.html`, CSS, JS и картинки.
2. `app.js` запрашивает `/api/projects`. Java читает `projects.json`, досчитывает площадь и минимальную цену и отдаёт JSON. Из него строятся карточки и окна проектов.
3. При отправке формы `app.js` шлёт заявку на `/api/leads`. Java проверяет имя и телефон, дописывает строку в `data/leads.csv` (открывается в Excel) и, если настроен бот, присылает сообщение в Telegram.

### Как добавить проект

1. Положите фото в `src/main/resources/static/img/`.
2. Скопируйте блок проекта в `src/main/resources/projects.json` и замените данные. Если не указать `area`, площадь посчитается как сумма комнат. Цена: либо `"price": 5030000` (под ключ), либо список `"prices"` с вариантами отделки.
3. Пересоберите и перезапустите сервер.

## Запуск на своём компьютере

Нужны **Java 21** и **Maven** (или откройте проект в IntelliJ IDEA, она подтянет всё сама и запустит `YudomApplication`).

```bash
mvn spring-boot:run
```

Откройте http://localhost:8080.

Собрать один файл и запустить его:

```bash
mvn package
java -jar target/yudom-site.jar
```

## Уведомления о заявках в Telegram

1. Напишите [@BotFather](https://t.me/BotFather) команду `/newbot` и получите **токен**.
2. Напишите своему боту любое сообщение, затем откройте `https://api.telegram.org/bot<ТОКЕН>/getUpdates` и найдите `"chat":{"id": ...}`. Это **chat id**.
3. Задайте переменные окружения перед запуском:

```bash
export TELEGRAM_BOT_TOKEN=123456:ABC...
export TELEGRAM_CHAT_ID=123456789
java -jar target/yudom-site.jar
```

Токен не кладите в код и в GitHub, только в переменные окружения на хостинге.

## Как выложить в открытый доступ

Java-сайту нужен сервер, который постоянно запускает программу (GitHub Pages не подойдёт: он умеет только статичные файлы). Для этого в проекте есть `Dockerfile`, его понимают почти все хостинги.

### Вариант 1. Render.com (бесплатно, проще всего)

1. Залейте проект на GitHub (он уже там).
2. Зарегистрируйтесь на https://render.com через GitHub.
3. **New → Web Service** → выберите репозиторий → Render сам найдёт `Dockerfile`.
4. Ветка: `main` (или та, где лежит код). Тариф: **Free**.
5. В **Environment** добавьте `TELEGRAM_BOT_TOKEN` и `TELEGRAM_CHAT_ID`.
6. **Create Web Service**. Через несколько минут сайт будет по адресу вида `https://yudom.onrender.com`.

На бесплатном тарифе сайт «засыпает» без посетителей (первое открытие ~30–60 с), а файл `leads.csv` стирается при перезапуске. Поэтому заявки обязательно получайте в Telegram.

### Вариант 2. Российский хостинг (Amvera, Timeweb Cloud Apps)

Тоже умеют собирать по `Dockerfile` из GitHub: создайте приложение, укажите репозиторий, порт `8080`, добавьте переменные Telegram. Удобно, если оплата нужна российской картой и сайт для российских клиентов.

### Вариант 3. Свой VPS (полный контроль, ~200–500 ₽/мес)

На сервере с Ubuntu:

```bash
sudo apt install -y docker.io git
git clone https://github.com/hitrexx/hitrexx.git && cd hitrexx
sudo docker build -t yudom .
sudo docker run -d --restart=always -p 80:8080 \
  -v /opt/yudom-data:/app/data \
  -e TELEGRAM_BOT_TOKEN=... -e TELEGRAM_CHAT_ID=... \
  --name yudom yudom
```

Сайт откроется по IP сервера, заявки будут копиться в `/opt/yudom-data/leads.csv`.

### Свой домен (yudom.ru и т.п.)

1. Купите домен у регистратора (REG.RU, Timeweb, Nic.ru).
2. На хостинге добавьте домен в настройках (Render: **Settings → Custom Domains**) и посмотрите, какую DNS-запись он просит.
3. У регистратора добавьте эту запись (`CNAME` или `A`). HTTPS-сертификат Render/Amvera выпустят сами.

### Перед публикацией

- Замените заглушки (подчёркнуты пунктиром на странице): адрес, почту, часы работы, срок гарантии «N лет».
- Сайт собирает имена и телефоны, поэтому по 152-ФЗ нужна страница «Политика обработки персональных данных», ссылку на неё стоит поставить рядом с кнопками форм.
