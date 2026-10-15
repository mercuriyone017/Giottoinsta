---
name: instagram-tahlil
description: Instagram post yoki reel linkini ochib, ichidagi g'oyani tahlil qiladi va bizning restoran tizimi kontentimizga moslab g'oyalar bazasiga saqlaydi. Foydalanuvchi instagram.com linkini yuborganda (izohli yoki izohsiz), yoki telefondan Instagram videosini yuklaganda ishlat.
---

# Instagram g'oya tahlili

Foydalanuvchi Instagram'da ko'rgan g'oyalarni yuboradi. Maqsad: g'oya yo'qolib ketmasin, undan
bizning kontentimiz uchun aniq foyda chiqsin. Loyiha konteksti `CLAUDE.md` da.

## 1. Yuklab olish

Har bir link uchun:

```bash
python3 scripts/insta_tahlil.py "<link>"
```

Foydalanuvchi videoni fayl qilib yuklagan bo'lsa: `python3 scripts/insta_tahlil.py --fayl <yo'l>`.

Natija `goyalar/_xom/<id>/` papkasida: `meta.json`, `caption.txt`, `transkript.txt`,
`kadrlar_jadval.jpg`, `kadrlar/` (karuselda `rasmlar/`).

**Xato bo'lsa** (skript `"xato"` qaytaradi), sababini aniqlab, foydalanuvchiga qisqa ayt:
- `403`, `Tunnel`, `ENOTFOUND`: muhit tarmog'ida Instagram ruxsat etilmagan. `README.md` dagi 1-qadam.
- `login required`, `rate-limit`, `empty media response`: Instagram kirishni talab qilyapti.
  `INSTAGRAM_COOKIES` sirini qo'shish kerak (`README.md`, 3-qadam).
- `Private`: yopiq akkaunt, ko'rib bo'lmaydi.

Shunda foydalanuvchidan videoni telefonga saqlab, chatga fayl qilib yuklashni yoki skrinshot
yuborishni so'ra. Hech qachon postni ko'rmasdan taxminiy tahlil yozma.

## 2. Ko'rib chiqish

1. `meta.json` va `caption.txt` ni o'qi.
2. `transkript.txt` ni o'qi. Transkript olinmagan bo'lsa, buni tahlilda ayt.
3. `kadrlar_jadval.jpg` ni Read bilan ko'r. Hook uchun `kadrlar/` dagi birinchi 3 soniya kadrlarini
   alohida ko'r: ekrandagi matn, kim kadrda, qanday ko'rinish.
4. Karusel bo'lsa, `rasmlar/` dagi har bir rasmni ko'r.

## 3. Foydalanuvchi nima xohlayotganini aniqlash

- Link yonida izoh bo'lsa (masalan "hook uchun", "montaj uslubi", "shuni restoranga moslab ber"),
  asosiy e'tiborni o'shanga qarat, qolgan bo'limlarni qisqa qil.
- Izoh bo'lmasa, quyidagi to'liq shablonni ishlat.
- Bir nechta link birga kelsa, har birini tahlil qil, oxirida umumiy xulosa: ular nimasi bilan
  o'xshash va qaysi biri bizga eng foydali.

## 4. Tahlil shabloni (o'zbek tilida)

```markdown
# <qisqa nom>

**Link:** <url> · **Muallif:** @<username> · **Sana:** <sana>
**Ko'rsatkichlar:** <ko'rishlar> ko'rish · <like> like · <izoh> izoh · <davomiylik> s
**Foydaliligi:** ⭐⭐⭐⭐☆ (1–5) · **Teglar:** #hook #montaj #restoran ...

## Nima haqida
2–3 gapda mazmuni.

## Hook (birinchi 3 soniya)
Nima deyildi va nima ko'rsatildi. Nega tomoshabinni ushlab qoladi.

## Tuzilish
| Vaqt | Nima bo'ladi |
|---|---|

## Format va montaj
Kamera, kadrdagi odam, ekrandagi matn, musiqa, kesishlar tezligi, uzunlik.

## Nega ishlagan
Raqamlar va mazmundan kelib chiqib, 2–4 ta sabab.

## Bizga qanday moslash
- **Qayerda ishlatamiz:** YouTube video (qaysi blok/xato) yoki alohida Reels/Shorts.
- **Bizning variant:** restoran tizimi mavzusiga moslangan aniq g'oya.
- **Tayyor hook matni:** o'zbek tilida, kameraga aytiladigan 1–2 gap.
- **Suratga olish uchun:** nima kerak (joy, odamlar, ekran).
```

Umumiy maslahatlar emas, aynan shu postdan chiqqan aniq narsalarni yoz.

## 5. Saqlash

1. Tahlilni `goyalar/<YYYY-MM-DD>_<username>_<id>.md` ga yoz.
2. `goyalar/README.md` jadvaliga bir qator qo'sh (sana, nom, muallif, foydaliligi, teglar, fayl havolasi).
3. Git repo bo'lsa: `git add goyalar && git commit -m "G'oya: <qisqa nom>" && git push`.

## 6. Javob

Chatda qisqa javob ber: 3–5 qatorda asosiy topilma, "Bizga qanday moslash" bo'limi va saqlangan
fayl yo'li. To'liq tahlilni chatga takrorlama.
