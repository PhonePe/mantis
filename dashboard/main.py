from fastapi import FastAPI, status
from pymongo import MongoClient

#routes
from routes.assets import router as assets
from routes.certificates import router as certificates
from routes.informational_vulnerabilities import router as infoVulnerabilities
from routes.network_information import router as network_information
from routes.phishing_domain import router as phishing_domain
from routes.secrets import router as secrets
from routes.vulnerabilities import router as vulnerabilities
from routes.org import router as org
from routes.static_page_routes import router as static_page_routes
from routes.login_reg import router as loginReg
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# from router.test import test
app = FastAPI(
    # docs_url=None, # Disable docs (Swagger UI)
    # redoc_url=None, # Disable redoc
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://mantis.dashboard:8000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# app.add_middleware(TokenMiddleware)


# class TokenMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
        
#         if request.url.path not in ["/login", "/registration"]:
#             access_token = request.cookies.get("access_token")
#             if not access_token:
#                 return RedirectResponse(url="/login")

#         response = await call_next(request)
#         return response



@app.exception_handler(404)
async def custom_404_handler(request, __):
    return templates.TemplateResponse("404.html", {"request": request })


#include routers
app.include_router(static_page_routes)
app.include_router(loginReg)
app.include_router(assets)
app.include_router(org)
app.include_router(certificates)
app.include_router(infoVulnerabilities)
app.include_router(phishing_domain)
app.include_router(network_information)
app.include_router(secrets)
app.include_router(vulnerabilities)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


#mongo connection
client = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.1")


#mongodb details
db = client["mantis"]
Assets_collection = db["assets_collection"]
Findings_collection = db["findings_collection"]


