import re
import logging
from typing import Dict, List, Optional, Tuple, Any

class LoginDetector:
    """
    Utility for detecting login forms, password inputs, authentication endpoints,
    and exposed login surfaces across web assets, HTTP responses, HTML bodies, and URL paths.
    """

    # Common URL path keywords indicating login, authentication, admin, or SSO portals
    AUTH_PATH_PATTERNS = [
        r'(?:^|/)(?:login|signin|sign-in|authenticate|auth|session|oauth|sso|cas|saml)(?:$|[/?#._])',
        r'(?:^|/)(?:admin|administrator|admin-login|wp-login|user/login|cpanel|webmail)(?:$|[/?#._])',
        r'(?:^|/)(?:portal|dashboard|authn|idp|keycloak|auth0)(?:$|[/?#._])',
        r'(?:^|/)(?:api/v\d+/(?:auth|login|token|oauth|authenticate))(?:$|[/?#._])',
    ]

    # HTML Input field patterns indicating login / authentication forms
    PASSWORD_INPUT_PATTERN = re.compile(
        r'<input[^>]+type\s*=\s*["\']password["\'][^>]*>',
        re.IGNORECASE
    )

    USERNAME_EMAIL_INPUT_PATTERN = re.compile(
        r'<input[^>]+(?:name|id|autocomplete|placeholder)\s*=\s*["\'](?:username|user|email|login|user_login|userid|account)["\'][^>]*>',
        re.IGNORECASE
    )

    FORM_ACTION_AUTH_PATTERN = re.compile(
        r'<form[^>]+action\s*=\s*["\'][^"\']*(?:login|signin|sign-in|auth|session|authenticate|token)[^"\']*["\'][^>]*>',
        re.IGNORECASE
    )

    LOGIN_BUTTON_TEXT_PATTERN = re.compile(
        r'<(?:button|input)[^>]+(?:type\s*=\s*["\']submit["\'][^>]*)?(?:value\s*=\s*["\'](?:Log\s*In|Sign\s*In|Login|Submit|Authorize)["\'][^>]*>|>[^<]*(?:Log\s*In|Sign\s*In|Login)[^<]*</button>)',
        re.IGNORECASE
    )

    OAUTH_SSO_INDICATOR_PATTERN = re.compile(
        r'(?:Sign\s*in\s*with\s*(?:Google|Microsoft|Apple|GitHub|Okta|SAML|SSO)|OAuth\s*2\.0\s*Authorization\s*Server)',
        re.IGNORECASE
    )

    @classmethod
    def matches_auth_path(cls, url_or_path: str) -> bool:
        """Check if a URL or path matches known login/auth endpoint patterns."""
        if not url_or_path:
            return False
        for pattern in cls.AUTH_PATH_PATTERNS:
            if re.search(pattern, url_or_path, re.IGNORECASE):
                return True
        return False

    @classmethod
    def has_password_field(cls, html_content: str) -> bool:
        """Check if HTML content contains an input field of type password."""
        if not html_content:
            return False
        return bool(cls.PASSWORD_INPUT_PATTERN.search(html_content))

    @classmethod
    def analyze_html_content(cls, html_content: str, url: str = "") -> Dict[str, Any]:
        """
        Analyze HTML content for login surfaces.
        Returns a dictionary containing detection metadata and confidence score.
        """
        if not html_content:
            return {
                "is_login_page": False,
                "confidence": "LOW",
                "indicators": [],
                "has_password_field": False,
                "has_auth_form": False,
                "has_auth_endpoint": False
            }

        indicators: List[str] = []
        score = 0

        # Check password input field
        has_password = bool(cls.PASSWORD_INPUT_PATTERN.search(html_content))
        if has_password:
            indicators.append("Password input field detected (<input type='password'>)")
            score += 50

        # Check username / email field
        has_username = bool(cls.USERNAME_EMAIL_INPUT_PATTERN.search(html_content))
        if has_username:
            indicators.append("Username/Email input field detected")
            score += 20

        # Check form action
        has_auth_form = bool(cls.FORM_ACTION_AUTH_PATTERN.search(html_content))
        if has_auth_form:
            indicators.append("Form action targeting auth/login endpoint detected")
            score += 25

        # Check login button text
        has_login_btn = bool(cls.LOGIN_BUTTON_TEXT_PATTERN.search(html_content))
        if has_login_btn:
            indicators.append("Login/Sign-in submit button detected")
            score += 15

        # Check OAuth/SSO indicators
        has_sso = bool(cls.OAUTH_SSO_INDICATOR_PATTERN.search(html_content))
        if has_sso:
            indicators.append("OAuth/SSO authorization indicator detected")
            score += 20

        # Check URL path
        has_auth_path = cls.matches_auth_path(url)
        if has_auth_path:
            indicators.append("URL path matches authentication endpoint pattern")
            score += 20

        is_login = has_password or (score >= 40)

        if score >= 60:
            confidence = "HIGH"
        elif score >= 30:
            confidence = "MEDIUM"
        else:
            confidence = "LOW"

        return {
            "is_login_page": is_login,
            "confidence": confidence,
            "score": score,
            "indicators": indicators,
            "has_password_field": has_password,
            "has_auth_form": has_auth_form,
            "has_auth_endpoint": has_auth_path,
            "has_sso": has_sso
        }

    @classmethod
    def detect_login_surface(cls, url: str, html_body: Optional[str] = None, status_code: Optional[int] = 200) -> Optional[Dict[str, Any]]:
        """
        Scan a given URL and its response body to identify login surfaces.
        Returns a finding dictionary if detected, otherwise None.
        """
        if status_code and status_code >= 400:
            return None

        analysis = cls.analyze_html_content(html_body or "", url=url)
        
        if analysis["is_login_page"] or (analysis["has_auth_endpoint"] and status_code == 200):
            return {
                "title": "Exposed Login Page / Authentication Surface Detected",
                "type": "informational",
                "severity": "info",
                "url": url,
                "description": f"Exposed authentication surface detected at {url}. " + "; ".join(analysis["indicators"]),
                "indicators": analysis["indicators"],
                "confidence": analysis["confidence"],
                "has_password_field": analysis["has_password_field"],
            }
        return None
