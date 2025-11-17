import requests
from bs4 import BeautifulSoup

def scrape_url():
    url = "https://www.tilda.com/faqs/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/121.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    res = requests.get(url, headers=headers)
    if res.status_code != 200:
        raise Exception(f"Failed to fetch page: {res.status_code}")

    soup = BeautifulSoup(res.text, "html.parser")

    # เลือก container หลัก
    container = soup.select_one("div.container--small.container--no-pad.faqs-list")
    if not container:
        raise Exception("Cannot find FAQ container. Structure may have changed.")

    faq_data = []
    current_section = None

    for element in container.children:

        # ถ้าเจอ H3 → หัวข้อหมวด
        if element.name == "h3":
            current_section = element.get_text(strip=True)

        # ถ้าเจอ FAQ item
        if element.name == "div" and element.get("class") and "faq" in element.get("class"):
            question = element.select_one(".faq__question").get_text(strip=True)
            answer_el = element.select_one(".faq__answer .user-content")

            answer = answer_el.get_text(" ", strip=True) if answer_el else ""

            faq_data.append({
                "section": current_section,
                "question": question,
                "answer": answer
            })

    return faq_data
