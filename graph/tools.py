from typing import Optional, Literal
from langchain_core.tools import tool

from job import Job
from resume import Resume

def process_job() -> Job:
    """Process job data."""
    job = Job.mock()
    print('job processed')
    return job

def process_resume() -> Resume:
    """Process resume data."""
    resume = Resume.mock()
    print('resume processed')
    return resume

@tool
def get_job(field: Optional[Literal['title', 'company', 'location', 'salary', 'description', 'responsibilities', 'benefits', 'employment_type', 'posted_date']] = None) -> str:
    """Get job data."""
    print('get job tool used')
    job = process_job()
    if field:
        return getattr(job, field)
    return job.dict()

@tool
def get_resume(field: Optional[Literal['name', 'professional_summary', 'work_experience', 'education', 'skills']] = None) -> str:
    """Get resume data."""
    print('get resume tool used')
    resume = process_resume()
    if field:
        return getattr(resume, field)
    return resume.dict()