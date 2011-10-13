if 1:
    import os
    from gaesessions import SessionMiddleware
    def webapp_add_wsgi_middleware(app):
        cookie_key = '\xb2EV;\x06]gE\r\x12t\xb3j\xd2W\xd8\x01\xb4\xbc\xc0.\xe2\n\xba\x13\xca`\xccc*x\x0c\x10\x02\n\x86\x07\x90R\xc0\xf2\x1e#\xc3\xaf%\xb0\x12\xc8Q\x97\x0b|\x12%.\x18\xe3\xbc\x91\xce\xcf\x8c`'
        app = SessionMiddleware(app, cookie_key=cookie_key)
        return app
        