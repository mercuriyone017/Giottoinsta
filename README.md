# YouTube loyiha: restoran tizimi kontenti

Restoran tizimi bo'yicha kontent loyihasi: YouTube video rejasi, ssenariylar va Instagram'dan yig'ilgan g'oyalar bazasi.

## Papkalar
- `loyihalar/` — video rejalari va ssenariylar
- `goyalar/` — Instagram g'oyalari tahlili (`goyalar/README.md` jadvalida ro'yxati)
- `scripts/insta_tahlil.py` — Instagram post/reel'ni yuklab, kadrlar va nutq matnini oladi
- `.claude/` — Claude uchun skill va hook: Instagram link yuborilganda tahlil avtomatik boshlanadi

## Instagram linkdan avtomatik tahlil: sozlash

### 1. Tarmoqqa ruxsat
Cloud environment sozlamalarida (sessiya sarlavhasidagi environment menyusi → Edit → Network access)
**Allowed domains** ro'yxatiga qo'shing, "Allow package managers" belgisini qoldiring:

```
instagram.com
*.instagram.com
*.cdninstagram.com
*.fbcdn.net
huggingface.co
*.huggingface.co
*.hf.co
```

Instagram domenlari postni yuklab olish uchun, huggingface esa nutqni matnga o'giruvchi
(Whisper) modelni yuklash uchun kerak. Batafsil: https://code.claude.com/docs/en/cloud-environments#network-access

### 2. Shu repo bilan sessiya ochish
Yangi sessiyani shu repo tanlangan holda oching. Shunda `CLAUDE.md`, skill va hook avtomatik yuklanadi,
g'oyalar esa repoga saqlanib boradi.

### 3. (Faqat kerak bo'lsa) Instagram cookies
Instagram ba'zan kirishni (login) talab qiladi. Shunda:
1. **Asosiy emas, qo'shimcha** Instagram akkauntga brauzerda kiring.
2. "Get cookies.txt LOCALLY" kengaytmasi bilan instagram.com uchun cookies.txt ni eksport qiling.
3. Uning mazmunini environment sozlamalarida `INSTAGRAM_COOKIES` nomli o'zgaruvchiga qo'ying.

Cookies'ni chatga yozmang.

## Ishlatish
Chatga Instagram linkni tashlang. Xohlasangiz yoniga izoh yozing:
- `https://www.instagram.com/reel/...` — to'liq tahlil
- `https://www.instagram.com/reel/... hook uchun` — faqat hook'ka e'tibor
- `https://www.instagram.com/reel/... montaj uslubi` — montaj va formatga e'tibor
- bir nechta link birga — har biri tahlil qilinadi va solishtiriladi

Instagram ochilmasa, videoni telefonga saqlab chatga fayl qilib yuklang. Xuddi shu tahlil qilinadi.
