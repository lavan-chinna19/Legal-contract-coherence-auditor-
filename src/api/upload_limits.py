"""Bound multipart bytes before parsing; prevent plaintext tempfile spooling."""
from starlette.formparsers import MultiPartParser
from starlette.responses import JSONResponse
from src.api.ingestion import MAX_UPLOAD_BYTES

MAX_MULTIPART_BYTES = MAX_UPLOAD_BYTES + 64 * 1024
# The byte-limit middleware buffers at most this amount before the framework parser.
MultiPartParser.spool_max_size = MAX_MULTIPART_BYTES


class UploadLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope["path"] != "/v1/upload":
            return await self.app(scope, receive, send)
        chunks, length = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            length += len(message.get("body", b""))
            if length > MAX_MULTIPART_BYTES:
                return await JSONResponse({"detail": "Upload exceeds the 10 MB file limit."}, status_code=413)(scope, receive, send)
            chunks.append(message.get("body", b""))
            if not message.get("more_body", False):
                break
        sent = False
        async def bounded_receive():
            nonlocal sent
            if not sent:
                sent = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()
        await self.app(scope, bounded_receive, send)
