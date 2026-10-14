import os
import traceback

from groq import Groq

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from .models import Lecture
from .credit_services import (
    consume_credit,
    refund_credit,
    InsufficientCredits,
)
from .permissions import HasPremiumSubscription, HasTestingAccess


# ============================================================
# AUDIO UPLOAD
# ============================================================
@csrf_exempt
@api_view(["POST"])
@permission_classes([
    IsAuthenticated,
    HasTestingAccess
])
def upload_audio(request):

    lecture = None

    try:
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

        # Save the upload so we have a stable lecture ID.
        lecture = Lecture.objects.create(
            user=request.user,
            title=title,
            audio_file=audio_file,
            status="processing"
        )

        # One audio credit per lecture transcription.
        usage_key = f"audio:lecture:{lecture.id}:usage"

        try:
            consume_credit(
                user=request.user,
                feature="audio",
                idempotency_key=usage_key,
            )

        except InsufficientCredits:
            # Remove the uploaded file and database record.
            if lecture.audio_file:
                lecture.audio_file.delete(save=False)

            lecture.delete()

            return JsonResponse(
                {
                    "error": (
                        "You have no audio credits remaining. "
                        "Please purchase a package to continue."
                    ),
                    "code": "insufficient_audio_credits",
                },
                status=402
            )

        # Begin transcription.
        process_audio(lecture.id)

        # process_audio currently runs synchronously.
        # It may have completed or failed by the time it returns.
        lecture.refresh_from_db()

        if lecture.status == "failed":
            return JsonResponse(
                {
                    "error": "Audio transcription failed.",
                    "lecture_id": lecture.id,
                    "status": lecture.status,
                },
                status=500
            )

        return JsonResponse(
            {
                "message": "Audio transcription processed.",
                "lecture_id": lecture.id,
                "title": lecture.title,
                "status": lecture.status,
            },
            status=200
        )

    except Exception as e:

        print("UPLOAD ERROR:", str(e))
        traceback.print_exc()

        return JsonResponse(
            {"error": "Audio upload failed."},
            status=500
        )
        
        
def refund_failed_audio(lecture, reason):
    """
    Refund the audio credit for a failed transcription.
    Repeated calls will not refund the same operation twice.
    """

    usage_key = f"audio:lecture:{lecture.id}:usage"
    refund_key = f"audio:lecture:{lecture.id}:refund"

    try:
        refund_credit(
            user=lecture.user,
            feature="audio",
            usage_idempotency_key=usage_key,
            refund_idempotency_key=refund_key,
            description=reason,
        )

        print(
            f"Audio credit refund processed for "
            f"Lecture {lecture.id}"
        )

    except Exception as e:
        print(
            f"Audio credit refund failed for "
            f"Lecture {lecture.id}: {e}"
        )

        traceback.print_exc()
        
        
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

            refund_failed_audio(
                lecture,
                "Audio transcription failed: missing Groq API key."
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
            
            refund_failed_audio(
                lecture,
                "Audio transcription failed: audio file missing."
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
            
            refund_failed_audio(
                lecture,
                "Audio transcription failed: empty transcript."
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
            
            refund_failed_audio(
                lecture,
                "Audio transcription failed because of a processing error."
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