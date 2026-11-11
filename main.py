import os
import json
import requests
import telebot
from telebot import types
from datetime import datetime

# ============ الإعدادات ============
BOT_TOKEN = "9045949602:AAHAtAVXtnbMubs9m3x9wCcbtxMIk4lITr4"
OWNER_ID = 8593727596              # آيدي المالك
VODAFONE_NUMBER = "01041974269"   # رقم فودافون كاش
STAR_PRICE = 25                   # سعر النجمة بالجنيه
DEVELOPER = "asmael175"           # يوزر المطور
API_URL = "https://ghostsnet.xyz/sc/"
DATA_FILE = "data.json"

bot = telebot.TeleBot(BOT_TOKEN)

# ============ قاعدة البيانات ============
def load_db():
    if not os.path.exists(DATA_FILE):
        return {"users": {}, "banned": [], "stats": {"activations": 0},
                "pending": {}, "next_req_id": 1}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

db = load_db()

# ============ الثوابت ============
STAR = "⭐"; BRIGHT = "🔆"; FIRE = "🔥"; DIAMOND = "💎"
CROWN = "👑"; CHECK = "✅"; CROSS = "❌"; GHOST = "👻"
MONEY = "💰"; SCREEN = "🖼"; WAIT = "⏳"

# ============ API ============
def get_packages():
    try:
        r = requests.get(API_URL, timeout=10)
        data = r.json()
        if data.get('status') == 'success':
            return data.get('packages', [])
    except:
        pass
    return []

def activate_package(number, password, package_id):
    payload = {"number": number, "password": password, "package": package_id}
    try:
        r = requests.post(API_URL, json=payload, timeout=30)
        return r.json()
    except requests.exceptions.Timeout:
        return {"status": "error", "message": "⏰ انتهت مهلة الاتصال"}
    except Exception as e:
        return {"status": "error", "message": f"❌ خطأ: {str(e)[:50]}"}

# ============ أدوات ============
def is_owner(uid): return uid == OWNER_ID
def is_banned(uid): return str(uid) in db["banned"]

def ensure_user(uid, name):
    if str(uid) not in db["users"]:
        db["users"][str(uid)] = {
            "name": name, "stars": 0,
            "joined": datetime.now().isoformat(),
            "activations": 0
        }
        save_db(db)

def get_stars(uid): return db["users"].get(str(uid), {}).get("stars", 0)

# ============ لوحات المفاتيح ============
def main_menu(uid):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(f"{STAR} تحويل نظام {STAR}", callback_data="convert"),
        types.InlineKeyboardButton(f"{DIAMOND} رصيدي", callback_data="balance"),
    )
    kb.add(
        types.InlineKeyboardButton(f"{MONEY} شراء نجوم {STAR}", callback_data="buy_stars"),
        types.InlineKeyboardButton(f"{GHOST} حول البوت", callback_data="about"),
    )
    kb.add(
        types.InlineKeyboardButton(f"👨‍💻 تواصل مع المطور", url=f"https://t.me/{DEVELOPER}"),
    )
    if is_owner(uid):
        kb.add(types.InlineKeyboardButton(f"{CROWN} لوحة التحكم {CROWN}", callback_data="admin_panel"))
    return kb

def reply_menu(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(f"{STAR} تحويل نظام"),
        types.KeyboardButton(f"{DIAMOND} رصيدي"),
    )
    kb.add(
        types.KeyboardButton(f"{MONEY} شراء نجوم"),
        types.KeyboardButton(f"{GHOST} حول البوت"),
    )
    kb.add(types.KeyboardButton(f"👨‍💻 تواصل مع المطور"))
    if is_owner(uid):
        kb.add(types.KeyboardButton(f"{CROWN} لوحة التحكم"))
    return kb

def packages_menu(packages):
    kb = types.InlineKeyboardMarkup(row_width=1)
    for p in packages:
        kb.add(types.InlineKeyboardButton(
            f"{BRIGHT} {p['name']}",
            callback_data=f"pkg_{p['id']}_{p['name']}"
        ))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

def buy_stars_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    for n in [1, 2, 5, 10, 25, 50]:
        kb.add(types.InlineKeyboardButton(
            f"{n} {STAR} = {n*STAR_PRICE}ج",
            callback_data=f"buystars_{n}"
        ))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    return kb

# ============ /start ============
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.from_user.id
    ensure_user(uid, msg.from_user.first_name)
    if is_banned(uid):
        bot.send_message(uid, f"{CROSS} أنت محظور من استخدام البوت.")
        return
    text = (
        f"{GHOST} <b>مرحباً {msg.from_user.first_name}!</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{BRIGHT} بوت تحويل الأنظمة القديمة\n"
        f"{STAR} سعر النجمة: <b>{STAR_PRICE} جنيه</b>\n"
        f"{DIAMOND} رصيدك: <b>{get_stars(uid)} {STAR}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"اختر من القائمة 👇"
    )
    bot.send_message(uid, text, reply_markup=reply_menu(uid), parse_mode="HTML")
    bot.send_message(uid, f"{BRIGHT} القائمة الرئيسية:", reply_markup=main_menu(uid))

# ============ أمر المطور ============
@bot.message_handler(commands=['developer', 'dev'])
def cmd_dev(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=f"https://t.me/{DEVELOPER}"))
    bot.send_message(
        msg.chat.id,
        f"👨‍💻 <b>المطور</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 يوزر: @{DEVELOPER}\n"
        f"📩 للاستفسارات والدعم الفني\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"اضغط الزر للتواصل مباشرة 👇",
        reply_markup=kb, parse_mode="HTML")

# ============ تحويل النظام ============
@bot.callback_query_handler(func=lambda c: c.data == "convert")
def cb_convert(call):
    if is_banned(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 محظور", show_alert=True); return
    stars = get_stars(call.from_user.id)
    COST = 1
    if stars < COST:
        bot.answer_callback_query(
            call.id,
            f"❌ تحتاج {COST} {STAR} للتحويل!\n"
            f"رصيدك: {stars} {STAR}\n"
            f"سعر النجمة: {STAR_PRICE} جنيه\n"
            f"اشترِ نجوم الآن من زر {MONEY} شراء نجوم.",
            show_alert=True)
        return
    packages = get_packages()
    if not packages:
        bot.answer_callback_query(call.id, "❌ فشل تحميل الباقات", show_alert=True); return
    text = (
        f"{BRIGHT} <b>اختر الباقة</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 تكلفة التحويل: <b>{COST} {STAR}</b>\n"
        f"رصيدك: <b>{stars} {STAR}</b>"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=packages_menu(packages), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("pkg_"))
def cb_pkg(call):
    uid = call.from_user.id
    _, pkg_id, pkg_name = call.data.split("_", 2)
    db["users"][str(uid)]["temp_pkg"] = {"id": int(pkg_id), "name": pkg_name}
    save_db(db)
    msg = bot.send_message(
        uid,
        f"{FIRE} الباقة: <b>{pkg_name}</b>\n\n"
        f"📱 <b>أدخل رقم الموبايل:</b>\n"
        f"مثال: <code>01234567890</code>",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔙 إلغاء", callback_data="back_main")))
    bot.register_next_step_handler(msg, receive_phone)

def receive_phone(msg):
    uid = msg.from_user.id
    user = db["users"].get(str(uid), {})
    pkg = user.get("temp_pkg")
    if not pkg:
        bot.send_message(uid, f"{CROSS} لم يتم اختيار باقة.")
        return

    phone = msg.text.strip() if msg.text else ""
    if not phone.isdigit() or len(phone) < 10:
        m = bot.send_message(uid, f"{CROSS} رقم غير صالح! أدخل رقم صحيح:\nمثال: <code>01234567890</code>",
                             parse_mode="HTML")
        bot.register_next_step_handler(m, receive_phone)
        return

    db["users"][str(uid)]["temp_phone"] = phone
    save_db(db)

    m = bot.send_message(
        uid,
        f"{CHECK} تم حفظ الرقم: <code>{phone}</code>\n\n"
        f"🔐 <b>أدخل باسورد فودافون:</b>",
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔙 إلغاء", callback_data="back_main")))
    bot.register_next_step_handler(m, receive_password)

def receive_password(msg):
    uid = msg.from_user.id
    user = db["users"].get(str(uid), {})
    pkg = user.get("temp_pkg")
    phone = user.get("temp_phone")

    if not pkg or not phone:
        bot.send_message(uid, f"{CROSS} حدث خطأ. ابدأ من جديد /start")
        return

    password = msg.text.strip() if msg.text else ""
    if not password:
        m = bot.send_message(uid, f"{CROSS} الباسورد لا يمكن أن يكون فارغاً! أرسل الباسورد:")
        bot.register_next_step_handler(m, receive_password)
        return

    db["users"][str(uid)].pop("temp_phone", None)
    db["users"][str(uid)].pop("temp_pkg", None)
    save_db(db)

    do_activation(msg, phone, password, pkg)

def do_activation(msg, number, password, pkg):
    uid = msg.from_user.id
    COST = 1
    if get_stars(uid) < COST:
        bot.send_message(uid, f"{CROSS} رصيدك غير كافٍ!"); return
    wait = bot.send_message(uid, f"{BRIGHT} جاري التحويل... انتظر")
    result = activate_package(number, password, pkg['id'])
    if result.get('status') == 'success':
        db["users"][str(uid)]["stars"] -= COST
        db["users"][str(uid)]["activations"] += 1
        db["stats"]["activations"] += 1
        save_db(db)
        bot.edit_message_text(
            f"{CHECK} <b>تم التحويل بنجاح!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 الباقة: {pkg['name']}\n"
            f"📱 الرقم: <code>{number}</code>\n"
            f"{STAR} الرصيد المتبقي: {get_stars(uid)}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 {result.get('message','')}",
            uid, wait.message_id, parse_mode="HTML")
    else:
        bot.edit_message_text(
            f"{CROSS} <b>فشل التحويل</b>\n\n💬 {result.get('message','خطأ')}",
            uid, wait.message_id, parse_mode="HTML")

# ============ شراء النجوم ============
@bot.callback_query_handler(func=lambda c: c.data == "buy_stars")
def cb_buy(call):
    text = (
        f"{MONEY} <b>شراء نجوم</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{STAR} سعر النجمة: <b>{STAR_PRICE} جنيه</b>\n"
        f"{DIAMOND} رصيدك الحالي: <b>{get_stars(call.from_user.id)} {STAR}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"اختر عدد النجوم اللي عايز تشتريها:"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=buy_stars_menu(), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("buystars_"))
def cb_buystars(call):
    n = int(call.data.split("_")[1])
    total = n * STAR_PRICE
    uid = call.from_user.id
    db["users"][str(uid)]["temp_buy"] = n
    save_db(db)

    text = (
        f"{MONEY} <b>طلب شراء {n} {STAR}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{STAR} النجوم: <b>{n}</b>\n"
        f"{MONEY} المبلغ المطلوب: <b>{total} جنيه</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💳 <b>حوّل المبلغ على فودافون كاش:</b>\n"
        f"<code>{VODAFONE_NUMBER}</code>\n\n"
        f"📸 بعد التحويل، ابعت <b>صورة سكرين شوت</b> للتحويل هنا.\n"
        f"⏳ سيتم مراجعة طلبك من الإدارة."
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          parse_mode="HTML")
    msg = bot.send_message(uid, f"{SCREEN} ابعت صورة السكرين شوت الآن:")
    bot.register_next_step_handler(msg, receive_screenshot, n)

def receive_screenshot(msg, n):
    uid = msg.from_user.id
    if not msg.photo:
        bot.send_message(uid, f"{CROSS} لازم تبعت صورة سكرين شوت!")
        return
    total = n * STAR_PRICE
    req_id = db["next_req_id"]
    db["next_req_id"] += 1

    db["pending"][str(req_id)] = {
        "user_id": uid,
        "name": msg.from_user.first_name,
        "username": msg.from_user.username or "—",
        "stars": n,
        "amount": total,
        "screenshot": msg.photo[-1].file_id,
        "date": datetime.now().isoformat()
    }
    save_db(db)

    bot.send_message(
        uid,
        f"{CHECK} <b>تم إرسال طلبك للإدارة</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 رقم الطلب: <code>#{req_id}</code>\n"
        f"{STAR} النجوم: {n}\n"
        f"{MONEY} المبلغ: {total} جنيه\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{WAIT} سيتم المراجعة وإعلامك بالنتيجة.",
        parse_mode="HTML")

    owner_text = (
        f"{FIRE} <b>طلب شراء جديد</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 الطلب: <code>#{req_id}</code>\n"
        f"👤 المستخدم: {msg.from_user.first_name}\n"
        f"🔗 يوزر: @{msg.from_user.username or '—'}\n"
        f"🆔 آيدي: <code>{uid}</code>\n"
        f"{STAR} النجوم: <b>{n}</b>\n"
        f"{MONEY} المبلغ: <b>{total} جنيه</b>\n"
        f"🕐 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(f"{CHECK} موافقة (+{n} {STAR})",
                                   callback_data=f"approve_{req_id}"),
        types.InlineKeyboardButton(f"{CROSS} رفض + حظر",
                                   callback_data=f"reject_{req_id}")
    )
    try:
        bot.send_photo(OWNER_ID, msg.photo[-1].file_id,
                       caption=owner_text, reply_markup=kb, parse_mode="HTML")
    except: pass

# ============ موافقة / رفض المالك ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("approve_"))
def cb_approve(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 للمالك فقط", show_alert=True); return
    req_id = call.data.split("_")[1]
    req = db["pending"].get(req_id)
    if not req:
        bot.answer_callback_query(call.id, "❌ الطلب غير موجود", show_alert=True); return

    uid = req["user_id"]; n = req["stars"]
    if str(uid) not in db["users"]:
        db["users"][str(uid)] = {"name": req["name"], "stars": 0,
                                  "joined": datetime.now().isoformat(),
                                  "activations": 0}
    db["users"][str(uid)]["stars"] = db["users"][str(uid)].get("stars", 0) + n
    del db["pending"][req_id]
    save_db(db)

    bot.edit_message_caption(
        f"{CHECK} <b>تمت الموافقة</b>\nطلب #{req_id} — أضيف {n} {STAR}",
        call.message.chat.id, call.message.message_id, parse_mode="HTML")
    try:
        bot.send_message(uid,
            f"{CHECK} <b>تمت الموافقة على طلبك!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 الطلب: #{req_id}\n"
            f"{STAR} تمت إضافة: <b>{n} نجمة</b>\n"
            f"{DIAMOND} رصيدك الآن: <b>{get_stars(uid)} {STAR}</b>",
            parse_mode="HTML", reply_markup=reply_menu(uid))
    except: pass

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def cb_reject(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 للمالك فقط", show_alert=True); return
    req_id = call.data.split("_")[1]
    req = db["pending"].get(req_id)
    if not req:
        bot.answer_callback_query(call.id, "❌ الطلب غير موجود", show_alert=True); return
    uid = req["user_id"]
    if str(uid) not in db["banned"]:
        db["banned"].append(str(uid))
    del db["pending"][req_id]
    save_db(db)

    bot.edit_message_caption(
        f"{CROSS} <b>تم الرفض والحظر</b>\nطلب #{req_id}",
        call.message.chat.id, call.message.message_id, parse_mode="HTML")
    try:
        bot.send_message(uid,
            f"{CROSS} <b>تم رفض طلبك وحظرك</b>\n"
            f"🆔 الطلب: #{req_id}\n"
            f"للاستفسار تواصل مع الإدارة: @{DEVELOPER}")
    except: pass

# ============ الرصيد ============
@bot.callback_query_handler(func=lambda c: c.data == "balance")
def cb_balance(call):
    uid = call.from_user.id
    u = db["users"].get(str(uid), {})
    text = (
        f"{DIAMOND} <b>رصيدك</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{STAR} النجوم: <b>{u.get('stars',0)}</b>\n"
        f"{FIRE} التحويلات: <b>{u.get('activations',0)}</b>\n"
        f"📅 انضم: {u.get('joined','')[:10]}"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=types.InlineKeyboardMarkup().add(
                              types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main")),
                          parse_mode="HTML")

# ============ حول البوت ============
@bot.callback_query_handler(func=lambda c: c.data == "about")
def cb_about(call):
    text = (
        f"{GHOST} <b>Ghosts Net Bot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔆 تحويل الأنظمة القديمة\n"
        f"{STAR} سعر النجمة: {STAR_PRICE} جنيه\n"
        f"{MONEY} دفع يدوي فودافون كاش\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 المطور: @{DEVELOPER}"
    )
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=f"https://t.me/{DEVELOPER}"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=kb, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "back_main")
def cb_back(call):
    uid = call.from_user.id
    text = (f"{GHOST} <b>القائمة الرئيسية</b>\n"
            f"{DIAMOND} رصيدك: <b>{get_stars(uid)} {STAR}</b>")
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=main_menu(uid), parse_mode="HTML")

# ============ لوحة المالك ============
@bot.callback_query_handler(func=lambda c: c.data == "admin_panel")
def cb_admin(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 للمالك فقط", show_alert=True); return
    pending_count = len(db["pending"])
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(f"⏳ الطلبات ({pending_count})", callback_data="adm_pending"),
        types.InlineKeyboardButton(f"📊 إحصائيات", callback_data="adm_stats"),
    )
    kb.add(
        types.InlineKeyboardButton(f"👥 المستخدمين", callback_data="adm_users"),
        types.InlineKeyboardButton(f"{STAR} إضافة نجوم", callback_data="adm_addstars"),
    )
    kb.add(
        types.InlineKeyboardButton(f"🚫 حظر", callback_data="adm_ban"),
        types.InlineKeyboardButton(f"✅ رفع الحظر", callback_data="adm_unban"),
    )
    kb.add(types.InlineKeyboardButton(f"📢 إذاعة", callback_data="adm_broadcast"))
    kb.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="back_main"))
    bot.edit_message_text(
        f"{CROWN} <b>لوحة تحكم المالك</b>\n"
        f"⏳ طلبات معلقة: <b>{pending_count}</b>",
        call.message.chat.id, call.message.message_id,
        reply_markup=kb, parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "adm_pending")
def adm_pending(call):
    if not is_owner(call.from_user.id): return
    if not db["pending"]:
        bot.answer_callback_query(call.id, "لا توجد طلبات معلقة ✅", show_alert=True); return
    bot.edit_message_text(
        f"⏳ <b>الطلبات المعلقة: {len(db['pending'])}</b>\n"
        f"سيتم إرسال كل طلب بشكل منفصل أدناه 👇",
        call.message.chat.id, call.message.message_id,
        reply_markup=types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")),
        parse_mode="HTML")

    for rid, req in db["pending"].items():
        text = (
            f"{FIRE} <b>طلب #{rid}</b>\n"
            f"👤 {req['name']} | @{req['username']}\n"
            f"🆔 <code>{req['user_id']}</code>\n"
            f"{STAR} {req['stars']} نجمة | {MONEY} {req['amount']}ج\n"
            f"🕐 {req['date'][:16]}"
        )
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton(f"{CHECK} موافقة", callback_data=f"approve_{rid}"),
            types.InlineKeyboardButton(f"{CROSS} رفض + حظر", callback_data=f"reject_{rid}")
        )
        try:
            bot.send_photo(OWNER_ID, req["screenshot"], caption=text,
                           reply_markup=kb, parse_mode="HTML")
        except: pass

@bot.callback_query_handler(func=lambda c: c.data == "adm_stats")
def adm_stats(call):
    if not is_owner(call.from_user.id): return
    text = (
        f"📊 <b>الإحصائيات</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👥 المستخدمين: {len(db['users'])}\n"
        f"{FIRE} التحويلات: {db['stats']['activations']}\n"
        f"⏳ طلبات معلقة: {len(db['pending'])}\n"
        f"🚫 المحظورين: {len(db['banned'])}\n"
        f"{STAR} مجموع النجوم: {sum(u.get('stars',0) for u in db['users'].values())}"
    )
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                          reply_markup=types.InlineKeyboardMarkup().add(
                              types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")),
                          parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "adm_users")
def adm_users(call):
    if not is_owner(call.from_user.id): return
    lines = [f"👥 <b>المستخدمين ({len(db['users'])})</b>\n"]
    for i, (uid, u) in enumerate(list(db['users'].items())[:30], 1):
        lines.append(f"{i}. {u['name']} | <code>{uid}</code> | {STAR}{u.get('stars',0)}")
    bot.edit_message_text("\n".join(lines), call.message.chat.id, call.message.message_id,
                          reply_markup=types.InlineKeyboardMarkup().add(
                              types.InlineKeyboardButton("🔙 رجوع", callback_data="admin_panel")),
                          parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data == "adm_addstars")
def adm_addstars(call):
    if not is_owner(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "أرسل: <code>الآيدي عدد_النجوم</code>", parse_mode="HTML")
    bot.register_next_step_handler(msg, _do_addstars)

def _do_addstars(msg):
    if msg.from_user.id != OWNER_ID: return
    try:
        uid, n = msg.text.split(); n = int(n)
        if str(uid) not in db["users"]:
            db["users"][str(uid)] = {"name": "?", "stars": 0, "joined": "", "activations": 0}
        db["users"][str(uid)]["stars"] = db["users"][str(uid)].get("stars", 0) + n
        save_db(db)
        bot.send_message(msg.chat.id, f"{CHECK} أضيف {n} {STAR} للمستخدم {uid}")
        try: bot.send_message(int(uid), f"{STAR} تم إضافة {n} نجمة! رصيدك: {get_stars(uid)}")
        except: pass
    except:
        bot.send_message(msg.chat.id, f"{CROSS} صيغة خاطئة")

@bot.callback_query_handler(func=lambda c: c.data == "adm_ban")
def adm_ban(call):
    if not is_owner(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "أرسل آيدي المستخدم للحظر:")
    bot.register_next_step_handler(msg, lambda m: _do_ban(m, True))

@bot.callback_query_handler(func=lambda c: c.data == "adm_unban")
def adm_unban(call):
    if not is_owner(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "أرسل آيدي المستخدم لرفع الحظر:")
    bot.register_next_step_handler(msg, lambda m: _do_ban(m, False))

def _do_ban(msg, ban):
    if msg.from_user.id != OWNER_ID: return
    uid = msg.text.strip()
    if ban:
        if uid not in db["banned"]: db["banned"].append(uid)
        txt = f"{CROSS} تم حظر {uid}"
    else:
        if uid in db["banned"]: db["banned"].remove(uid)
        txt = f"{CHECK} تم رفع الحظر عن {uid}"
    save_db(db)
    bot.send_message(msg.chat.id, txt)

@bot.callback_query_handler(func=lambda c: c.data == "adm_broadcast")
def adm_broadcast(call):
    if not is_owner(call.from_user.id): return
    msg = bot.send_message(call.message.chat.id, "أرسل رسالة الإذاعة:")
    bot.register_next_step_handler(msg, _do_broadcast)

def _do_broadcast(msg):
    if msg.from_user.id != OWNER_ID: return
    ok = fail = 0
    for uid in db["users"].keys():
        try:
            bot.send_message(int(uid), f"📢 <b>إعلان</b>\n\n{msg.text}", parse_mode="HTML")
            ok += 1
        except: fail += 1
    bot.send_message(msg.chat.id, f"{CHECK} نجح: {ok} | {CROSS} فشل: {fail}")

# ============ معالجات الأزرار الثابتة (Reply) ============
@bot.message_handler(func=lambda m: m.text == f"{STAR} تحويل نظام")
def btn_convert(msg):
    uid = msg.from_user.id
    if is_banned(uid):
        bot.send_message(uid, f"{CROSS} أنت محظور."); return
    stars = get_stars(uid)
    COST = 1
    if stars < COST:
        bot.send_message(uid,
            f"❌ تحتاج {COST} {STAR} للتحويل!\n"
            f"رصيدك: {stars} {STAR}\n"
            f"سعر النجمة: {STAR_PRICE} جنيه\n"
            f"اشترِ نجوم الآن 👇",
            reply_markup=reply_menu(uid))
        return
    packages = get_packages()
    if not packages:
        bot.send_message(uid, "❌ فشل تحميل الباقات"); return
    text = (
        f"{BRIGHT} <b>اختر الباقة</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 تكلفة التحويل: <b>{COST} {STAR}</b>\n"
        f"رصيدك: <b>{stars} {STAR}</b>"
    )
    bot.send_message(uid, text, reply_markup=packages_menu(packages), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == f"{DIAMOND} رصيدي")
def btn_balance(msg):
    uid = msg.from_user.id
    u = db["users"].get(str(uid), {})
    text = (
        f"{DIAMOND} <b>رصيدك</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{STAR} النجوم: <b>{u.get('stars',0)}</b>\n"
        f"{FIRE} التحويلات: <b>{u.get('activations',0)}</b>\n"
        f"📅 انضم: {u.get('joined','')[:10]}"
    )
    bot.send_message(uid, text, parse_mode="HTML", reply_markup=reply_menu(uid))

@bot.message_handler(func=lambda m: m.text == f"{MONEY} شراء نجوم")
def btn_buy(msg):
    uid = msg.from_user.id
    text = (
        f"{MONEY} <b>شراء نجوم</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{STAR} سعر النجمة: <b>{STAR_PRICE} جنيه</b>\n"
        f"{DIAMOND} رصيدك الحالي: <b>{get_stars(uid)} {STAR}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"اختر عدد النجوم:"
    )
    bot.send_message(uid, text, reply_markup=buy_stars_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == f"{GHOST} حول البوت")
def btn_about(msg):
    text = (
        f"{GHOST} <b>Ghosts Net Bot</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔆 تحويل الأنظمة القديمة\n"
        f"{STAR} سعر النجمة: {STAR_PRICE} جنيه\n"
        f"{MONEY} دفع يدوي فودافون كاش\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👨‍💻 المطور: @{DEVELOPER}"
    )
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=f"https://t.me/{DEVELOPER}"))
    bot.send_message(msg.chat.id, text, reply_markup=kb, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == "👨‍💻 تواصل مع المطور")
def btn_dev(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("👨‍💻 اضغط للتواصل", url=f"https://t.me/{DEVELOPER}"))
    bot.send_message(
        msg.chat.id,
        f"👨‍💻 <b>المطور</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔗 يوزر: @{DEVELOPER}\n"
        f"📩 للاستفسارات والدعم\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"اضغط الزر للتواصل 👇",
        reply_markup=kb, parse_mode="HTML")

@bot.message_handler(func=lambda m: m.text == f"{CROWN} لوحة التحكم")
def btn_admin(msg):
    if not is_owner(msg.from_user.id):
        bot.send_message(msg.chat.id, f"{CROSS} للمالك فقط"); return
    pending_count = len(db["pending"])
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(f"⏳ الطلبات ({pending_count})", callback_data="adm_pending"),
        types.InlineKeyboardButton(f"📊 إحصائيات", callback_data="adm_stats"),
    )
    kb.add(
        types.InlineKeyboardButton(f"👥 المستخدمين", callback_data="adm_users"),
        types.InlineKeyboardButton(f"{STAR} إضافة نجوم", callback_data="adm_addstars"),
    )
    kb.add(
        types.InlineKeyboardButton(f"🚫 حظر", callback_data="adm_ban"),
        types.InlineKeyboardButton(f"✅ رفع الحظر", callback_data="adm_unban"),
    )
    kb.add(types.InlineKeyboardButton(f"📢 إذاعة", callback_data="adm_broadcast"))
    bot.send_message(
        msg.chat.id,
        f"{CROWN} <b>لوحة تحكم المالك</b>\n"
        f"⏳ طلبات معلقة: <b>{pending_count}</b>",
        reply_markup=kb, parse_mode="HTML")

# ============ تشغيل ============
if __name__ == "__main__":
    print(f"{GHOST} Bot running...")
    bot.infinity_polling(timeout=60)
