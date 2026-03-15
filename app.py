import re
import os

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def extract_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        fetched_transcript = ytt_api.fetch(video_id)
        raw_text = " ".join([snippet.text for snippet in fetched_transcript])
        return re.sub(r"\s+", " ", raw_text).strip()
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None


def structure_transcript(raw_transcript):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that structures raw video transcripts. "
                        "Add proper punctuation, capitalization, and split the text into "
                        "clear sentences and paragraphs. Do not change the meaning or words. "
                        "Return only the structured text."
                    ),
                },
                {"role": "user", "content": raw_transcript},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error structuring transcript: {e}")
        return raw_transcript


def summarize_transcript(transcript):
    try:
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an assistant that summarizes video transcripts. "
                        "Write a clear, concise summary in a few paragraphs covering the main points. "
                        "Return only the summary."
                    ),
                },
                {"role": "user", "content": transcript},
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error summarizing transcript: {e}")
        return None


def copy_button(text):
    import html
    safe = html.escape(text)
    st.components.v1.html(
        f"""
        <textarea id="t" style="display:none">{safe}</textarea>
        <button onclick="navigator.clipboard.writeText(document.getElementById('t').value);this.innerText='Copied!';setTimeout(()=>this.innerText='Copy',1500)" style="padding:6px 14px;border:1px solid #ccc;border-radius:6px;background:#f0f2f6;cursor:pointer;font-size:14px;">Copy</button>
        """,
        height=45,
    )


def main():
    st.title("YouTube Video Transcript Extractor")
    url = st.text_input("Enter the YouTube video URL:")

    if url:
        video_id = url.split("&")[0].split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg")

    if st.button("Extract Transcript"):
        with st.spinner("Extracting transcript..."):
            raw = extract_transcript(video_id)
        if raw:
            with st.spinner("Structuring transcript with gpt-4.1-nano..."):
                st.session_state.structured = structure_transcript(raw)
            st.session_state.summary = None

    if "structured" in st.session_state and st.session_state.structured:
        st.subheader("Structured Transcript")
        st.text_area("", value=st.session_state.structured, height=400, key="transcript_area")
        copy_button(st.session_state.structured)

        if st.button("Summarize"):
            with st.spinner("Summarizing with gpt-4.1-nano..."):
                st.session_state.summary = summarize_transcript(st.session_state.structured)

    if "summary" in st.session_state and st.session_state.summary:
        st.subheader("Summary")
        st.text_area("", value=st.session_state.summary, height=250, key="summary_area")
        copy_button(st.session_state.summary)


if __name__ == "__main__":
    main()
