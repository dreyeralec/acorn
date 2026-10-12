from telegram.telegram import telegram_client


def test_send_trade():
    telegram_client.tel_send_trade("NVDA", "BUY", 5, "MKT", None, "testing", 1, 1)