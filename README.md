


# Termina

Brauzerda Linux terminal buyruqlarini **xavfsiz** mashq qilish uchun backend API.
Foydalanuvchi topshiriq oladi (masalan, papka va fayl yaratish), buyruqlarni yozadi,
`check` bilan tekshiradi va XP, daraja hamda streak yutadi.

## Imkoniyatlari

- **Terminal emulyatsiyasi.** Buyruqlar `subprocess` orqali emas, Python ichida
  bajariladi va faqat ruxsat etilgan ro'yxatdan ishlaydi (whitelist).
- **Alohida workspace.** Har bir foydalanuvchi o'z papkasida ishlaydi, undan tashqariga chiqa olmaydi.
- **Topshiriqlar tizimi.** Topshiriq maqsadli fayl strukturasi (`JSON`) sifatida saqlanadi,
  tekshiruv rekursiv bajariladi.
- **Fon tekshiruvi.** `check` natijasi Celery orqali asinxron hisoblanadi.
- **Gamifikatsiya.** XP, daraja (level), ketma-ket muvaffaqiyat (streak).
- **Xavfsizlik.** JWT autentifikatsiya, so'rovlar chastotasini cheklash (throttling),
  fayl hajmi chegarasi, yo'l (`../`) hujumlaridan himoya.
- **Hujjatlar.** Swagger va ReDoc (drf-spectacular).

## Texnologiyalar

Python 3.12 · Django · Django REST Framework · SimpleJWT · PostgreSQL ·
Celery · Redis · drf-spectacular · django-import-export · WhiteNoise · Gunicorn · Docker Compose

## Tezkor ishga tushirish (Docker)

Talab: Docker va Docker Compose v2 (`docker compose version`).

```bash
git clone https://github.com/oydinov012/termina.git
cd termina

cp src/.env.example src/.env       # keyin src/.env ni tahrirlang (pastga qarang)
docker compose up --build -d

docker compose exec web python manage.py createsuperuser
```

Tayyor bo'lgach:

| Manzil | Vazifasi |
|---|---|
| http://127.0.0.1:8000/api/docs/ | Swagger UI |
| http://127.0.0.1:8000/api/redoc/ | ReDoc |
| http://127.0.0.1:8000/admin/ | Admin panel |

Migratsiyalar va `collectstatic` `web` konteyneri ishga tushganda avtomatik bajariladi.

### Sozlamalar (`src/.env`)

| O'zgaruvchi | Izoh |
|---|---|
| `SECRET_KEY` | Uzun tasodifiy kalit: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `DEBUG` | Lokalda `True`, serverda `False` |
| `ALLOWED_HOSTS` | Vergul bilan: `127.0.0.1,localhost` |
| `CORS_ALLOWED_ORIGINS` | Frontend manzillari, masalan `http://localhost:5174` |
| `CSRF_TRUSTED_ORIGINS` | Ishonchli manzillar (`https://` bilan to'liq yoziladi) |
| `SECURE_SSL_REDIRECT` | Faqat HTTPS sozlangan serverda `True` |
| `DB_ENGINE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Django'ning baza ulanishi. Docker'da `DB_HOST=db` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Postgres konteyneri uchun. **`DB_*` bilan bir xil bo'lishi shart** |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD` | Celery uchun. Docker'da `REDIS_HOST=redis` |

> `.env` faylini hech qachon GitHub'ga yubormang (`.gitignore` da bor).
> Parolda `@ : / # %` belgilarini ishlatmang, chunki u Redis URL ichida ishlatiladi.

Postgres konteyneri bazani birinchi ishga tushganda `POSTGRES_*` qiymatlaridan o'zi yaratadi.
Keyinroq parolni o'zgartirsangiz, eski volume'ni o'chirish kerak: `docker compose down -v`
(bazadagi ma'lumotlar yo'qoladi).

## Foydalanish tartibi

1. **Ro'yxatdan o'tish** va **login** qiling, `access` tokenni oling.
2. Topshiriqlarni admin panel orqali yuklang (quyida).
3. `GET /task/` bilan topshiriq oling, javobdagi `task_id` ni eslab qoling.
4. `POST /terminal/` orqali `start <task_id>` yozing. Topshiriq papkasi yaratiladi.
5. Shu papkada buyruqlar bilan vazifani bajaring (`mkdir`, `touch`, `nano` va h.k.).
6. `check` yozing. Javobda `celery_task_id` keladi.
7. `GET /api/task-status/<celery_task_id>/` ni natija tayyor bo'lguncha so'rab turing (polling).

Swagger'da tokenni **Authorize** tugmasi orqali `Bearer <access>` shaklida kiriting.

## Terminal buyruqlari

| Buyruq | Vazifasi |
|---|---|
| `pwd` | Joriy papka |
| `ls` | Papka ichidagilar |
| `cd <papka>` / `cd ..` | Papkaga o'tish |
| `mkdir <nom>` | Papka yaratish (bitta papkada ko'pi bilan 20 ta element) |
| `touch <nom>` | Bo'sh fayl yaratish |
| `cat <fayl>` | Fayl mazmunini ko'rish |
| `cp <manba> <maqsad>` | Nusxa ko'chirish |
| `mv <manba> <maqsad>` | Ko'chirish / nomini o'zgartirish |
| `rm <nom>` | Fayl yoki papkani o'chirish |
| `nano <fayl>` | Faylni tahrirlash uchun ochish (saqlash alohida so'rov bilan) |
| `start <id>` | Topshiriqni boshlash |
| `check` | Joriy topshiriqni tekshirish (topshiriq papkasi ichida turib yoziladi) |
| `help` | Qo'llanma |

Cheklovlar: bitta fayl **100 KB** dan oshmasligi kerak, workspace'dan tashqariga chiqib bo'lmaydi,
ro'yxatda yo'q buyruqlar rad etiladi.

## API endpointlari

| Metod | URL | Autentifikatsiya | Vazifasi |
|---|---|---|---|
| POST | `/api/auth/register/` | yo'q | Ro'yxatdan o'tish (`username`, `email`, `password`) |
| POST | `/api/auth/login/` | yo'q | Login, `access` va `refresh` token |
| POST | `/api/auth/token/refresh/` | yo'q | Access tokenni yangilash |
| GET | `/api/profile/` | JWT | Daraja, XP, streak, bajarilgan topshiriqlar |
| GET/PUT/PATCH/DELETE | `/api/profile1/` | JWT | Foydalanuvchi ma'lumotlarini ko'rish, yangilash, hisobni o'chirish |
| GET | `/task/` | JWT | Yangi topshiriq olish |
| POST | `/task/` | JWT | Topshiriqni bevosita tekshirish (`{"task_id": 1}`) |
| POST | `/terminal/` | JWT | Terminal buyrug'ini bajarish |
| GET | `/api/task-status/<id>/` | JWT | Fon tekshiruvi holati va natijasi |

**Terminal so'rovi:**

```json
{ "command": "mkdir loyiha" }
```

Nano ichida faylni saqlash:

```json
{ "type": "nano_save", "path": "hello.txt", "content": "Salom dunyo" }
```

**Terminal javobi:**

```json
{
  "result": { "type": "output", "output": "Papka yaratildi: loyiha" },
  "current_path": "~",
  "structure": ["loyiha"]
}
```

So'rovlar chastotasi: anonim foydalanuvchi uchun daqiqasiga 10 ta, login qilgan foydalanuvchi
uchun 20 ta. JWT: access token 1 kun, refresh token 7 kun.

## Topshiriqlar va daraja tizimi

### Topshiriq shabloni (`TaskTemplate`)

Topshiriqlar admin panelda **Task templates** bo'limida yaratiladi yoki **Import** tugmasi
orqali ommaviy yuklanadi (kategoriyalarni oldindan **Task categories** bo'limida yarating).
`target_structure` maydoni foydalanuvchi oxirida hosil qilishi kerak bo'lgan strukturani tavsiflaydi:

```json
{
  "project": {
    "readme.txt": "Bu loyiha haqida",
    "src": {},
    "main.py": null
  }
}
```

- `"nom": "matn"` degani: shu nomli fayl bo'lishi va ichidagi matn aynan shunday bo'lishi kerak;
- `"nom": null` degani: fayl mavjud bo'lishi yetarli, ichi tekshirilmaydi;
- `"nom": {}` degani: bo'sh papka;
- `"nom": {...}` degani: ichma-ich papka.

Namunalar: `src/apps/utils/test.json`.

### XP va daraja

- To'g'ri bajarilsa, topshiriqning `xp` qiymati profilga qo'shiladi, streak +1.
- Ketma-ket **5** ta muvaffaqiyatdan keyin daraja +1 bo'ladi (maksimum 10) va streak nolga tushadi.
- Xato bo'lsa, topshiriq `failed` bo'ladi, streak nolga tushadi. Tuzatib, `check` ni qayta yozish mumkin.
- Bir topshiriq uchun XP faqat bir marta beriladi (takroriy `check` XP'ni ko'paytirmaydi).

## Loyiha tuzilmasi

```text
termina/
├── docker-compose.yml        # db, redis, web, celery
├── Dockerfile
├── requirements.txt
└── src/
    ├── manage.py
    ├── .env.example
    ├── config/               # settings, urls, celery, wsgi
    ├── api/                  # views, serializers, urls (REST qatlam)
    ├── apps/
    │   ├── task/             # Profile, TaskTemplate, Task, tekshiruv va XP logikasi
    │   ├── terminal/         # Workspace modeli va signal
    │   ├── users/
    │   └── utils/
    │       ├── funksion.py   # TerminalEngine: buyruqlarni bajarish
    │       └── tasks.py      # Celery: async_check_task
    └── templates/
        └── terminal_help.html
```

## Testlar

```bash
docker compose exec web python manage.py test apps.task.tests
```

Testlar quyidagilarni qamrab oladi: begona foydalanuvchi boshqa birovning topshiriq holatini
ko'ra olmasligi, `../` orqali workspace'dan chiqib bo'lmasligi, `check` aynan boshlangan
topshiriqni bir marta yuborishi, XP'ning ikki marta berilmasligi.

## Lokal ishlab chiqish (Docker'siz)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

`src/.env` da `DB_HOST=127.0.0.1` va `REDIS_HOST=127.0.0.1` qiling (yoki
`DB_ENGINE=django.db.backends.sqlite3`, `DB_NAME=db.sqlite3` bilan SQLite ishlating), so'ng:

```bash
cd src
python manage.py migrate
python manage.py runserver
celery -A config worker --loglevel=info    # alohida terminalda, Redis ishlab turishi kerak
```

Docker'dagi va lokal jarayonlarni aralashtirmang: ular turli Redis'ga ulanishi mumkin.

## Serverga joylash

- `.env` da `DEBUG=False`, haqiqiy `ALLOWED_HOSTS`, `CORS_ALLOWED_ORIGINS` va `CSRF_TRUSTED_ORIGINS`
  (`https://` bilan) yozing, yangi `SECRET_KEY` va parollarni ishlating.
- Gunicorn oldiga Nginx qo'yib, HTTPS sertifikatini (Let's Encrypt) ulang, so'ng
  `SECURE_SSL_REDIRECT=True` qiling.
- Postgres va Redis portlarini tashqariga ochmang (compose'da ular ochilmagan).
- `postgres_data` volume'ini va `src/workspaces/` papkasini muntazam zaxiralang.
- `web` va `celery` konteynerlari `src/workspaces/` ni bir xil papka sifatida ko'rishi kerak
  (compose'dagi `./src:/app` mount'i shuni ta'minlaydi).

## Muammolarni hal qilish

| Belgi | Sababi va yechimi |
|---|---|
| `web` konteyneri `Restarting` | `docker compose logs web` ni oching, xato matni shu yerda |
| `password authentication failed` | Baza eski parol bilan yaratilgan: `docker compose down -v` |
| `address already in use` (6379) | Lokal Redis portni band qilgan. Compose Redis'ni hostga ochmaydi, `ports:` qo'shmang |
| Status doim `PENDING` | Celery ishlamayapti yoki boshqa Redis'ga ulangan: `docker compose logs celery` |
| Admin sahifasi CSS'siz | Static fayllar yig'ilmagan yoki `whitenoise` o'rnatilmagan |
| `Set the ... environment variable` | `src/.env` da o'zgaruvchi yetishmayapti, `.env.example` bilan solishtiring |

## Muallif

Oydinov Ilyos · [github.com/oydinov012](https://github.com/oydinov012)
