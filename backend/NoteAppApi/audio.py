import os
import traceback

from groq import Groq

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Lecture
from .permissions import HasPremiumSubscription


# ============================================================
# AUDIO UPLOAD
# ============================================================

@csrf_exempt
@api_view(["POST"])
@permission_classes([
    IsAuthenticated,
    HasPremiumSubscription
])
def upload_audio(request):

    try:
        print("USER:", request.user)
        print("AUTH:", request.user.is_authenticated)

        audio_file = request.FILES.get("audio")
        title = request.data.get("title", "").strip()

        if not audio_file:
            return JsonResponse(
                {"error": "No audio file"},
                status=400
            )

        MAX_AUDIO_SIZE = 50 * 1024 * 1024

        if audio_file.size > MAX_AUDIO_SIZE:
            return JsonResponse(
                {
                    "error": (
                        "Audio file is too large. "
                        "Maximum allowed size is 50 MB."
                    )
                },
                status=400
            )

        lecture = Lecture.objects.create(
            user=request.user,
            title=title,
            audio_file=audio_file,
            status="processing"
        )

        print(
            f"🎧 Audio upload saved. Lecture ID: {lecture.id}"
        )

        process_audio(lecture.id)

        return JsonResponse(
            {
                "message": "Processing started",
                "lecture_id": lecture.id,
                "title": lecture.title,
            },
            status=202
        )

    except Exception as e:

        print("❌ UPLOAD ERROR:", str(e))
        traceback.print_exc()

        return JsonResponse(
            {"error": str(e)},
            status=500
        )


# ============================================================
# AUDIO PROCESSING / TRANSCRIPTION
# ============================================================

def process_audio(lecture_id):

    file_path = None

    try:

        lecture = Lecture.objects.get(
            id=lecture_id
        )

        file_path = lecture.audio_file.path

        print(
            f"🎧 Starting audio processing "
            f"for Lecture {lecture_id}"
        )

        # ----------------------------------------------------
        # GROQ API KEY
        # ----------------------------------------------------

        api_key = os.getenv(
            "GROQ_API_KEY",
            ""
        ).strip()

        if not api_key:

            print("❌ GROQ_API_KEY is missing")

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return

        # ----------------------------------------------------
        # CHECK FILE
        # ----------------------------------------------------

        if not os.path.exists(file_path):

            print(
                "❌ Audio file does not exist:",
                file_path
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return

        # ----------------------------------------------------
        # GROQ CLIENT
        # ----------------------------------------------------

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        print(
            "🎙️ Transcribing audio with "
            "Whisper Large V3 Turbo..."
        )

        # ----------------------------------------------------
        # TRANSCRIPTION
        # ----------------------------------------------------

        with open(file_path, "rb") as audio:

            transcription = (
                client.audio.transcriptions.create(
                    file=audio,
                    model="whisper-large-v3-turbo",
                    response_format="json",
                    temperature=0.0,
                )
            )

        transcript_text = (
            transcription.text or ""
        ).strip()

        # ----------------------------------------------------
        # EMPTY TRANSCRIPT
        # ----------------------------------------------------

        if not transcript_text:

            print(
                "❌ Groq returned an empty transcript"
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

            return

        print(
            "✅ Audio transcription completed"
        )

        print(
            "Transcript length:",
            len(transcript_text),
            "characters"
        )

        # ----------------------------------------------------
        # SAVE TRANSCRIPT
        # ----------------------------------------------------

        lecture.transcript = transcript_text

        lecture.status = "completed"

        lecture.save(
            update_fields=[
                "transcript",
                "status"
            ]
        )

        print(
            f"✅ Audio processing completed "
            f"for Lecture {lecture_id}"
        )

        # ----------------------------------------------------
        # DELETE TEMPORARY AUDIO FILE
        # ----------------------------------------------------

        if os.path.exists(file_path):

            os.remove(file_path)

            print(
                "🗑️ Audio file deleted successfully"
            )

    except Exception as e:

        print(
            "❌ Audio processing error:",
            repr(e)
        )

        traceback.print_exc()

        try:

            lecture = Lecture.objects.get(
                id=lecture_id
            )

            lecture.status = "failed"

            lecture.save(
                update_fields=["status"]
            )

        except Exception:

            pass


# ============================================================
# AUDIO STATUS
# ============================================================

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def lecture_status(request, id):

    try:

        lecture = Lecture.objects.get(
            id=id,
            user=request.user,
            is_deleted=False
        )

        return JsonResponse(
            {
                "id": lecture.id,
                "status": lecture.status,
                "transcript": lecture.transcript,
            }
        )

    except Lecture.DoesNotExist:

        return JsonResponse(
            {"error": "Not found"},
            status=404
        )


# ============================================================
# GENERATE LECTURE NOTES FROM TRANSCRIPT
# ============================================================

def generate_lecture_note(transcript):

    if not transcript:

        print(
            "❌ Cannot generate lecture notes "
            "without transcript"
        )

        return None

    api_key = os.getenv(
        "GROQ_API_KEY",
        ""
    ).strip()

    if not api_key:

        print(
            "❌ GROQ_API_KEY is missing"
        )

        return None

    try:

        client = Groq(
            api_key=api_key,
            max_retries=0
        )

        prompt = f"""
You are the SmartNotes Lecture Notes Generator.

Your task is to transform the transcript below into
clear, detailed, well-structured lecture notes.

The transcript may contain transcription errors.
Correct obvious transcription mistakes where the
intended meaning is clear.

Your notes should:

- Preserve the important information from the transcript.
- Explain important concepts clearly.
- Include definitions where appropriate.
- Include examples when they are discussed.
- Explain processes or stages clearly.
- Include comparisons where relevant.
- Follow a logical structure.
- Do not invent information that is not supported by
  the transcript.
- Do not use Markdown tables.
- End with a useful conclusion.
- If appropriate, include a "Further Reading" section
  based only on topics actually discussed.

Transcript:

{transcript}
"""

        for attempt in range(2):

            try:

                print(
                    f"🧠 Generating lecture notes "
                    f"(attempt {attempt + 1}/2)..."
                )

                response = client.chat.completions.create(
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

                notes = (
                    response.choices[0]
                    .message.content
                    .strip()
                )

                if notes:

                    print(
                        "✅ Lecture notes generated"
                    )

                    if response.usage:

                        print(
                            "Token usage:",
                            response.usage
                        )

                    return notes

                print(
                    "❌ Model returned empty notes"
                )

            except Exception as e:

                print(
                    f"❌ Lecture generation attempt "
                    f"{attempt + 1} failed:",
                    repr(e)
                )

                traceback.print_exc()

                if attempt == 0:

                    import time

                    time.sleep(2)

        return None

    except Exception as e:

        print(
            "❌ Lecture generation error:",
            repr(e)
        )

        traceback.print_exc()

        return None