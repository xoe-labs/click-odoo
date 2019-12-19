# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements a client session store for use with scarlette
asgi client session middleware"""


from secure_cookie.sessions import SessionStore


class ClientSessionStore(SessionStore):
    """Werkzeug client session store implementation for asgi.
    :param scope: The asgi scope to strore the session on.
    """

    # path = odoo.tools.config.session_dir
    def __init__(self, scope=None, **kwargs):
        super().__init__(**kwargs)
        self.scope = scope

    def save(self, session):
        """Save a session."""
        self.scope = dict(session)

    def delete(self, session):
        """Delete a session."""
        if self.scope["session"].get("sid") != session.sid:
            return
        self.scope = {}

    def get(self, sid):
        """Get a session for this sid or a new session object. This
        method has to check if the session key is valid and create a new
        session if that wasn't the case.
        """
        if not self.is_valid_key(sid):
            return self.new()

        if self.scope["session"].get("sid") != sid:
            return self.new()
        data = self.scope["session"]
        return self.session_class(data, sid, False)
