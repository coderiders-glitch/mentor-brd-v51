from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import search_router


app = FastAPI(
    title="GLM Alumni Tracker",
    description="Track and manage alumni relationships",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "healthy"}

# AGENTIC_SDLC_SPA_STATIC: serve the built frontend from ./static on the deploy URL.
import os as _spa_os
import mimetypes as _spa_mimetypes
from pathlib import Path as _SpaPath
from fastapi.responses import FileResponse as _SpaFileResponse

# Browsers enforce strict MIME types for ES modules (.mjs) and WebAssembly
# (.wasm). Python's default mimetypes serves them as application/octet-stream,
# which the browser rejects ("non-JavaScript MIME type"), breaking modern
# bundles (Vite chunks, the pdf.js worker, etc). Register + map them explicitly.
_spa_mimetypes.add_type("text/javascript", ".js")
_spa_mimetypes.add_type("text/javascript", ".mjs")
_spa_mimetypes.add_type("application/wasm", ".wasm")
_spa_mimetypes.add_type("application/json", ".map")

_SPA_MEDIA_TYPES = {
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".wasm": "application/wasm",
    ".css": "text/css",
    ".json": "application/json",
    ".map": "application/json",
    ".svg": "image/svg+xml",
}


def _spa_media_type(path):
    return _SPA_MEDIA_TYPES.get(_SpaPath(str(path)).suffix.lower())


def _spa_file_response(path):
    media = _spa_media_type(path)
    return _SpaFileResponse(path, media_type=media) if media else _SpaFileResponse(path)


def _spa_find_static_dir() -> _SpaPath:
    here = _SpaPath(__file__).resolve()
    candidates = [
        here.parent.parent / "static",
        here.parent / "static",
        here.parent.parent.parent / "static",
        _SpaPath(_spa_os.getcwd()) / "static",
        _SpaPath("/app/static"),
    ]
    for cand in candidates:
        if (cand / "index.html").is_file():
            return cand
    for cand in candidates:
        if cand.is_dir():
            return cand
    return candidates[0]


_STATIC_DIR = _spa_find_static_dir()


@app.get("/")
async def _agentic_spa_root():
    index = _STATIC_DIR / "index.html"
    if index.is_file():
        return _spa_file_response(index)
    return {"message": "API is running", "status": "healthy"}


@app.get("/{full_path:path}")
async def _agentic_spa_fallback(full_path: str):
    reserved = ("api", "health", "docs", "openapi.json", "redoc")
    first = (full_path or "").split("/", 1)[0]
    if first in reserved:
        from fastapi.responses import JSONResponse as _SpaJSON
        return _SpaJSON({"detail": "Not Found"}, status_code=404)
    candidate = (_STATIC_DIR / full_path).resolve()
    static_root = _STATIC_DIR.resolve()
    if str(candidate).startswith(str(static_root)) and candidate.is_file():
        return _spa_file_response(candidate)
    # Missing JS/CSS/font assets must 404 — returning index.html here breaks the UI.
    asset_ext = (".js", ".mjs", ".wasm", ".css", ".map", ".woff", ".woff2", ".ttf", ".svg", ".png", ".jpg", ".ico")
    if full_path and full_path.lower().endswith(asset_ext):
        from fastapi.responses import JSONResponse as _SpaJSON
        return _SpaJSON({"detail": "Not Found"}, status_code=404)
    index = _STATIC_DIR / "index.html"
    if index.is_file():
        return _spa_file_response(index)
    from fastapi.responses import JSONResponse as _SpaJSON
    return _SpaJSON({"detail": "Not Found"}, status_code=404)