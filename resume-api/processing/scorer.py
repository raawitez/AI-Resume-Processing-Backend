from loguru import logger


# ── Scoring Configuration ─────────────────────────────────
# Weights must add up to 100

SCORING_CONFIG = {

    "technical_skills": {
        "weight": 40,        # 40 points maximum
        "keywords": [
            # Languages
            "python", "java", "javascript", "typescript",
            "go", "rust", "c++", "c#", "kotlin", "swift",
            # Frameworks
            "fastapi", "django", "flask", "spring", "react",
            "angular", "vue", "express", "nodejs",
            # Databases
            "postgresql", "mysql", "mongodb", "redis",
            "elasticsearch", "sqlite", "dynamodb",
            # DevOps/Cloud
            "docker", "kubernetes", "aws", "gcp", "azure",
            "terraform", "ci/cd", "jenkins", "github actions",
            # Concepts
            "rest api", "graphql", "microservices", "kafka",
            "rabbitmq", "celery", "redis", "sql", "nosql",
            "machine learning", "deep learning", "nlp",
        ]
    },

    "resume_structure": {
        "weight": 30,        # 30 points maximum
        "keywords": [
            "experience",
            "education",
            "skills",
            "projects",
            "summary", "objective",
            "certifications", "certification",
            "achievements", "accomplishments",
            "publications",
            "languages",
        ]
    },

    "action_verbs": {
        "weight": 20,        # 20 points maximum
        "keywords": [
            "built", "developed", "designed", "implemented",
            "created", "architected", "led", "managed",
            "optimised", "improved", "reduced", "increased",
            "deployed", "automated", "integrated", "migrated",
            "launched", "delivered", "collaborated", "mentored",
            "maintained", "refactored", "scaled", "monitored",
        ]
    },

    "contact_info": {
        "weight": 10,        # 10 points maximum
        "keywords": [
            "@",             # email contains @
            "phone", "mobile", "tel", "+91", "+1",
            "linkedin", "github", "portfolio",
            "github.com", "linkedin.com",
        ]
    }
}


def score_resume(text: str) -> dict:
    """
    Score resume text across four categories.

    Returns dict with:
    - total_score: float (0-100)
    - breakdown: dict of category scores
    - keywords_found: list of matched keywords
    - feedback: list of improvement suggestions

    HOW SCORING WORKS:
    For each category:
    - Count how many keywords are found in text
    - Score = (found/total) * weight
    - Capped at the category weight

    Example:
    Technical: 10 keywords found out of 40 defined
    Score = (10/40) * 40 = 10 points out of 40 max
    """
    logger.info("[SCORER] Starting resume scoring")

    text_lower = text.lower()

    breakdown      = {}
    keywords_found = []
    total_score    = 0.0

    for category, config in SCORING_CONFIG.items():
        weight   = config["weight"]
        keywords = config["keywords"]

        found = [kw for kw in keywords if kw.lower() in text_lower]

      
        if len(keywords) > 0:
            raw_score      = (len(found) / len(keywords)) * weight
            category_score = min(round(raw_score, 2), weight)
        else:
            category_score = 0.0

        breakdown[category] = {
            "score":         category_score,
            "max_score":     weight,
            "keywords_found": found,
            "total_keywords": len(keywords)
        }

        keywords_found.extend(found)
        total_score += category_score

        logger.debug(
            f"[SCORER] {category}: "
            f"{category_score}/{weight} "
            f"({len(found)} keywords found)"
        )

    total_score = round(min(total_score, 100.0), 2)

    feedback = _generate_feedback(breakdown)

    result = {
        "total_score":    total_score,
        "breakdown":      breakdown,
        "keywords_found": list(set(keywords_found)),  # deduplicate
        "feedback":       feedback,
        "grade":          _score_to_grade(total_score)
    }

    logger.info(
        f"[SCORER] Score: {total_score}/100 "
        f"Grade: {result['grade']}"
    )

    return result


def _score_to_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 85: return "A"
    if score >= 70: return "B"
    if score >= 55: return "C"
    if score >= 40: return "D"
    return "F"


def _generate_feedback(breakdown: dict) -> list:
    feedback = []

    tech = breakdown.get("technical_skills", {})
    if tech.get("score", 0) < tech.get("max_score", 40) * 0.5:
        feedback.append(
            "Add more technical skills — "
            "include programming languages, frameworks, "
            "databases, and tools you've used"
        )

    structure = breakdown.get("resume_structure", {})
    if structure.get("score", 0) < structure.get("max_score", 30) * 0.5:
        feedback.append(
            "Improve resume structure — "
            "ensure you have clear sections: "
            "Experience, Education, Skills, Projects"
        )

    verbs = breakdown.get("action_verbs", {})
    if verbs.get("score", 0) < verbs.get("max_score", 20) * 0.5:
        feedback.append(
            "Use stronger action verbs — "
            "start bullet points with: Built, Developed, "
            "Designed, Implemented, Led, Optimised"
        )

    contact = breakdown.get("contact_info", {})
    if contact.get("score", 0) < contact.get("max_score", 10) * 0.5:
        feedback.append(
            "Add contact information — "
            "include email, phone, LinkedIn, and GitHub"
        )

    if not feedback:
        feedback.append(
            "Strong resume! "
            "Consider tailoring keywords to specific job descriptions."
        )

    return feedback