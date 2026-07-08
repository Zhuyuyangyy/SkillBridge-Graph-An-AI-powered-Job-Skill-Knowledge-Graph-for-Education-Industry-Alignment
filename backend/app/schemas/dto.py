from pydantic import BaseModel


class JDParseRequest(BaseModel):
    text: str


class ResumeParseRequest(BaseModel):
    text: str


class MatchAnalysisRequest(BaseModel):
    resume_id: int | None = None
    resume: dict | None = None
    target_job_id: int | None = None
    target_job_name: str | None = None


class AIAnalyzeRequest(BaseModel):
    task_type: str
    payload: dict


class DigitalInterviewRequest(BaseModel):
    job_name: str
    resume_summary: str | None = None
    candidate_answer: str | None = None
    stage: str = "opening"


class RegisterRequest(BaseModel):
    username: str
    password: str
    confirm_password: str
    role: str = "candidate"
    display_name: str = ""
    email: str
    phone: str = ""
    organization: str = ""
    captcha_token: str
    captcha_answer: str


class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str = ""


class AccountUpdateRequest(BaseModel):
    display_name: str | None = None
    email: str | None = None
    phone: str | None = None
    organization: str | None = None


class CandidateProfileUpdateRequest(BaseModel):
    real_name: str = ""
    education: str = ""
    major: str = ""
    school: str = ""
    target_role: str = ""
    city: str = ""
    expected_salary: str = ""
    avatar_url: str = ""
    skills: list[str] = []
    certificates: list[str] = []
    projects: list[str] = []
    internships: list[str] = []
    awards: list[str] = []
    self_summary: str = ""


class ReviewActionResponse(BaseModel):
    id: int
    status: str
    message: str
