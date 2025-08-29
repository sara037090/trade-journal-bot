import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.executor import start_webhook
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# گرفتن توکن از متغیر محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN")

# تنظیمات وبهوک
WEBHOOK_HOST = os.getenv("WEBHOOK_URL")  # این رو بعد از دیپلوی در Koyeb می‌ذاریم
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# تنظیمات وب‌سرور
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.getenv("PORT", 8000))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# تعریف استیت‌ها
class TradeForm(StatesGroup):
    symbol = State()
    trade_type = State()
    volume = State()
    entry_price = State()
    stop_loss = State()
    take_profit = State()
    reason = State()

# شروع
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("➕ ثبت معامله جدید"), KeyboardButton("📂 لیست معاملات من"))
    await message.answer("سلام! به ژورنال ترید خوش اومدی 📊", reply_markup=kb)

# شروع ثبت معامله
@dp.message_handler(lambda m: m.text == "➕ ثبت معامله جدید")
async def new_trade(message: types.Message):
    await message.answer("نماد رو وارد کن (مثلاً BTCUSDT):")
    await TradeForm.symbol.set()

@dp.message_handler(state=TradeForm.symbol)
async def set_symbol(message: types.Message, state: FSMContext):
    await state.update_data(symbol=message.text)
    await message.answer("نوع معامله رو انتخاب کن (خرید یا فروش):")
    await TradeForm.trade_type.set()

@dp.message_handler(state=TradeForm.trade_type)
async def set_type(message: types.Message, state: FSMContext):
    await state.update_data(trade_type=message.text)
    await message.answer("حجم معامله رو وارد کن:")
    await TradeForm.volume.set()

@dp.message_handler(state=TradeForm.volume)
async def set_volume(message: types.Message, state: FSMContext):
    await state.update_data(volume=message.text)
    await message.answer("قیمت ورود رو وارد کن:")
    await TradeForm.entry_price.set()

@dp.message_handler(state=TradeForm.entry_price)
async def set_entry(message: types.Message, state: FSMContext):
    await state.update_data(entry_price=message.text)
    await message.answer("حد ضرر رو وارد کن (یا بنویس ندارد):")
    await TradeForm.stop_loss.set()

@dp.message_handler(state=TradeForm.stop_loss)
async def set_sl(message: types.Message, state: FSMContext):
    await state.update_data(stop_loss=message.text)
    await message.answer("حد سود رو وارد کن (یا بنویس ندارد):")
    await TradeForm.take_profit.set()

@dp.message_handler(state=TradeForm.take_profit)
async def set_tp(message: types.Message, state: FSMContext):
    await state.update_data(take_profit=message.text)
    await message.answer("دلیل ورود رو بنویس:")
    await TradeForm.reason.set()

@dp.message_handler(state=TradeForm.reason)
async def set_reason(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text)
    data = await state.get_data()
    summary = (
        f"📌 نماد: {data['symbol']}\n"
        f"📈 نوع: {data['trade_type']}\n"
        f"📦 حجم: {data['volume']}\n"
        f"💵 ورود: {data['entry_price']}\n"
        f"⛔ حد ضرر: {data['stop_loss']}\n"
        f"🎯 حد سود: {data['take_profit']}\n"
        f"📝 دلیل: {data['reason']}"
    )
    await message.answer("✅ معامله ثبت شد:\n" + summary)
    await state.finish()

# وبهوک
async def on_startup(dp):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dp):
    await bot.delete_webhook()

if __name__ == '__main__':
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
