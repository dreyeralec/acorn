from acorn.engine import dispatch_acorn

def test_dispatch_acorn():
    dispatch_acorn("trade")
    dispatch_acorn("analysis")