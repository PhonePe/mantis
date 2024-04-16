from fastapi import APIRouter, Request, Query, Security
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import Annotated
from pydantic import BaseModel
from routes.login_reg import get_current_user
from models.user import User


router = APIRouter(
    tags=['Pages']
)

#tempelete and static file mount
router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

#route for the testing 
@router.get("/login", response_class=HTMLResponse)
async def read_item(request: Request): 

    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registration", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("reg.html", {"request": request})

@router.get("/admin", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["admin"])]):
    return templates.TemplateResponse("admin.html", {"request": request, "current_user": current_user})

#route for vulnerabilities page
@router.get("/vulnerabilities", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    print(current_user)
    return templates.TemplateResponse("vulnerabilities.html", {"request": request, "current_user": current_user})


#route for secrets page
@router.get("/secrets", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("secrets.html", {"request": request, "current_user": current_user})

#route for Phishing page
@router.get("/Phishing", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("Phishing.html", {"request": request, "current_user": current_user})

#route for network_information page
@router.get("/network_info", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("network_info.html", {"request": request, "current_user": current_user})

#route for information_vulnerabilities page
@router.get("/information_vul", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("information_vul.html", {"request": request, "current_user": current_user})

#route for certificates page
@router.get("/certificates", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("certificates.html", {"request": request, "current_user": current_user})

#route for assets page
@router.get("/assets", response_class=HTMLResponse)
async def read_item(request: Request, current_user: Annotated[User, Security(get_current_user, scopes=["write", "read", "admin"])]):
    return templates.TemplateResponse("assets.html", {"request": request, "current_user": current_user})