import unittest
from unittest.mock import MagicMock
from mantis.utils.login_detector import LoginDetector
from mantis.modules.scan.LoginPageScanner import LoginPageScanner

class TestLoginDetector(unittest.TestCase):

    def test_matches_auth_path(self):
        self.assertTrue(LoginDetector.matches_auth_path("https://example.com/login"))
        self.assertTrue(LoginDetector.matches_auth_path("https://example.com/signin"))
        self.assertTrue(LoginDetector.matches_auth_path("https://example.com/admin/dashboard"))
        self.assertTrue(LoginDetector.matches_auth_path("https://example.com/api/v1/auth"))
        self.assertTrue(LoginDetector.matches_auth_path("https://example.com/oauth/authorize"))
        self.assertFalse(LoginDetector.matches_auth_path("https://example.com/about-us"))
        self.assertFalse(LoginDetector.matches_auth_path("https://example.com/pricing"))

    def test_has_password_field(self):
        html_with_password = """
        <html>
            <body>
                <form action="/login" method="POST">
                    <input type="text" name="username" placeholder="Username" />
                    <input type="password" name="password" placeholder="Password" />
                    <button type="submit">Sign In</button>
                </form>
            </body>
        </html>
        """
        self.assertTrue(LoginDetector.has_password_field(html_with_password))

        html_without_password = """
        <html>
            <body>
                <h1>Welcome to our blog</h1>
                <input type="text" name="search" placeholder="Search..." />
            </body>
        </html>
        """
        self.assertFalse(LoginDetector.has_password_field(html_without_password))

    def test_analyze_html_content(self):
        login_html = """
        <html>
            <head><title>Admin Login</title></head>
            <body>
                <form action="/api/v1/authenticate" method="POST">
                    <label>Email</label>
                    <input type="email" name="email" id="email" />
                    <label>Password</label>
                    <input type="password" name="password" id="password" />
                    <input type="submit" value="Log In" />
                </form>
            </body>
        </html>
        """
        result = LoginDetector.analyze_html_content(login_html, url="https://example.com/admin")
        self.assertTrue(result["is_login_page"])
        self.assertEqual(result["confidence"], "HIGH")
        self.assertTrue(result["has_password_field"])
        self.assertTrue(result["has_auth_form"])
        self.assertTrue(result["has_auth_endpoint"])
        self.assertGreaterEqual(len(result["indicators"]), 3)

    def test_detect_login_surface(self):
        login_html = """
        <form action="/auth/login">
            <input type="password" name="pwd" />
        </form>
        """
        finding = LoginDetector.detect_login_surface("https://app.example.com/login", html_body=login_html, status_code=200)
        self.assertIsNotNone(finding)
        self.assertEqual(finding["title"], "Exposed Login Page / Authentication Surface Detected")
        self.assertEqual(finding["type"], "informational")
        self.assertTrue(finding["has_password_field"])

    def test_login_page_scanner_parse_response(self):
        scanner = LoginPageScanner()
        scanner.org = "test_org"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.url = "https://admin.example.com/login"
        mock_response.text = '<form><input type="password" name="pass"/><button>Log In</button></form>'

        findings = scanner.parse_response(mock_response)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Exposed Login Page / Authentication Surface Detected")
        self.assertEqual(findings[0]["org"], "test_org")
        self.assertEqual(findings[0]["type"], "informational")

if __name__ == "__main__":
    unittest.main()
