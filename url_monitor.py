import os
import sys
import streamlit as st
import requests
import schedule
import time
from threading import Thread

# Check HTTP response code
def check_url(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.RequestException as e:
        return str(e)

# Update the status of all URLs
def update_status(urls, status_dict):
    for url in urls:
        status_dict[url] = check_url(url)

# Periodic check in a separate thread
def periodic_check(urls, status_dict):
    while True:
        schedule.run_pending()
        time.sleep(1)

# Streamlit UI
def main():
    st.title("URL Monitor")

    # Load URL list
    urls = st.text_area("Enter URLs (one per line)", height=200).split("\n")
    urls = [url.strip() for url in urls if url.strip()]

    # Status dictionary
    status_dict = {url: "Not Checked" for url in urls}

    # Display current status
    st.subheader("URL Status")
    for url, status in status_dict.items():
        st.write(f"{url}: {status}")

    # Schedule the update every 5 minutes
    schedule.every(5).minutes.do(update_status, urls, status_dict)

    # Start periodic check in a separate thread
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
