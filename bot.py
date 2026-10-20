import os
import time
import random
import logging
import unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("BOT_TOKEN", "").strip()

# ---------- Supported UI languages ----------
LANGS = {
    "en": "🇬🇧 English",
    "km": "🇰🇭 ខ្មែរ",
    "zh": "🇨🇳 中文",
    "fr": "🇫🇷 Français",
    "ja": "🇯🇵 日本語",
    "es": "🇪🇸 Español",
}

# Per-user language preference (in-memory; resets on restart)
USER_LANG = {}

def get_lang(uid: int) -> str:
    return USER_LANG.get(uid, "en")

# ---------- Translated strings ----------
STRINGS = {
    "en": {
        "welcome": "👋 Welcome to *SB24GZ Khmer Bot*!\n\nI help you learn Khmer 🇰🇭",
        "choose": "Choose a feature:",
        "word": "📚 Word of the Day",
        "num_btn": "🔢 Numbers → Khmer",
        "phrase_btn": "💬 Random Phrase",
        "char_btn": "🔤 Khmer Character Info",
        "about_btn": "ℹ️ About",
        "lang_btn": "🌐 Change Language",
        "original": "Original",
        "rom": "Pronunciation",
        "meaning": "Meaning",
        "example": "Example",
        "usage_num": "Usage: /num 123",
        "char_info": "🔤 Send Khmer text and I'll show Unicode names.",
        "char_title": "🔤 Khmer Character Info:",
        "help": "📖 Commands:\n/word — Word of the day\n/num 123 — Arabic → Khmer numerals\n/phrase — Random phrase\n/lang — Change language\n/menu — Show menu",
        "about": "🤖 *SB24GZ Khmer Bot*\nKhmer learning assistant.\nMulti-language UI.\nDeployed on Railway 🚂",
        "pick_lang": "🌐 Pick your language:",
        "lang_set": "✅ Language set to English.",
        "phrase_title": "💬 Common Phrase",
    },
    "km": {
        "welcome": "👋 សូមស្វាគមន៍មកកាន់ *SB24GZ Khmer Bot*!\n\nខ្ញុំជួយអ្នករៀនភាសាខ្មែរ 🇰🇭",
        "choose": "ជ្រើសរើសមុខងារ៖",
        "word": "📚 ពាក្យប្រចាំថ្ងៃ",
        "num_btn": "🔢 លេខ → ខ្មែរ",
        "phrase_btn": "💬 ឃ្លាប្រចាំថ្ងៃ",
        "char_btn": "🔤 ព័ត៌មានតួអក្សរខ្មែរ",
        "about_btn": "ℹ️ អំពី",
        "lang_btn": "🌐 ប្តូរភាសា",
        "original": "ដើម",
        "rom": "ការបញ្ចេញសំឡេង",
        "meaning": "អត្ថន័យ",
        "example": "ឧទាហរណ៍",
        "usage_num": "ប្រើ៖ /num 123",
        "char_info": "🔤 ផ្ញើអក្សរខ្មែរ ខ្ញុំនឹងបង្ហាញឈ្មោះ Unicode។",
        "char_title": "🔤 ព័ត៌មានតួអក្សរខ្មែរ៖",
        "help": "📖 ពាក្យបញ្ជា៖\n/word — ពាក្យប្រចាំថ្ងៃ\n/num 123 — លេខអារ៉ាប់ → ខ្មែរ\n/phrase — ឃ្លាប្រចាំថ្ងៃ\n/lang — ប្តូរភាសា\n/menu — ម៉ឺនុយ",
        "about": "🤖 *SB24GZ Khmer Bot*\nជំនួយការរៀនភាសាខ្មែរ។\nគាំទ្រច្រើនភាសា។\nដាក់ពង្រាយនៅ Railway 🚂",
        "pick_lang": "🌐 ជ្រើសរើសភាសារបស់អ្នក៖",
        "lang_set": "✅ ភាសាត្រូវបានកំណត់ជាខ្មែរ។",
        "phrase_title": "💬 ឃ្លាប្រចាំថ្ងៃ",
    },
    "zh": {
        "welcome": "👋 欢迎使用 *SB24GZ Khmer Bot*！\n\n我帮助您学习高棉语 🇰🇭",
        "choose": "请选择功能：",
        "word": "📚 每日一词",
        "num_btn": "🔢 数字 → 高棉数字",
        "phrase_btn": "💬 随机短语",
        "char_btn": "🔤 高棉字符信息",
        "about_btn": "ℹ️ 关于",
        "lang_btn": "🌐 切换语言",
        "original": "原文",
        "rom": "发音",
        "meaning": "含义",
        "example": "例句",
        "usage_num": "用法：/num 123",
        "char_info": "🔤 发送高棉文，我会显示每个字符的 Unicode 名称。",
        "char_title": "🔤 高棉字符信息：",
        "help": "📖 命令：\n/word — 每日一词\n/num 123 — 阿拉伯数字 → 高棉数字\n/phrase — 随机短语\n/lang — 切换语言\n/menu — 菜单",
        "about": "🤖 *SB24GZ Khmer Bot*\n高棉语学习助手。\n多语言界面。\n部署在 Railway 🚂",
        "pick_lang": "🌐 选择您的语言：",
        "lang_set": "✅ 语言已设为中文。",
        "phrase_title": "💬 常用短语",
    },
    "fr": {
        "welcome": "👋 Bienvenue sur *SB24GZ Khmer Bot* !\n\nJe vous aide à apprendre le khmer 🇰🇭",
        "choose": "Choisissez une fonction :",
        "word": "📚 Mot du jour",
        "num_btn": "🔢 Nombres → Khmer",
        "phrase_btn": "💬 Phrase aléatoire",
        "char_btn": "🔤 Infos caractère khmer",
        "about_btn": "ℹ️ À propos",
        "lang_btn": "🌐 Changer de langue",
        "original": "Original",
        "rom": "Prononciation",
        "meaning": "Signification",
        "example": "Exemple",
        "usage_num": "Utilisation : /num 123",
        "char_info": "🔤 Envoyez du texte khmer, je montrerai les noms Unicode.",
        "char_title": "🔤 Infos caractère khmer :",
        "help": "📖 Commandes :\n/word — Mot du jour\n/num 123 — Chiffres arabes → khmers\n/phrase — Phrase aléatoire\n/lang — Changer de langue\n/menu — Menu",
        "about": "🤖 *SB24GZ Khmer Bot*\nAssistant d'apprentissage du khmer.\nInterface multilingue.\nDéployé sur Railway 🚂",
        "pick_lang": "🌐 Choisissez votre langue :",
        "lang_set": "✅ Langue définie sur le français.",
        "phrase_title": "💬 Phrase courante",
    },
    "ja": {
        "welcome": "👋 *SB24GZ Khmer Bot* へようこそ！\n\nクメール語学習をお手伝いします 🇰🇭",
        "choose": "機能を選択してください：",
        "word": "📚 今日の単語",
        "num_btn": "🔢 数字 → クメール数字",
        "phrase_btn": "💬 ランダムフレーズ",
        "char_btn": "🔤 クメール文字情報",
        "about_btn": "ℹ️ 概要",
        "lang_btn": "🌐 言語を変更",
        "original": "原文",
        "rom": "発音",
        "meaning": "意味",
        "example": "例文",
        "usage_num": "使い方：/num 123",
        "char_info": "🔤 クメール文字を送ってください。Unicode 名を表示します。",
        "char_title": "🔤 クメール文字情報：",
        "help": "📖 コマンド：\n/word — 今日の単語\n/num 123 — アラビア数字 → クメール数字\n/phrase — ランダムフレーズ\n/lang — 言語を変更\n/menu — メニュー",
        "about": "🤖 *SB24GZ Khmer Bot*\nクメール語学習アシスタント。\n多言語対応。\nRailway でデプロイ 🚂",
        "pick_lang": "🌐 言語を選択してください：",
        "lang_set": "✅ 言語を日本語に設定しました。",
        "phrase_title": "💬 よく使うフレーズ",
    },
    "es": {
        "welcome": "👋 ¡Bienvenido a *SB24GZ Khmer Bot*!\n\nTe ayudo a aprender jemer 🇰🇭",
        "choose": "Elige una función:",
        "word": "📚 Palabra del día",
        "num_btn": "🔢 Números → Jemer",
        "phrase_btn": "💬 Frase aleatoria",
        "char_btn": "🔤 Info de carácter jemer",
        "about_btn": "ℹ️ Acerca de",
        "lang_btn": "🌐 Cambiar idioma",
        "original": "Original",
        "rom": "Pronunciación",
        "meaning": "Significado",
        "example": "Ejemplo",
        "usage_num": "Uso: /num 123",
        "char_info": "🔤 Envía texto jemer y mostraré los nombres Unicode.",
        "char_title": "🔤 Info de carácter jemer:",
        "help": "📖 Comandos:\n/word — Palabra del día\n/num 123 — Números árabes → jemeres\n/phrase — Frase aleatoria\n/lang — Cambiar idioma\n/menu — Menú",
        "about": "🤖 *SB24GZ Khmer Bot*\nAsistente de aprendizaje de jemer.\nInterfaz multilingüe.\nDesplegado en Railway 🚂",
        "pick_lang": "🌐 Elige tu idioma:",
        "lang_set": "✅ Idioma establecido en español.",
        "phrase_title": "💬 Frase común",
    },
}

def S(uid: int, key: str) -> str:
    return STRINGS.get(get_lang(uid), STRINGS["en"]).get(key, key)

# ---------- Khmer numerals ----------
KHMER_DIGITS = {
    "0": "០", "1": "១", "2": "២", "3": "៣", "4": "៤",
    "5": "៥", "6": "៦", "7": "៧", "8": "៨", "9": "៩",
}

def to_khmer_numeral(text: str) -> str:
    return "".join(KHMER_DIGITS.get(ch, ch) for ch in text)

# ---------- Vocabulary (each word translated into all UI langs) ----------
VOCAB = [
    {
        "km": "សួស្តី", "rom": "suostei",
        "tr": {"en": "Hello", "km": "សួស្តី", "zh": "你好", "fr": "Bonjour", "ja": "こんにちは", "es": "Hola"},
        "ex": {
            "en": "Suostei! How are you?",
            "km": "សួស្តី! អ្នកសុខសប្បាយទេ?",
            "zh": "你好！你好吗？",
            "fr": "Bonjour ! Comment allez-vous ?",
            "ja": "こんにちは！お元気ですか？",
            "es": "¡Hola! ¿Cómo estás?",
        },
    },
    {
        "km": "អរគុណ", "rom": "orkun",
        "tr": {"en": "Thank you", "km": "អរគុណ", "zh": "谢谢", "fr": "Merci", "ja": "ありがとう", "es": "Gracias"},
        "ex": {
            "en": "Orkun for your help.",
            "km": "អរគុណសម្រាប់ជំនួយ។",
            "zh": "谢谢你的帮助。",
            "fr": "Merci pour votre aide.",
            "ja": "助けてくれてありがとう。",
            "es": "Gracias por tu ayuda.",
        },
    },
    {
        "km": "ទឹក", "rom": "teuk",
        "tr": {"en": "Water", "km": "ទឹក", "zh": "水", "fr": "Eau", "ja": "水", "es": "Agua"},
        "ex": {
            "en": "I want to drink water.",
            "km": "ខ្ញុំចង់ផឹកទឹក។",
            "zh": "我想喝水。",
            "fr": "Je veux boire de l'eau.",
            "ja": "水が飲みたいです。",
            "es": "Quiero beber agua.",
        },
    },
    {
        "km": "ផ្ទះ", "rom": "phteah",
        "tr": {"en": "House", "km": "ផ្ទះ", "zh": "房子", "fr": "Maison", "ja": "家", "es": "Casa"},
        "ex": {
            "en": "My house is near here.",
            "km": "ផ្ទះខ្ញុំនៅជិតទីនេះ។",
            "zh": "我家在这附近。",
            "fr": "Ma maison est près d'ici.",
            "ja": "私の家はこの近くです。",
            "es": "Mi casa está cerca de aquí.",
        },
    },
    {
        "km": "ស្រលាញ់", "rom": "sralanh",
        "tr": {"en": "Love", "km": "ស្រលាញ់", "zh": "爱", "fr": "Amour", "ja": "愛", "es": "Amor"},
        "ex": {
            "en": "I love you.",
            "km": "ខ្ញុំស្រលាញ់អ្នក។",
            "zh": "我爱你。",
            "fr": "Je t'aime.",
            "ja": "愛してる。",
            "es": "Te quiero.",
        },
    },
]

PHRASES = [
    {"km": "សួស្តី", "rom": "suostei", "tr": {"en": "Hello", "km": "សួស្តី", "zh": "你好", "fr": "Bonjour", "ja": "こんにちは", "es": "Hola"}},
    {"km": "អរគុណ", "rom": "orkun", "tr": {"en": "Thank you", "km": "អរគុណ", "zh": "谢谢", "fr": "Merci", "ja": "ありがとう", "es": "Gracias"}},
    {"km": "តើថ្លៃប៉ុន្មាន?", "rom": "tae thlai ponman?", "tr": {"en": "How much?", "km": "តើថ្លៃប៉ុន្មាន?", "zh": "多少钱？", "fr": "Combien ?", "ja": "いくらですか？", "es": "¿Cuánto?"}},
    {"km": "ខ្ញុំមិនយល់ទេ", "rom": "khnyom min yol te", "tr": {"en": "I don't understand", "km": "ខ្ញុំមិនយល់ទេ", "zh": "我不明白", "fr": "Je ne comprends pas", "ja": "わかりません", "es": "No entiendo"}},
]

# ---------- Menus ----------
def main_menu(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(S(uid, "word"), callback_data="daily")],
        [InlineKeyboardButton(S(uid, "num_btn"), callback_data="numbers")],
        [InlineKeyboardButton(S(uid, "phrase_btn"), callback_data="phrase")],
        [InlineKeyboardButton(S(uid, "char_btn"), callback_data="charinfo")],
        [InlineKeyboardButton(S(uid, "lang_btn"), callback_data="lang")],
        [InlineKeyboardButton(S(uid, "about_btn"), callback_data="about")],
    ])

def lang_menu() -> InlineKeyboardMarkup:
    rows = [[InlineKeyboardButton(label, callback_data=f"setlang:{code}")]
            for code, label in LANGS.items()]
    return InlineKeyboardMarkup(rows)

# ---------- Handlers ----------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(
        S(uid, "welcome") + "\n\n" + S(uid, "choose"),
        parse_mode="Markdown",
        reply_markup=main_menu(uid),
    )

async def help_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(S(uid, "help"), parse_mode="Markdown")

async def about(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = update.effective_user.id
    if q:
        await q.answer()
        await q.edit_message_text(
            S(uid, "about"),
            parse_mode="Markdown",
            reply_markup=main_menu(uid),
        )
    else:
        await update.message.reply_text(S(uid, "about"), parse_mode="Markdown")

async def menu_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(S(uid, "choose"), reply_markup=main_menu(uid))

async def lang_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    await update.message.reply_text(S(uid, "pick_lang"), reply_markup=lang_menu())

async def word_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    v = random.choice(VOCAB)
    await update.message.reply_text(
        f"📚 *{S(uid, 'word')}*\n\n"
        f"🇰🇭 *{v['km']}*\n"
        f"🔊 _{v['rom']}_\n\n"
        f"*{S(uid, 'meaning')}:* {v['tr'].get(lang, v['tr']['en'])}\n\n"
        f"📝 *{S(uid, 'example')}:*\n{v['ex'].get(lang, v['ex']['en'])}",
        parse_mode="Markdown",
    )

async def num_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = " ".join(ctx.args)
    if not text:
        return await update.message.reply_text(S(uid, "usage_num"), parse_mode="Markdown")
    result = to_khmer_numeral(text)
    await update.message.reply_text(f"🔢 *{text}* → *{result}*", parse_mode="Markdown")

async def phrase_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    lang = get_lang(uid)
    p = random.choice(PHRASES)
    await update.message.reply_text(
        f"{S(uid, 'phrase_title')}\n\n"
        f"🇰🇭 *{p['km']}*\n"
        f"🔊 _{p['rom']}_\n"
        f"*{S(uid, 'meaning')}:* {p['tr'].get(lang, p['tr']['en'])}",
        parse_mode="Markdown",
    )

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = update.effective_user.id
    lang = get_lang(uid)
    await q.answer()

    if q.data == "about":
        return await about(update, ctx)
    if q.data == "lang":
        return await q.edit_message_text(S(uid, "pick_lang"), reply_markup=lang_menu())
    if q.data.startswith("setlang:"):
        new_lang = q.data.split(":", 1)[1]
        if new_lang in LANGS:
            USER_LANG[uid] = new_lang
            return await q.edit_message_text(
                S(uid, "lang_set"),
                reply_markup=main_menu(uid),
            )
    if q.data == "daily":
        v = random.choice(VOCAB)
        return await q.edit_message_text(
            f"📚 *{S(uid, 'word')}*\n\n🇰🇭 *{v['km']}*\n🔊 _{v['rom']}_\n\n"
            f"*{S(uid, 'meaning')}:* {v['tr'].get(lang, v['tr']['en'])}\n\n"
            f"📝 *{S(uid, 'example')}:*\n{v['ex'].get(lang, v['ex']['en'])}",
            parse_mode="Markdown",
            reply_markup=main_menu(uid),
        )
    if q.data == "phrase":
        p = random.choice(PHRASES)
        return await q.edit_message_text(
            f"{S(uid, 'phrase_title')}\n\n🇰🇭 *{p['km']}*\n🔊 _{p['rom']}_\n"
            f"*{S(uid, 'meaning')}:* {p['tr'].get(lang, p['tr']['en'])}",
            parse_mode="Markdown",
            reply_markup=main_menu(uid),
        )
    if q.data == "numbers":
        return await q.edit_message_text(S(uid, "usage_num"), parse_mode="Markdown")
    if q.data == "charinfo":
        return await q.edit_message_text(S(uid, "char_info"), parse_mode="Markdown")

# ---------- Khmer character info ----------
async def khmer_char_info(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    uid = update.effective_user.id
    has_khmer = any("\u1780" <= ch <= "\u17ff" for ch in text)
    if not has_khmer:
        return
    lines = []
    for ch in text:
        if "\u1780" <= ch <= "\u17ff":
            try:
                name = unicodedata.name(ch)
            except ValueError:
                name = "UNKNOWN"
            lines.append(f"`{ch}` → {name}")
    if lines:
        await update.message.reply_text(
            f"{S(uid, 'char_title')}\n\n" + "\n".join(lines[:15]),
            parse_mode="Markdown",
        )

async def auto_numeral(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        return
    result = to_khmer_numeral(text)
    await update.message.reply_text(f"🔢 *{text}* → *{result}*", parse_mode="Markdown")

async def error_handler(update: object, ctx: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception:", exc_info=ctx.error)

# ---------- Main ----------
def main():
    if not TOKEN:
        logger.error("❌ BOT_TOKEN missing")
        time.sleep(30)
        raise SystemExit(1)
    logger.info(f"🚀 Starting SB24GZ Khmer Bot (token len={len(TOKEN)})")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("menu", menu_cmd))
    app.add_handler(CommandHandler("lang", lang_cmd))
    app.add_handler(CommandHandler("word", word_cmd))
    app.add_handler(CommandHandler("num", num_cmd))
    app.add_handler(CommandHandler("phrase", phrase_cmd))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, khmer_char_info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_numeral))
    app.add_error_handler(error_handler)

    logger.info("✅ Bot polling...")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
