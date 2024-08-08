import streamlit as st
import requests
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
        update_status(urls, status_dict)
        time.sleep(300)  # Sleep for 5 minutes

def main():
    st.title("URL Monitor")

    urls = st.text_area("Enter URLs (one per line)", height=200).split("\n")
    urls = [url.strip() for url in urls if url.strip()]

    status_dict = {url: "Not Checked" for url in urls}

    st.subheader("URL Status")
    for url, status in status_dict.items():
        st.write(f"{url}: {status}")

    if st.button("Start Monitoring"):
        checker_thread = Thread(target=periodic_check, args=(urls, status_dict))
        checker_thread.start()
        st.write("Monitoring started.")

    if st.button("Check Now"):
        update_status(urls, status_dict)
        st.experimental_rerun()

if __name__ == "__main__":
    main()
