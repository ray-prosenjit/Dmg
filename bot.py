
import io, pyotp, instaloader as ins
from telegram import Update, ReplyKeyboardMarkup as RK
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes

# কনফিগারেশন
TOKEN = '8696096538:AAEwCxJm_-DjduDayZj3_PhgbcuJKx4-OmY'
U, P, T = range(3)

async def start(up: Update, c: ContextTypes.DEFAULT_TYPE):
    kb = [['🚀 START KOR SALA'], ['❌ CANCEL']]
    await up.message.reply_text("🔱 DMG GENERATOR COOKIES✅", reply_markup=RK(kb, resize_keyboard=True))
    return ConversationHandler.END

async def ask_u(up: Update, c: ContextTypes.DEFAULT_TYPE):
    await up.message.reply_text("👤 ইউজারনেম লিস্ট দিন:")
    return U

async def get_u(up: Update, c: ContextTypes.DEFAULT_TYPE):
    text = up.message.text
    if text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    c.user_data['u'] = text.split('\n')
    await up.message.reply_text("🔐 কমন পাসওয়ার্ড দিন:")
    return P

async def get_p(up: Update, c: ContextTypes.DEFAULT_TYPE):
    text = up.message.text
    if text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    c.user_data['p'] = text.strip()
    await up.message.reply_text("🔑 2FA Key দিন:")
    return T

async def run(up: Update, c: ContextTypes.DEFAULT_TYPE):
    text = up.message.text
    if text == '❌ CANCEL':
        await up.message.reply_text("🚫 Cancel করা হয়েছে।")
        return ConversationHandler.END
    
    seeds = text.split('\n')
    users = c.user_data.get('u', [])
    pw = c.user_data.get('p', '')
    
    await up.message.reply_text("🤖 আরে বোকাচোদা ওয়েট কর ব্যস্ত কেন এত!")
    
    res = ""
    for i, user in enumerate(users):
        L = ins.Instaloader()
        try:
            s = seeds[i].strip().replace(" ", "") if i < len(seeds) else ""
            try:
                L.login(user, pw)
            except:
                if s: 
                    L.two_factor_login(pyotp.TOTP(s).now())
                else: 
                    raise Exception("No Seed")
            
            ck = "; ".join([f"{k}={v}" for k, v in L.context._session.cookies.get_dict().items()])
            res += f"{user}|{pw}|{ck}\n"
            await up.message.reply_text(f"✅ Success: {user}")
        except:
            await up.message.reply_text(f"❌ Failed: {user}")
    
    if res:
        bio = io.BytesIO(res.encode())
        bio.name = "Dmg.txt"
        await up.message.reply_document(document=bio, caption="📊 এই নে বোকাচোদা তোর ফাইল রেডি।")
    
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
    print("Bot is running...")
    app.run_polling()
