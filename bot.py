import os
import logging
import asyncio

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import BOT_TOKEN, UPLOAD_FOLDER
from parser import ResumeParser
from compare import ATSAnalyzer

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

analyzer = ATSAnalyzer()

# ======================================
# Conversation States
# ======================================

WAITING_FOR_ROLE = "waiting_for_role"
WAITING_FOR_RESUME1 = "waiting_for_resume1"
WAITING_FOR_RESUME2 = "waiting_for_resume2"


# ======================================
# /start
# ======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    await update.message.reply_text(
        "👋 Welcome to ATS Resume Analyzer\n\n"
        "This bot analyzes resumes based on the Job Role.\n\n"
        "Use /compare to begin."
    )


# ======================================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "Commands\n\n"
        "/start - Start Bot\n"
        "/compare - Analyze Resumes\n"
        "/cgpa - Show CGPA of last analyzed resumes (if available)\n"
        "/help - Help"
    )


# ======================================
# /compare
# ======================================

async def compare(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data.clear()

    context.user_data["state"] = WAITING_FOR_ROLE

    await update.message.reply_text(
        "💼 Enter the Job Role.\n\n"
        "Example:\n"
        "Python Full Stack Developer"
    )


# ======================================
# Handle Text Messages
# ======================================

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE):

    state = context.user_data.get("state")

    if state == WAITING_FOR_ROLE:

        context.user_data["job_role"] = update.message.text.strip()

        context.user_data["state"] = WAITING_FOR_RESUME1

        await update.message.reply_text(
            "✅ Job Role Saved.\n\n"
            "📄 Please upload Resume."
        )

        return

    else:
        # Allow users to ask natural-language CGPA/GPA queries like
        # "who has highest cgpa" or "who has higher gpa" anywhere in chat.
        text = (update.message.text or "").lower()

        # Natural-language CGPA/GPA questions
        if ("cgpa" in text or "gpa" in text) and (
            "who" in text or "higher" in text or "highest" in text
        ):
            await cgpa_command(update, context)
            return

        # Natural-language comparisons for education/projects/experience
        if any(k in text for k in ["education", "projects", "experience"]):
            if any(q in text for q in ["who", "which", "higher", "more", "best"]):
                if "education" in text:
                    await compare_sections_command(update, context, "education")
                    return
                if "projects" in text or "project" in text:
                    await compare_sections_command(update, context, "projects")
                    return
                if "experience" in text:
                    await compare_sections_command(update, context, "experience")
                    return
        # Skills comparison
        if "skills" in text and any(q in text for q in ["who", "which", "better", "best", "higher"]):
            await compare_skills_command(update, context)
            return

        await update.message.reply_text(
            "Please use /compare to start the resume analysis flow."
        )

        return


async def cgpa_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show CGPA comparison from the last analysis if available."""
    last = context.user_data.get("last_result")

    if not last:
        await update.message.reply_text(
            "No recent analysis found. Run /compare and upload resumes first."
        )
        return

    r1 = last.get("result1", {})
    r2 = last.get("result2", {})
    cgpa_raw1 = r1.get("cgpa_raw")
    cgpa_raw2 = r2.get("cgpa_raw")
    cgpa_score1 = r1.get("cgpa_score")
    cgpa_score2 = r2.get("cgpa_score")

    if not cgpa_raw1 and not cgpa_raw2:
        await update.message.reply_text("CGPA not found in either resume.")
        return

    msg = []
    msg.append("📚 CGPA Comparison:")
    msg.append(f"Resume 1: {cgpa_raw1 if cgpa_raw1 else 'N/A'}")
    msg.append(f"Resume 2: {cgpa_raw2 if cgpa_raw2 else 'N/A'}")

    # Compare using numeric scores when available
    if cgpa_score1 is not None and cgpa_score2 is not None:
        if cgpa_score1 > cgpa_score2:
            msg.append("🏅 Higher CGPA: Resume 1")
        elif cgpa_score2 > cgpa_score1:
            msg.append("🏅 Higher CGPA: Resume 2")
        else:
            msg.append("🏅 Both resumes have the same CGPA")
    else:
        msg.append("(Comparison unavailable if numeric CGPA not found in both resumes)")

    reply_to = context.user_data.get('last_bot_message_id')
    await update.message.reply_text("\n".join(msg), reply_to_message_id=reply_to)


async def compare_sections_command(update: Update, context: ContextTypes.DEFAULT_TYPE, attribute: str = None):
    """Compare `education`, `projects`, or `experience` between last analyzed resumes."""
    last = context.user_data.get("last_result")

    if not last:
        await update.message.reply_text(
            "No recent analysis found. Run /compare and upload resumes first."
        )
        return

    sections1 = last.get("sections1", {})
    sections2 = last.get("sections2", {})

    attr = (attribute or "").lower()

    if attr not in ["education", "projects", "experience"]:
        await update.message.reply_text("I can compare `education`, `projects`, or `experience`.")
        return

    s1 = sections1.get(attr, "").strip()
    s2 = sections2.get(attr, "").strip()

    # Fallback: if sections empty, try to use analyzer scores
    result1 = last.get("result1", {})
    result2 = last.get("result2", {})

    if attr == "education":
        score1 = result1.get("scores", {}).get("Education")
        score2 = result2.get("scores", {}).get("Education")
    elif attr == "experience":
        score1 = result1.get("scores", {}).get("Experience")
        score2 = result2.get("scores", {}).get("Experience")
    else:
        # For projects, approximate by counting non-empty lines in the section
        score1 = len([l for l in s1.splitlines() if l.strip()])
        score2 = len([l for l in s2.splitlines() if l.strip()])

    # Build reply with sections/content
    parts = [f"📊 Comparison: {attr.title()}"]
    parts.append("\n-- Resume 1 --\n" + (s1 if s1 else "(No section found)"))
    parts.append("\n-- Resume 2 --\n" + (s2 if s2 else "(No section found)"))

    # Determine winner
    winner_text = ""
    try:
        if score1 is not None and score2 is not None:
            if isinstance(score1, (int, float)) and isinstance(score2, (int, float)):
                if score1 > score2:
                    winner_text = f"\n🏅 Higher {attr.title()}: Resume 1"
                elif score2 > score1:
                    winner_text = f"\n🏅 Higher {attr.title()}: Resume 2"
                else:
                    winner_text = f"\n🏅 Both resumes similar for {attr.title()}"
    except Exception:
        winner_text = "\n(Unable to compare numerically)"

    parts.append(winner_text)

    reply_to = context.user_data.get("last_bot_message_id")
    await update.message.reply_text("\n".join(parts), reply_to_message_id=reply_to)


async def compare_skills_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Compare skills between last analyzed resumes and report winner."""
    last = context.user_data.get("last_result")

    if not last:
        await update.message.reply_text(
            "No recent analysis found. Run /compare and upload resumes first."
        )
        return

    r1 = last.get("result1", {})
    r2 = last.get("result2", {})

    matched1 = set(r1.get("matched_skills", []))
    matched2 = set(r2.get("matched_skills", []))

    score1 = r1.get("scores", {}).get("Skills")
    score2 = r2.get("scores", {}).get("Skills")

    only1 = sorted(list(matched1 - matched2))
    only2 = sorted(list(matched2 - matched1))
    common = sorted(list(matched1 & matched2))

    parts = ["📌 Skills Comparison:"]
    parts.append("\n-- Resume 1 --")
    parts.append("Matched Skills: " + (", ".join(sorted(matched1)) if matched1 else "None"))
    parts.append("Skills Score: " + (f"{score1}%" if score1 is not None else "N/A"))

    parts.append("\n-- Resume 2 --")
    parts.append("Matched Skills: " + (", ".join(sorted(matched2)) if matched2 else "None"))
    parts.append("Skills Score: " + (f"{score2}%" if score2 is not None else "N/A"))

    parts.append("\nCommon Skills: " + (", ".join(common) if common else "None"))
    parts.append("Skills only in Resume 1: " + (", ".join(only1) if only1 else "None"))
    parts.append("Skills only in Resume 2: " + (", ".join(only2) if only2 else "None"))

    # Decide winner
    winner_text = ""
    try:
        if score1 is not None and score2 is not None:
            if score1 > score2:
                winner_text = "\n🏅 Resume 1 has stronger skills"
            elif score2 > score1:
                winner_text = "\n🏅 Resume 2 has stronger skills"
            else:
                winner_text = "\n🏅 Both resumes have similar skill strength"
    except Exception:
        winner_text = "\n(Unable to determine winner by numeric score)"

    parts.append(winner_text)

    reply_to = context.user_data.get("last_bot_message_id")
    await update.message.reply_text("\n".join(parts), reply_to_message_id=reply_to)


# ======================================
# Handle Resume Uploads
# ======================================

async def receive_resume(update: Update, context: ContextTypes.DEFAULT_TYPE):

    state = context.user_data.get("state")

    if state not in [WAITING_FOR_RESUME1, WAITING_FOR_RESUME2]:
        await update.message.reply_text(
            "Please start with /compare."
        )
        return

    # Support single or multiple document uploads in one message
    docs = []
    if getattr(update.message, "document", None):
        docs.append(update.message.document)
    if getattr(update.message, "documents", None):
        docs.extend(update.message.documents)

    if not docs:
        return

    parsed_texts = []

    media_group_id = getattr(update.message, "media_group_id", None)

    for document in docs:
        filename = document.file_name.lower() if document.file_name else ""

        if not (filename.endswith(".pdf") or filename.endswith(".docx")):
            await update.message.reply_text(
                "❌ Only PDF and DOCX files are supported."
            )
            return

        telegram_file = await document.get_file()

        save_path = os.path.join(
            UPLOAD_FOLDER,
            f"{update.effective_user.id}_{document.file_name}"
        )

        await telegram_file.download_to_drive(save_path)

        resume_text = ResumeParser.extract_text(save_path)

        try:
            os.remove(save_path)
        except Exception:
            pass

        parsed_texts.append(resume_text)

    # If this message is part of a media group, accumulate and wait briefly
    if media_group_id:
        key = f"mg_{media_group_id}_{update.effective_user.id}"
        bucket = context.user_data.get(key, [])
        bucket.extend(parsed_texts)
        context.user_data[key] = bucket

        # wait a bit to allow other parts of the media group to arrive
        await asyncio.sleep(1.0)

        collected = context.user_data.pop(key, [])

        # continue processing using collected list
        parsed_texts = collected

    # -----------------------------
    # Resume handling (support 1 or 2 files in one message)
    # -----------------------------

    if state == WAITING_FOR_RESUME1:

        # If user uploaded two files at once, process both
        if len(parsed_texts) >= 2:
            context.user_data["resume1"] = parsed_texts[0]
            context.user_data["resume2"] = parsed_texts[1]

            await update.message.reply_text(
                "✅ 2 files uploaded.\n\n"
                "⏳ Analyzing... Please wait."
            )

            job_role = context.user_data.get("job_role")

            result1 = analyzer.analyze_resume(
                job_role,
                context.user_data["resume1"]
            )

            result2 = analyzer.analyze_resume(
                job_role,
                context.user_data["resume2"]
            )

        else:
            # Single file: save as resume1 and ask for resume2
            context.user_data["resume1"] = parsed_texts[0]

            context.user_data["state"] = WAITING_FOR_RESUME2

            await update.message.reply_text(
                "✅ Resumes uploaded successfully.\n\n"
            )

            return

    # -----------------------------
    # Resume 2
    # -----------------------------

    if state == WAITING_FOR_RESUME2:

        # Use the first document if multiple were sent
        context.user_data["resume2"] = parsed_texts[0]

        await update.message.reply_text(
            "⏳ Analyzing resumes against the Job Role...\n\n"
            "Please wait..."
        )

        job_role = context.user_data.get("job_role")

        result1 = analyzer.analyze_resume(
            job_role,
            context.user_data["resume1"]
        )

        result2 = analyzer.analyze_resume(
            job_role,
            context.user_data["resume2"]
        )

        if result1["overall_score"] > result2["overall_score"]:
            winner = "Resume 1"

        elif result2["overall_score"] > result1["overall_score"]:
            winner = "Resume 2"

        else:
            winner = "Tie"

        context.user_data["result1"] = result1
        context.user_data["result2"] = result2
        context.user_data["winner"] = winner
                # ======================================
        # Preserve last analysis so user can ask CGPA later
        # store parsed sections so later comparisons (education/projects/etc.) work
        sections1 = ResumeParser.get_resume_sections(context.user_data.get("resume1", ""))
        sections2 = ResumeParser.get_resume_sections(context.user_data.get("resume2", ""))

        context.user_data["last_result"] = {
            "job_role": job_role,
            "result1": result1,
            "result2": result2,
            "winner": winner,
            "sections1": sections1,
            "sections2": sections2,
        }

        # remove temporary keys but keep last_result
        for k in ["state", "resume1", "resume2", "result1", "result2", "winner", "job_role"]:
            context.user_data.pop(k, None)

        # ======================================
        # Generate Chat Report
        # ======================================

        resume1_suggestions = "\n• ".join(result1["suggestions"])
        resume1_strengths = "\n• ".join(result1["strengths"])
        resume1_weaknesses = "\n• ".join(result1["weaknesses"])

        resume2_suggestions = "\n• ".join(result2["suggestions"])
        resume2_strengths = "\n• ".join(result2["strengths"])
        resume2_weaknesses = "\n• ".join(result2["weaknesses"])

        report_1 = f"""
🤖 ATS RESUME ANALYSIS

💼 Job Role: {job_role}

📄 RESUME 1
• Overall Match: {result1['overall_score']}%
• Skills: {result1['scores']['Skills']}%
• Experience: {result1['scores']['Experience']}%
• Education: {result1['scores']['Education']}%
• Formatting: {result1['scores']['Formatting']}%
• Grammar: {result1['scores']['Grammar']}%

✅ Matching Skills: {', '.join(result1['matched_skills']) if result1['matched_skills'] else 'None'}
❌ Missing Skills: {', '.join(result1['missing_skills']) if result1['missing_skills'] else 'None'}

💪 Strengths:
• {resume1_strengths}

⚠ Weaknesses:
• {resume1_weaknesses}

💡 Suggestions:
• {resume1_suggestions}

⭐ Recommendation:
{result1['recommendation']}
"""

        report_2 = f"""
📄 RESUME 2
• Overall Match: {result2['overall_score']}%
• Skills: {result2['scores']['Skills']}%
• Experience: {result2['scores']['Experience']}%
• Education: {result2['scores']['Education']}%
• Formatting: {result2['scores']['Formatting']}%
• Grammar: {result2['scores']['Grammar']}%

✅ Matching Skills: {', '.join(result2['matched_skills']) if result2['matched_skills'] else 'None'}
❌ Missing Skills: {', '.join(result2['missing_skills']) if result2['missing_skills'] else 'None'}

💪 Strengths:
• {resume2_strengths}

⚠ Weaknesses:
• {resume2_weaknesses}

💡 Suggestions:
• {resume2_suggestions}

⭐ Recommendation:
{result2['recommendation']}
"""

        summary = f"""
🏆 BEST CANDIDATE: {winner}

Resume 1 Match: {result1['overall_score']}%
Resume 2 Match: {result2['overall_score']}%
"""

        last_msg = None
        for message in [report_1, report_2, summary]:
            for i in range(0, len(message), 4000):
                last_msg = await update.message.reply_text(message[i:i + 4000])

        # store last bot message id so /cgpa can reply to it
        if last_msg:
            context.user_data['last_bot_message_id'] = last_msg.message_id

            # keep last_result in user_data (already set above)
            # Note: do NOT send an automatic CGPA hint; user will invoke /cgpa manually.


# ======================================
# Main
# ======================================

def main():

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("compare", compare))
    application.add_handler(CommandHandler("cgpa", cgpa_command))

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            receive_text,
        )
    )

    application.add_handler(
        MessageHandler(
            filters.Document.ALL,
            receive_resume,
        )
    )

    logger.info("ATS Resume Analyzer Started...")

    application.run_polling()


if __name__ == "__main__":
    main()