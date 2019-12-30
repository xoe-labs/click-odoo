# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This package implements a client session store for use with scarlette
asgi client session middleware"""


from secure_cookie.sessions import SessionStore


class ClientSessionStore(SessionStore):
    """Werkzeug client session store implementation for asgi.
    :param global_scope: A global handle to access the asgi scope
        to strore the session on.
    """

    def __init__(self, global_scope=None, **kwargs):
        super().__init__(**kwargs)
        self.global_scope = global_scope

    def save(self, session):
        """Save a session."""
        scope = self.global_scope.get()
        scope["session"] = dict(session)

    def delete(self, session):
        """Delete a session."""
        scope = self.global_scope.get()
        if scope["session"].get("sid") != session.sid:
            return
        scope["session"] = {}

    def get(self, sid):
        """Get a session for this sid or a new session object. This
        method has to check if the session key is valid and create a new
        session if that wasn't the case.
        """
        if not self.is_valid_key(sid):
            return self.new()

        scope = self.global_scope.get()
        if scope["session"].get("sid") != sid:
            return self.new()
        data = scope["session"]
        return self.session_class(data, sid, False)
