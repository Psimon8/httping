import os
import streamlit as st
import requests
import schedule
import time
from threading import Thread

def check_url(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        return str(e)

def update_status(urls, status_dict):
    for url in urls:
        status_dict[url] = check_url(url)

def periodic_check(urls, status_dict):
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    st.title("URL Monitor")

    urls = st.text_area("Enter URLs (one per line)", height=200).split("\n")
    urls = [url.strip() for url in urls if url.strip()]

    status_dict = {url: "Not Checked" for url in urls}

    st.subheader("URL Status")
    for url, status in status_dict.items():
        st.write(f"{url}: {status}")

    schedule.every(5).minutes.do(update_status, urls, status_dict)

    checker_thread = Thread(target=periodic_check, args=(urls, status_dict))
    checker_thread.start()

    if st.button("Check Now"):
        update_status(urls, status_dict)
        st.experimental_rerun()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8501))
    st._is_running_with_streamlit = True
    from streamlit.web import cli as stcli
    sys.argv = ["streamlit", "run", "--server.port", str(port), "url_monitor.py"]
    sys.exit(stcli.main())
