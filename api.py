import requests

from logger import logger


class CheckInAPI:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.LOGIN = "https://linkedmatrix.resourceinn.com/api/v1/oauth/webLogin"
        self.CHECKIN = "https://linkedmatrix.resourceinn.com/api/v1/directives/markAttendance"
        self.access_token = ""
        self.cookies = {}

    def login(self):
        headers = {
            "sec-ch-ua-platform": '"Linux"',
            "Referer": "https://linkedmatrix.resourceinn.com/",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "Version-Code": "417",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Version-No": "4.1.7"
        }

        data = {
            "email": self.username,
            "password": self.password
        }

        res = requests.post(self.LOGIN, headers=headers, data=data, timeout=10)
        logger.info("Login for %s: %d", self.username, res.status_code)
        if res.status_code != 200:
            raise RuntimeError("Login failed")

        self.access_token = res.json().get("data").get("access_token")
        self.cookies = res.cookies.get_dict()  # {'laravel_session': 'P1AqDqbULorKaKUzq54i1vkLYp4ba1tGJsPxZzl7'}

    def checkin(self):
        self.login()
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en-US,en;q=0.9",
            "authorization": self.access_token,
            "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryLlz6sJ56J5TaAiKJ",
            "cookie": f"laravel_session={self.cookies.get('laravel_session')}",
            "origin": "https://linkedmatrix.resourceinn.com",
            "priority": "u=1, i",
            "referer": "https://linkedmatrix.resourceinn.com/",
            "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "version-code": "417",
            "version-no": "4.1.7",
        }

        data = """------WebKitFormBoundaryLlz6sJ56J5TaAiKJ
Content-Disposition: form-data; name="mark_attendance"

{"mark_checkin": true}

------WebKitFormBoundaryLlz6sJ56J5TaAiKJ--
"""

        res = requests.post(self.CHECKIN, headers=headers, data=data, timeout=10)
        logger.info("Check-in for %s: %d", self.username, res.status_code)
        if res.status_code == 200 and 'data' in res.json():
            return "Success"
        return "Failed"
