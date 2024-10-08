import os
import streamlit as st
import requests
import schedule
import time
import pandas as pd
import altair as alt
from threading import Thread, Event
from datetime import datetime

# Set Streamlit page configuration
st.set_page_config(page_title="URL Monitor", layout="wide", page_icon="🥕")

# User agents
USER_AGENTS = {
    "Chrome": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "GoogleBot": "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}

# Data storage
response_times = {"Chrome": [], "GoogleBot": []}
monitor_threads = {}

# Check HTTP response code and response time
def check_url(url, user_agent):
    headers = {"User-Agent": user_agent}
    try:
        start_time = time.time()
        response = requests.get(url, headers=headers, timeout=5)
        response_time = (time.time() - start_time) * 1000  # Convert to ms
        return response.status_code, response_time
    except requests.RequestException as e:
        return str(e), None

# Update the status of all URLs
def update_status(urls, status_dict, response_times):
    for url in urls:
        chrome_status, chrome_time = check_url(url, USER_AGENTS["Chrome"])
        googlebot_status, googlebot_time = check_url(url, USER_AGENTS["GoogleBot"])
        status_dict[url] = {
            "Chrome": chrome_status,
            "GoogleBot": googlebot_status
        }
        response_times["Chrome"].append({"time": datetime.now(), "response_time": chrome_time})
        response_times["GoogleBot"].append({"time": datetime.now(), "response_time": googlebot_time})

# Periodic check in a separate thread
def periodic_check(url, status_dict, response_times, stop_event):
    while not stop_event.is_set():
        update_status([url], status_dict, response_times)
        time.sleep(300)  # Check every 5 minutes

# Initialize session state
if 'monitoring' not in st.session_state:
    st.session_state.monitoring = {}

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

    if st.button("Start Monitoring"):
        for url in urls:
            if url not in st.session_state.monitoring:
                stop_event = Event()
                thread = Thread(target=periodic_check, args=(url, status_dict, response_times, stop_event))
                thread.daemon = True
                thread.start()
                st.session_state.monitoring[url] = stop_event
        st.success("Monitoring started.")

    active_monitoring = list(st.session_state.monitoring.keys())
    if active_monitoring:
        selected_monitor = st.selectbox("Select URL to stop monitoring", active_monitoring)
        if st.button("Stop Monitoring for Selected URL"):
            stop_event = st.session_state.monitoring.pop(selected_monitor, None)
            if stop_event:
                stop_event.set()
                st.success(f"Monitoring stopped for {selected_monitor}")

    if st.button("Check Now"):
        update_status(urls, status_dict, response_times)
        display_status()

    # Initial display
    display_status()

    # Display response time graphs
    st.subheader("Response Time Graphs")

    if response_times["Chrome"]:
        df_chrome = pd.DataFrame(response_times["Chrome"])
        chart_chrome = alt.Chart(df_chrome).mark_line().encode(
            x='time:T',
            y='response_time:Q'
        ).properties(title='Chrome Response Time')
        st.altair_chart(chart_chrome, use_container_width=True)

    if response_times["GoogleBot"]:
        df_googlebot = pd.DataFrame(response_times["GoogleBot"])
        chart_googlebot = alt.Chart(df_googlebot).mark_line().encode(
            x='time:T',
            y='response_time:Q'
        ).properties(title='GoogleBot Response Time')
        st.altair_chart(chart_googlebot, use_container_width=True)

if __name__ == "__main__":
    main()
