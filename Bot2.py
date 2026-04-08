import io, pyotp, instaloader as ins
from telegram import Update, ReplyKeyboardMarkup as RK
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

TOKEN = '8696096538:AAEwCxJm_-DjduDayZj3_PhgbcuJKx4-OmY'
U, P, T = range(3)

async def start(up: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [['🚀 START KOR SALA'], ['❌ CANCEL']]
    await up.message.reply_text("🔱 DMG GENERATOR V2 (2FA Optional) ✅", reply_markup=RK(kb, resize_keyboard=True))
    return ConversationHandler.END

async def ask_u(up: Update, c: ContextTypes.DEFAULT_TYPE):
    await up.message.reply_text("👤 ইউজারনেম লিস্ট দিন (নতুন লাইন করে):")
    return U

async def get_u(up: Update, c: ContextTypes.DEFAULT_TYPE):
    if up.message.text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    c.user_data['u'] = up.message.text.split('\n')
    await up.message.reply_text("🔐 কমন পাসওয়ার্ড দিন:")
    return P

async def get_p(up: Update, c: ContextTypes.DEFAULT_TYPE):
    if up.message.text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    c.user_data['p'] = up.message.text.strip()
    await up.message.reply_text("🔑 2FA Key দিন (না থাকলে no লিখুন):")
    return T

async def run(up: Update, c: ContextTypes.DEFAULT_TYPE):
    if up.message.text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    
    seeds = up.message.text.split('\n')
    users = c.user_data.get('u', [])
    pw = c.user_data.get('p', '')
    await up.message.reply_text("🤖 প্রসেসিং হচ্ছে... একটু দাঁড়ান!")
    
    res = ""
    for i, user in enumerate(users):
        L = ins.Instaloader()
        user = user.strip()
        try:
            try:
                L.login(user, pw)
            except:
                s = seeds[i].strip() if (i < len(seeds) and seeds[i].lower() != 'no') else ""
                if s: L.two_factor_login(pyotp.TOTP(s).now())
                else: raise Exception("Failed")
            
            ck = "; ".join([f"{k}={v}" for k, v in L.context._session.cookies.get_dict().items()])
            res += f"{user}|{pw}|{ck}\n"
            await up.message.reply_text(f"✅ Success: {user}")
        except:
            await up.message.reply_text(f"❌ Failed: {user}")
    
    if res:
        bio = io.BytesIO(res.encode()); bio.name = "Cookies_V2.txt"
        await up.message.reply_document(document=bio, caption="📊 এই নিন আপনার নতুন কুকি ফাইল।")
    
    c.user_data.clear()
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex('^🚀 START KOR SALA$'), ask_u)],
        states={
            U: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_u)],
            P: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_p)],
            T: [MessageHandler(filters.TEXT & ~filters.COMMAND, run)]
        },
        fallbacks=[MessageHandler(filters.Regex('^❌ CANCEL$'), start)]
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv)
    app.run_polling()