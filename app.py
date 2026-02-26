import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi

def extract_transcript(video_id):

    try:

        ytt_api = YouTubeTranscriptApi()
        
        fetched_transcript = ytt_api.fetch(video_id)
        transcript_text = " \n".join([snippet.text for snippet in fetched_transcript])
        return transcript_text
    
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return "Error extracting transcript"

def main():
    st.title("YouTube Video Transcript Extractor")
    url = st.text_input("Enter the YouTube video URL:")

    if url:
        video_id = url.split("&")[0].split("=")[1]
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg") #, use_column_width=True)

    if st.button("Extract Transcript"):   
        transcript_text = extract_transcript(video_id)
        st.text_area("Transcript", value=transcript_text, height=400)

if __name__ == "__main__":
    main()