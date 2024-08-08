import os
import streamlit as st
import requests
import schedule
import time
from threading import Thread

# Set Streamlit page configuration
st.set_page_config(page_title="URL Monitor", layout="wide", page_icon="🥕")

# User agents
USER_AGENTS = {
    "Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "GoogleBot": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

# Check HTTP response code
def check_url(url, user_agent):
    headers = {"User-Agent": user_agent}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        return response.status_code
    except requests.RequestException as e:
        return str(e)

# Update the status of all URLs
def update_status(urls, status_dict):
    for url in urls:
        status_dict[url] = {
            "Chrome": check_url(url, USER_AGENTS["Chrome"]),
            "GoogleBot": check_url(url, USER_AGENTS["GoogleBot"])
        }

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
    status_dict = {url: {"Chrome": "Not Checked", "GoogleBot": "Not Checked"} for url in urls}

    # Display current status
    st.subheader("URL Status")
    status_placeholder = st.empty()

    def display_status():
        with status_placeholder.container():
            for url, statuses in status_dict.items():
                st.write(f"{url}:")
                st.write(f"  Chrome: {statuses['Chrome']}")
                st.write(f"  GoogleBot: {statuses['GoogleBot']}")

    # Schedule the update every 5 minutes
    if st.button("Start Monitoring"):
        schedule.every(5).minutes.do(update_status, urls, status_dict)

        # Start periodic check in a separate thread
        checker_thread = Thread(target=periodic_check, args=(urls, status_dict))
        checker_thread.daemon = True
        checker_thread.start()
        st.success("Monitoring started.")

    if st.button("Check Now"):
        update_status(urls, status_dict)
        display_status()

    # Initial display
    display_status()

if __name__ == "__main__":
    main()
