import re


class ATSAnalyzer:

    def __init__(self):

        self.common_skills = [
            "python", "java", "c", "c++", "javascript",
            "typescript", "html", "css",
            "react", "angular", "vue",
            "node", "express", "django", "flask",
            "spring", "spring boot",
            "sql", "mysql", "postgresql", "mongodb",
            "firebase", "oracle",
            "aws", "azure", "gcp",
            "docker", "kubernetes",
            "git", "github",
            "linux",
            "rest api", "graphql",
            "machine learning",
            "deep learning",
            "tensorflow",
            "pytorch",
            "opencv",
            "pandas",
            "numpy",
            "power bi",
            "tableau"
        ]

    # =====================================
    # Extract skills from job role
    # =====================================

    def extract_required_skills(self, job_role):

        text = job_role.lower()

        skills = []

        for skill in self.common_skills:

            if skill in text:
                skills.append(skill)

        return list(set(skills))

    # =====================================
    # Match Skills
    # =====================================

    def match_skills(self, required_skills, resume):

        resume = resume.lower()

        matched = []
        missing = []

        for skill in required_skills:

            if skill in resume:
                matched.append(skill)
            else:
                missing.append(skill)

        return matched, missing

    # =====================================
    # Skill Match Score
    # =====================================

    def skill_score(self, matched, required):

        if len(required) == 0:
            return 100

        return round((len(matched) / len(required)) * 100)

    # =====================================
    # Experience Score
    # =====================================

    def experience_score(self, resume, job_role=None):

        resume = resume.lower()

        resume_years = re.findall(r"(\d+)\+?\s*years", resume)

        if resume_years:

            candidate = int(resume_years[0])

            if candidate >= 5:
                return 100

            return round((candidate / 5) * 100)

        keywords = [
            "intern",
            "internship",
            "experience",
            "developer",
            "software engineer",
            "worked",
            "company",
            "employee"
        ]

        count = 0

        for word in keywords:

            if word in resume:
                count += 1

        return min(count * 15, 100)

    # =====================================
    # Education Score
    # =====================================

    def education_score(self, resume):

        resume = resume.lower()

        keywords = [
            "b.tech",
            "btech",
            "computer science",
            "engineering",
            "master",
            "m.tech",
            "cgpa",
            "university",
            "college"
        ]

        count = 0

        for word in keywords:

            if word in resume:
                count += 1

        return min(count * 12, 100)

    # =====================================
    # ATS Formatting Score
    # =====================================

    def formatting_score(self, resume):

        resume = resume.lower()

        sections = [
            "summary",
            "skills",
            "projects",
            "experience",
            "education",
            "certifications"
        ]

        score = 0

        for section in sections:

            if section in resume:
                score += 1

        return round((score / len(sections)) * 100)

    # =====================================
    # Grammar Score
    # =====================================

    def grammar_score(self, resume):

        lines = resume.splitlines()

        long_lines = 0

        for line in lines:

            if len(line) > 140:
                long_lines += 1

        return max(100 - long_lines * 10, 60)

    # =====================================
    # Extract CGPA / Percentage
    # =====================================

    def extract_cgpa(self, resume):

        text = resume.lower()

        # Common CGPA patterns: 8.5, cgpa: 8.5/10, 3.6/4.0, 85%
        # Try to find cgpa/gpa explicitly (capture raw string)
        m = re.search(r"(?:cgpa|gpa)[:\s]*([0-9]+\.?[0-9]{0,2})(?:\s*/\s*([0-9]+\.?[0-9]{0,2}))?", text)
        if m:
            try:
                raw = m.group(0).split(':', 1)[-1].strip()
                val = float(m.group(1))
                # compute numeric score on 10-scale
                if m.group(2):
                    den = float(m.group(2))
                    score = round((val / den) * 10, 2) if den > 0 else None
                else:
                    if val <= 4.5:
                        score = round((val / 4.0) * 10, 2)
                    else:
                        score = round(val, 2)
                return raw, score
            except Exception:
                pass

        # Look for patterns like 8.5/10 or 3.6/4.0
        m = re.search(r"([0-9]+\.?[0-9]{0,2})\s*/\s*([0-9]+\.?[0-9]{0,2})", text)
        if m:
            try:
                raw = f"{m.group(1)}/{m.group(2)}"
                num = float(m.group(1))
                den = float(m.group(2))
                if den > 0:
                    score = round((num / den) * 10, 2)
                    return raw, score
            except Exception:
                pass

        # Percentage patterns like 85% -> convert to /10 by dividing by 10
        m = re.search(r"(\d{2,3})\s*%", text)
        if m:
            try:
                raw = f"{m.group(1)}%"
                pct = float(m.group(1))
                score = round((pct / 100) * 10, 2)
                return raw, score
            except Exception:
                pass

        return None, None
            # =====================================
    # Strengths
    # =====================================

    def get_strengths(self, matched_skills, scores):

        strengths = []

        if scores["Skills"] >= 80:
            strengths.append("Excellent match with the required technical skills.")

        if scores["Experience"] >= 80:
            strengths.append("Relevant work experience for this role.")

        if scores["Education"] >= 80:
            strengths.append("Strong educational background.")

        if scores["Formatting"] >= 80:
            strengths.append("ATS-friendly resume structure.")

        if len(matched_skills) >= 5:
            strengths.append("Covers most of the required technologies.")

        if not strengths:
            strengths.append("Resume has potential but needs improvements.")

        return strengths

    # =====================================
    # Weaknesses
    # =====================================

    def get_weaknesses(self, missing_skills, scores):

        weaknesses = []

        if missing_skills:
            weaknesses.append(
                "Missing important skills: " +
                ", ".join(missing_skills)
            )

        if scores["Experience"] < 60:
            weaknesses.append(
                "Relevant work experience could be stronger."
            )

        if scores["Education"] < 60:
            weaknesses.append(
                "Education details need improvement."
            )

        if scores["Formatting"] < 70:
            weaknesses.append(
                "Resume formatting can be improved for ATS systems."
            )

        if scores["Grammar"] < 80:
            weaknesses.append(
                "Grammar and readability need improvement."
            )

        return weaknesses

    # =====================================
    # Suggestions
    # =====================================

    def get_role_based_suggestions(self, job_role, missing_skills):

        suggestions = []

        role_text = job_role.lower()

        if "full stack" in role_text:
            suggestions.append(
                "Emphasize both front-end and back-end experience for a Full Stack role."
            )

        if "backend" in role_text or "backend developer" in role_text:
            suggestions.append(
                "Showcase APIs, database systems, and backend architecture experience."
            )

        if "frontend" in role_text or "frontend developer" in role_text:
            suggestions.append(
                "Highlight UI frameworks, responsive design, and front-end performance."
            )

        if "data" in role_text or "machine learning" in role_text or "ai" in role_text:
            suggestions.append(
                "Include data analysis, modeling, and deployment projects relevant to this role."
            )

        if "devops" in role_text or "site reliability" in role_text or "sre" in role_text:
            suggestions.append(
                "Highlight CI/CD, cloud infrastructure, automation, and monitoring experience."
            )

        if any(x in role_text for x in ["senior", "lead", "manager"]):
            suggestions.append(
                "Emphasize leadership, mentoring, and delivery ownership in the resume."
            )

        if missing_skills:
            suggestions.append(
                "Incorporate the missing role-specific skills wherever possible."
            )

        if not suggestions:
            suggestions.append(
                "Align the resume more closely with the job role to improve match rates."
            )

        return suggestions

    # =====================================
    # Suggestions
    # =====================================

    def get_suggestions(self, job_role, missing_skills, scores):

        suggestions = []

        for skill in missing_skills:
            suggestions.append(
                f"Consider adding experience with {skill} if applicable."
            )

        if scores["Experience"] < 70:
            suggestions.append(
                "Highlight internships, freelance work, or real-world projects."
            )

        if scores["Formatting"] < 80:
            suggestions.append(
                "Use clear headings like Skills, Experience, Projects, and Education."
            )

        if scores["Grammar"] < 90:
            suggestions.append(
                "Proofread the resume to improve grammar and readability."
            )

        suggestions.extend(
            self.get_role_based_suggestions(
                job_role,
                missing_skills,
            )
        )

        if not suggestions:
            suggestions.append(
                "Excellent resume. Only minor improvements are recommended."
            )

        return suggestions

    # =====================================
    # Hiring Recommendation
    # =====================================

    def hiring_recommendation(self, overall):

        if overall >= 90:
            return "★★★★★  Highly Recommended"

        elif overall >= 75:
            return "★★★★☆  Recommended"

        elif overall >= 60:
            return "★★★☆☆  Consider"

        return "★★☆☆☆  Not Recommended"

    # =====================================
    # Analyze Resume
    # =====================================

    def analyze_resume(self, job_role, resume):

        required_skills = self.extract_required_skills(job_role)

        matched_skills, missing_skills = self.match_skills(
            required_skills,
            resume
        )

        skill = self.skill_score(
            matched_skills,
            required_skills
        )

        experience = self.experience_score(
            resume
        )

        education = self.education_score(
            resume
        )

        formatting = self.formatting_score(
            resume
        )

        grammar = self.grammar_score(
            resume
        )

        # Extract CGPA if available (raw string and numeric score)
        cgpa_raw, cgpa_score = self.extract_cgpa(resume)

        overall = round(
            (
                skill * 0.40 +
                experience * 0.25 +
                education * 0.15 +
                formatting * 0.10 +
                grammar * 0.10
            )
        )

        scores = {
            "Overall": overall,
            "Skills": skill,
            "Experience": experience,
            "Education": education,
            "Formatting": formatting,
            "Grammar": grammar
        }

        return {

            "job_role": job_role,

            "overall_score": overall,

            "scores": scores,

            "matched_skills": matched_skills,

            "missing_skills": missing_skills,

            "strengths": self.get_strengths(
                matched_skills,
                scores
            ),

            "weaknesses": self.get_weaknesses(
                missing_skills,
                scores
            ),

            "suggestions": self.get_suggestions(
                job_role,
                missing_skills,
                scores
            ),

            "recommendation": self.hiring_recommendation(
                overall
            ),
            "cgpa_raw": cgpa_raw,
            "cgpa_score": cgpa_score
        }