from telegram.telegram import telegram_client


def test_send_trade():
    telegram_client.tel_send_trade("NVDA", "BUY", 5, "MKT", None, "testing", 1, 1)


def test_tel_notify():
    telegram_client.tel_notify("Testing function tel_notify: respond with YES")


def test_get_response_with_tel_notify():
    res = telegram_client.tel_get_response()
    assert res is not None
    assert res == "YES"
    if res == "YES":
        telegram_client.tel_notify("passed!")