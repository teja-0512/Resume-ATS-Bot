from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL


class ResumeAI:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def compare_resumes(self, resume1, resume2):

        prompt = f"""
You are an expert ATS Resume Reviewer and Career Coach.

Compare the following two resumes.

Resume 1:
{resume1}

----------------------------------------

Resume 2:
{resume2}

----------------------------------------

Provide your response in the following format.

🏆 Better Resume:
Mention whether Resume 1 or Resume 2 is better.

📊 ATS Comparison:
Give ATS score out of 100 for both resumes.

✅ Strengths of Resume 1

❌ Weaknesses of Resume 1

💡 Improvements for Resume 1

----------------------------------------

✅ Strengths of Resume 2

❌ Weaknesses of Resume 2

💡 Improvements for Resume 2

----------------------------------------

📌 Missing Skills

Mention important technologies or keywords missing from each resume.

----------------------------------------

🎯 Final Verdict

Explain in detail why one resume is better than the other.

Be professional and ATS-focused.
"""

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional ATS Resume Reviewer "
                        "and HR Hiring Expert."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.4,
            max_tokens=1800
        )

        return response.choices[0].message.content

    def review_resume(self, resume):

        prompt = f"""
You are an ATS Resume Expert.

Review this resume.

Resume:

{resume}

Provide:

1. ATS Score (/100)

2. Strengths

3. Weaknesses

4. Missing Skills

5. Grammar Suggestions

6. Formatting Suggestions

7. ATS Improvement Tips

8. Final Verdict
"""

        response = self.client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an ATS Resume Reviewer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )

        return response.choices[0].message.content