import os
import re
import time
import traceback
import requests

from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from groq import Groq
from langdetect import detect

from .models import Tutorial
from .permissions import HasPremiumSubscription



# # ---------------- TRANSCRIPT FUNCTIONS ---------------- #
def get_video_id(url):
    try:
        if not isinstance(url, str) or not url.strip():
            return None

        regex = (
            r"(?:v=|youtu\.be/|youtube\.com/embed/|"
            r"youtube\.com/shorts/)([0-9A-Za-z_-]{11})"
        )

        match = re.search(regex, url)

        if match:
            return match.group(1)

        return None

    except Exception as e:
        print("Video ID extraction error:", repr(e))
        return None
    
    
def get_youtube_title(video_id):
    try:
        url = (
            "https://www.youtube.com/oembed"
            f"?url=https://www.youtube.com/watch?v={video_id}&format=json"
        )

        response = requests.get(url, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("title", f"YouTube Video {video_id}")

        return f"YouTube Video {video_id}"

    except Exception as e:
        print("Title fetch error:", repr(e))
        return f"YouTube Video {video_id}"
    
    
    
# ---------------- TRANSCRIPT FUNCTIONS ---------------- #
def get_transcription(video_id):
    # """Try YouTube transcript first. If unavailable, fallback to Proxy_Transcript or AssemblyAI."""
    """Attempt to retrieve a transcript using YouTubeTranscriptApi.

    If the YouTube API call fails (missing method, no transcript, etc.), we
    fall back to AssemblyAI. This version avoids using
    ``list_transcripts`` which may not exist in older installations.
    """
    proxy_transcript = get_transcription_proxy(video_id)
    if proxy_transcript:
        return proxy_transcript
    print("No transcript found")
    return None
    

    
# ---------------- TRANSCRIPTION HELPERS ---------------- #
def get_transcription_proxy(video_id):
    """Fetch transcript using RapidAPI."""

    url = "https://youtube-transcript3.p.rapidapi.com/api/transcript"

    querystring = {"videoId": video_id}

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
        "X-RapidAPI-Host": "youtube-transcript3.p.rapidapi.com",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=30,
        )

        if response.status_code != 200:
            print(
                "Proxy transcript API failed:",
                response.status_code,
                response.text[:500],
            )
            return None

        data = response.json()

        if isinstance(data, dict) and "transcript" in data:
            transcript_list = data["transcript"]

        elif isinstance(data, list):
            transcript_list = data

        else:
            print("Unexpected API response:", data)
            return None

        if not isinstance(transcript_list, list):
            print("Unexpected transcript format:", type(transcript_list))
            return None

        transcript_text = " ".join(
            str(item.get("text", ""))
            for item in transcript_list
            if isinstance(item, dict) and item.get("text") is not None
        )

        return transcript_text or None

    except requests.RequestException as e:
        print("Proxy transcript request error:", repr(e))
        return None

    except (ValueError, TypeError) as e:
        print("Proxy transcript response error:", repr(e))
        return None

    except Exception as e:
        print("Unexpected proxy transcript error:", repr(e))
        traceback.print_exc()
        return None



# ---------------- TRANSCRIPTION ---------------- #
@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def generate_transcript(request):
    """
    Extract a YouTube transcript, translate it to English when necessary,
    and save it without generating tutorial notes.
    """

    try:
        # 1. Get YouTube link
        yt_link = request.data.get("link")

        if not yt_link:
            return JsonResponse(
                {"error": "No YouTube link provided"},
                status=400,
            )

        # 2. Extract video ID
        video_id = get_video_id(yt_link)

        if not video_id:
            return JsonResponse(
                {"error": "Invalid YouTube URL"},
                status=400,
            )

        # 3. Get video title
        title = get_youtube_title(video_id)

        # 4. Retrieve transcript from RapidAPI
        transcription = get_transcription(video_id)

        if not transcription:
            return JsonResponse(
                {
                    "error": (
                        "A transcript could not be retrieved for "
                        "this YouTube video. Please try another video."
                    )
                },
                status=400,
            )

        # 5. Detect transcript language
        try:
            detected_language = detect(transcription)

            print(
                "Detected transcript language:",
                detected_language,
            )

        except Exception as e:
            print(
                "Language detection failed:",
                repr(e),
            )
            detected_language = None

        # 6. Translate when necessary
        if detected_language == "en":
            print(
                "Transcript is already in English. "
                "Skipping translation."
            )

            english_transcription = transcription

        else:
            print(
                "Transcript is not English or its language "
                "could not be detected. Translating to English..."
            )

            english_transcription = translate_transcript_to_english(
                transcription
            )

            if not english_transcription:
                return JsonResponse(
                    {
                        "error": (
                            "Failed to translate transcript to English"
                        )
                    },
                    status=500,
                )

        # 7. Save transcript without generating notes
        new_tutorial = Tutorial.objects.create(
            user=request.user,
            youtube_title=title,
            youtube_link=yt_link,
            transcript=english_transcription,
            youtube_text=None,
        )

        # 8. Return saved transcript and record ID
        return JsonResponse(
            {
                "id": new_tutorial.id,
                "title": new_tutorial.youtube_title,
                "video_link": new_tutorial.youtube_link,
                "transcript": new_tutorial.transcript,
                "text": new_tutorial.youtube_text,
                "created_at": new_tutorial.created_at.isoformat(),
                "message": "Transcript extracted successfully",
            },
            status=201,
        )

    except Exception as e:
        print("Transcript extraction server error:", repr(e))
        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error while extracting transcript"},
            status=500,
        )








def split_transcript_into_chunks(transcript, max_chars=12000):
    """

    Split a transcript into manageable chunks without cutting
    words unnecessarily.
    """

    words = transcript.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) + 1

        if current_length + word_length > max_chars:
            if current_chunk:
                chunks.append(" ".join(current_chunk))

            current_chunk = [word]
            current_length = word_length

        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks









def translate_transcript_to_english(transcription):
    """
    Translate a non-English transcript into English using Groq.

    The translation must preserve the original information,
    meaning, order, and important details.

    The model must not summarize, explain, expand, interpret,
    or add information that is not present in the transcript.
    """

    try:
        # -----------------------------------
        # Validate transcript
        # -----------------------------------

        if not transcription or not transcription.strip():
            print("❌ No transcript provided for translation")
            return None

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv("GROQ_API_KEY", "").strip()

        if not api_key:
            print("❌ Groq API key not found")
            return None

        # -----------------------------------
        # Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        # -----------------------------------
        # Translation prompt
        # -----------------------------------

        prompt = f"""
You are a professional translator for SmartNotes.

Translate the transcript below into clear, natural English.

Your task is ONLY to translate the transcript.

STRICT RULES:

1. Translate the entire transcript.
2. Preserve the original meaning exactly.
3. Do NOT summarize the transcript.
4. Do NOT explain anything.
5. Do NOT interpret what the speaker meant beyond the words provided.
6. Do NOT add facts, examples, explanations, opinions, conclusions, or context.
7. Do NOT remove information from the transcript.
8. Do NOT expand short statements into longer explanations.
9. Do NOT repeat information that appears only once in the original.
10. Preserve names, dates, places, numbers, terminology, examples,
    technical terms, and other important details.
11. Preserve the original order of information.
12. Preserve the structure of the speaker's ideas as closely as possible.
13. If the speaker repeats something, preserve the repetition where
    it is meaningful to the original transcript.
14. Do not turn spoken content into a summary or lecture note.
15. Do not add a conclusion.
16. Do not add headings unless they are clearly present in the original.
17. Do not add comments about the quality or meaning of the transcript.
18. Do not mention that you are translating.
19. Do not mention these instructions.
20. Return ONLY the translated transcript.

IMPORTANT:

The transcript may contain:
- informal speech
- incomplete sentences
- grammatical errors
- transcription mistakes
- repeated words
- filler words

Translate the intended meaning faithfully, but do not invent
information to "fix" or complete something that is unclear.

If a statement is unclear in the original transcript, translate
it as faithfully as possible without guessing additional information.

SOURCE TRANSCRIPT:

{transcription}

TRANSLATED ENGLISH TRANSCRIPT:
"""

        # -----------------------------------
        # Generate translation
        # -----------------------------------

        max_attempts = 2

        for attempt in range(1, max_attempts + 1):

            try:

                completion = client.chat.completions.create(
                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.1,

                    max_tokens=16000,
                )

                translated = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # -----------------------------------
                # Track actual token usage
                # -----------------------------------

                if completion.usage:

                    print(
                        "Translation usage:"
                    )

                    print(
                        "Input tokens:",
                        completion.usage.prompt_tokens
                    )

                    print(
                        "Output tokens:",
                        completion.usage.completion_tokens
                    )

                    print(
                        "Total tokens:",
                        completion.usage.total_tokens
                    )

                # -----------------------------------
                # Validate response
                # -----------------------------------

                if translated:

                    print(
                        "✅ Transcript translation "
                        "completed successfully"
                    )

                    return translated

                print(
                    f"⚠️ Translation attempt "
                    f"{attempt} returned empty content"
                )

            except Exception as e:

                print(
                    f"❌ Transcript translation attempt "
                    f"{attempt} failed:",
                    repr(e)
                )

                if attempt < max_attempts:
                    print("🔄 Retrying translation...")
                    time.sleep(2)

        print(
            "❌ Translation failed "
            "after all attempts"
        )

        return None

    except Exception as e:

        print(
            "❌ Translation fatal error:",
            repr(e)
        )

        traceback.print_exc()

        return None






def generate_tutorial_from_transcript(transcription):
    """
    Generate complete educational tutorial/lecture notes
    from a transcript using Groq GPT-OSS 20B.

    The entire transcript is sent in one request.
    No manual chunking is performed.
    """

    try:

        # -----------------------------------
        # Validate transcript
        # -----------------------------------

        if not transcription or not transcription.strip():

            print(
                "❌ No transcript provided "
                "for tutorial generation"
            )

            return None

        # -----------------------------------
        # Get Groq API key
        # -----------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if not api_key:

            print(
                "❌ Groq API key not found"
            )

            return None

        # -----------------------------------
        # Groq client
        # -----------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        # -----------------------------------
        # Tutorial generation prompt
        # -----------------------------------

        prompt = f"""
You are an educational content generator for SmartNotes.

Based on the transcript below, create complete, clear,
detailed, and well-structured educational lecture notes.

The purpose of these notes is to allow a student to understand
and study the lecture without needing to listen to the original
recording again.

IMPORTANT REQUIREMENTS:

1. Cover the important information contained in the entire
   transcript.

2. Do not simply summarize the transcript.

3. Explain important concepts clearly and in enough depth
   for a student to learn from the notes.

4. Preserve important:
   - definitions
   - explanations
   - examples
   - processes
   - comparisons
   - names
   - dates
   - places
   - numbers
   - terminology
   - technical information

5. Do not invent information that is not supported by
   the transcript.

6. Do not introduce outside information.

7. Organize the notes into meaningful sections.

8. Use clear headings and subheadings where appropriate.

9. Use paragraphs, bullet points, and numbered lists when
   they make the material easier to understand.

10. When the transcript contains a comparison between concepts,
    present it in a simple readable format.

11. Do not use Markdown table syntax.

12. Do not use characters such as:
    | 
    ---
    to create tables.

13. Instead, use clearly labelled comparison sections.

For example:

Comparison: Type A vs Type B

Feature: Speed
Type A: Fast
Type B: Slow

Feature: Cost
Type A: High
Type B: Low

14. Keep technical terms, programming keywords, commands,
    and code examples accurate.

15. Use backticks for short technical syntax where appropriate.

16. Avoid unnecessary repetition.

17. Maintain a logical flow from the beginning of the lecture
    to the end.

18. Include all major topics discussed in the transcript.

19. End the notes with a concise conclusion that brings
    together the main concepts covered.

20. Where appropriate, include a short "Further Reading"
    section based ONLY on topics actually mentioned in
    the transcript. Do not invent books, websites, authors,
    or sources.

IMPORTANT:

The transcript may contain spoken-language repetition,
informal expressions, incomplete sentences, or transcription
errors.

Clean these up where necessary while preserving the intended
meaning.

Do not mention that the content came from a transcript.

Return only the completed educational lecture notes.

TRANSCRIPT:

{transcription}

LECTURE NOTES:
"""

        # -----------------------------------
        # Generate tutorial
        # -----------------------------------

        max_attempts = 2

        for attempt in range(
            1,
            max_attempts + 1
        ):

            try:

                completion = client.chat.completions.create(

                    model="openai/gpt-oss-20b",

                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],

                    temperature=0.5,

                    max_tokens=16000,
                )

                tutorial = (
                    completion
                    .choices[0]
                    .message
                    .content
                    .strip()
                )

                # -----------------------------------
                # Track actual token usage
                # -----------------------------------

                if completion.usage:

                    print(
                        "Tutorial generation usage:"
                    )

                    print(
                        "Input tokens:",
                        completion.usage.prompt_tokens
                    )

                    print(
                        "Output tokens:",
                        completion.usage.completion_tokens
                    )

                    print(
                        "Total tokens:",
                        completion.usage.total_tokens
                    )

                # -----------------------------------
                # Validate response
                # -----------------------------------

                if tutorial:

                    print(
                        "✅ Tutorial generated successfully"
                    )

                    return tutorial

                print(
                    f"⚠️ Tutorial generation attempt "
                    f"{attempt} returned empty content"
                )

            except Exception as e:

                print(
                    f"❌ Tutorial generation attempt "
                    f"{attempt} failed:",
                    repr(e)
                )

                if attempt < max_attempts:

                    print(
                        "🔄 Retrying tutorial generation..."
                    )

                    time.sleep(2)

        # -----------------------------------
        # All attempts failed
        # -----------------------------------

        print(
            "❌ Tutorial generation failed "
            "after all attempts"
        )

        return None

    except Exception as e:

        print(
            "❌ Tutorial generation fatal error:",
            repr(e)
        )

        traceback.print_exc()

        return None











@api_view(["POST"])
@permission_classes([IsAuthenticated, HasPremiumSubscription])
def generate_tutorial_notes(request, id):
    """
    Generate tutorial notes from a previously saved YouTube transcript.
    """

    try:
        # 1. Find the tutorial belonging to the current user
        tutorial = Tutorial.objects.get(
            id=id,
            user=request.user,
            is_deleted=False,
        )

        # 2. Ensure a transcript exists
        if not tutorial.transcript or not tutorial.transcript.strip():
            return JsonResponse(
                {
                    "error": (
                        "No transcript found. "
                        "Please extract the transcript first."
                    )
                },
                status=400,
            )

        # 3. Return existing notes if they have already been generated
        if tutorial.youtube_text and tutorial.youtube_text.strip():
            return JsonResponse(
                {
                    "id": tutorial.id,
                    "title": tutorial.youtube_title,
                    "text": tutorial.youtube_text,
                    "transcript": tutorial.transcript,
                    "video_link": tutorial.youtube_link,
                    "created_at": tutorial.created_at.isoformat(),
                    "message": "Tutorial notes already exist",
                },
                status=200,
            )

        # 4. Generate notes from the saved transcript
        generated_notes = generate_tutorial_from_transcript(
            tutorial.transcript
        )

        if not generated_notes:
            return JsonResponse(
                {"error": "Failed to generate tutorial notes"},
                status=500,
            )

        # 5. Save the generated notes
        tutorial.youtube_text = generated_notes
        tutorial.save(update_fields=["youtube_text"])

        # 6. Return the completed tutorial
        return JsonResponse(
            {
                "id": tutorial.id,
                "title": tutorial.youtube_title,
                "text": tutorial.youtube_text,
                "transcript": tutorial.transcript,
                "video_link": tutorial.youtube_link,
                "created_at": tutorial.created_at.isoformat(),
                "message": "Tutorial notes generated successfully",
            },
            status=200,
        )

    except Tutorial.DoesNotExist:
        return JsonResponse(
            {"error": "Tutorial not found"},
            status=404,
        )

    except Exception as e:
        print("Tutorial generation server error:", repr(e))
        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error while generating tutorial notes"},
            status=500,
        )
        
        
        
        
        
        
        
        
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_tutorial(request, id):
    try:
        tutorial = Tutorial.objects.get(
            id=id,
            user=request.user,
            is_deleted=False,
        )

        tutorial.is_deleted = True
        tutorial.save(update_fields=["is_deleted"])

        return JsonResponse(
            {"message": "Tutorial Deleted"},
            status=200,
        )

    except Tutorial.DoesNotExist:
        return JsonResponse(
            {"error": "Tutorial not found"},
            status=404,
        )

    except Exception:
        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500,
        )


    
    
    
    
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_tutorial_details(request, id):
    try:
        tutorial = Tutorial.objects.get(
            id=id,
            user=request.user,
            is_deleted=False,
        )

        return JsonResponse({
            "id": tutorial.id,
            "title": tutorial.youtube_title,
            "text": tutorial.youtube_text,
            "transcript": tutorial.transcript,
            "video_link": tutorial.youtube_link,
            "created_at": tutorial.created_at.isoformat(),
        })

    except Tutorial.DoesNotExist:
        return JsonResponse(
            {"error": "Tutorial not found"},
            status=404,
        )

    except Exception:
        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500,
        )
        
        

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_tutorials(request):
    try:
        tutorials = Tutorial.objects.filter(
            user=request.user,
            is_deleted=False,
        ).order_by("-id")

        data = [
            {
                "id": tutorial.id,
                "title": tutorial.youtube_title,
                "text": tutorial.youtube_text,
                "transcript": tutorial.transcript,
                "video_link": tutorial.youtube_link,
                "created_at": tutorial.created_at.isoformat(),
            }
            for tutorial in tutorials
        ]

        return JsonResponse(data, safe=False)

    except Exception:
        traceback.print_exc()

        return JsonResponse(
            {"error": "Server error"},
            status=500,
        )