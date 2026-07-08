from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(160), default="")
    role: Mapped[str] = mapped_column(String(40), default="candidate")
    display_name: Mapped[str] = mapped_column(String(120), default="")
    email: Mapped[str] = mapped_column(String(160), default="")
    phone: Mapped[str] = mapped_column(String(40), default="")
    organization: Mapped[str] = mapped_column(String(160), default="")
    status: Mapped[str] = mapped_column(String(40), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    token: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    real_name: Mapped[str] = mapped_column(String(80), default="")
    education: Mapped[str] = mapped_column(String(120), default="")
    major: Mapped[str] = mapped_column(String(120), default="")
    school: Mapped[str] = mapped_column(String(160), default="")
    target_role: Mapped[str] = mapped_column(String(160), default="")
    city: Mapped[str] = mapped_column(String(80), default="")
    expected_salary: Mapped[str] = mapped_column(String(80), default="")
    avatar_url: Mapped[str] = mapped_column(Text, default="")
    skills: Mapped[str] = mapped_column(Text, default="[]")
    certificates: Mapped[str] = mapped_column(Text, default="[]")
    projects: Mapped[str] = mapped_column(Text, default="[]")
    internships: Mapped[str] = mapped_column(Text, default="[]")
    awards: Mapped[str] = mapped_column(Text, default="[]")
    self_summary: Mapped[str] = mapped_column(Text, default="")
    completeness: Mapped[float] = mapped_column(Float, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_name: Mapped[str] = mapped_column(String(120), index=True)
    data_type: Mapped[str] = mapped_column(String(60))
    domain: Mapped[str] = mapped_column(String(80))
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    data_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_rate: Mapped[float] = mapped_column(Float, default=0)
    noise_rate: Mapped[float] = mapped_column(Float, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(40), default="processed")


class RawJD(Base):
    __tablename__ = "raw_jds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    source_id: Mapped[int | None] = mapped_column(ForeignKey("data_sources.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    content: Mapped[str] = mapped_column(Text)
    text_hash: Mapped[str] = mapped_column(String(64), index=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ParsedJD(Base):
    __tablename__ = "parsed_jds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    raw_jd_id: Mapped[int | None] = mapped_column(ForeignKey("raw_jds.id"), nullable=True)
    job_name: Mapped[str] = mapped_column(String(160), index=True)
    domain: Mapped[str] = mapped_column(String(80))
    level: Mapped[str] = mapped_column(String(40))
    responsibilities: Mapped[str] = mapped_column(Text)
    required_skills: Mapped[str] = mapped_column(Text)
    preferred_skills: Mapped[str] = mapped_column(Text)
    tools: Mapped[str] = mapped_column(Text)
    certificates: Mapped[str] = mapped_column(Text)
    experience: Mapped[str] = mapped_column(String(120))
    scenarios: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    evidence: Mapped[str] = mapped_column(Text)


class JobEntity(Base):
    __tablename__ = "job_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    domain: Mapped[str] = mapped_column(String(80))
    job_type: Mapped[str] = mapped_column(String(80))
    level: Mapped[str] = mapped_column(String(40))
    description: Mapped[str] = mapped_column(Text)
    is_emerging: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(40), default="active")
    version: Mapped[str] = mapped_column(String(20), default="v1.0")
    evidence: Mapped[str] = mapped_column(Text)

    skill_relations = relationship("JobSkillRelation", back_populates="job")


class SkillEntity(Base):
    __tablename__ = "skill_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(80))
    description: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)


class JobSkillRelation(Base):
    __tablename__ = "job_skill_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_entities.id"))
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill_entities.id"))
    relation_type: Mapped[str] = mapped_column(String(40), default="requires")
    weight: Mapped[float] = mapped_column(Float, default=1)
    evidence: Mapped[str] = mapped_column(Text)

    job = relationship("JobEntity", back_populates="skill_relations")
    skill = relationship("SkillEntity")


class EvolutionEvent(Base):
    __tablename__ = "evolution_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("job_entities.id"))
    added_skills: Mapped[str] = mapped_column(Text)
    removed_skills: Mapped[str] = mapped_column(Text)
    modified_skills: Mapped[str] = mapped_column(Text)
    update_note: Mapped[str] = mapped_column(Text)
    data_sources: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    version_record: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    education: Mapped[str] = mapped_column(String(120))
    major: Mapped[str] = mapped_column(String(120))
    school: Mapped[str] = mapped_column(String(160))
    projects: Mapped[str] = mapped_column(Text)
    internships: Mapped[str] = mapped_column(Text)
    certificates: Mapped[str] = mapped_column(Text)
    competitions: Mapped[str] = mapped_column(Text)
    intention: Mapped[str] = mapped_column(String(160))
    raw_text: Mapped[str] = mapped_column(Text)


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    skill_name: Mapped[str] = mapped_column(String(120))
    level: Mapped[str] = mapped_column(String(40))
    evidence: Mapped[str] = mapped_column(Text)


class MatchReport(Base):
    __tablename__ = "match_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("job_entities.id"))
    total_score: Mapped[float] = mapped_column(Float)
    required_skill_score: Mapped[float] = mapped_column(Float)
    preferred_skill_score: Mapped[float] = mapped_column(Float)
    project_score: Mapped[float] = mapped_column(Float)
    tool_score: Mapped[float] = mapped_column(Float)
    scenario_score: Mapped[float] = mapped_column(Float)
    certificate_score: Mapped[float] = mapped_column(Float)
    missing_skills: Mapped[str] = mapped_column(Text)
    suggestions: Mapped[str] = mapped_column(Text)
    evidence: Mapped[str] = mapped_column(Text)


class ReviewTask(Base):
    __tablename__ = "review_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    task_type: Mapped[str] = mapped_column(String(60))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0)
    evidence: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    case_type: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(160))
    expected: Mapped[str] = mapped_column(Text)
    actual: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean, default=True)
