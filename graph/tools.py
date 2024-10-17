from typing import Literal, Optional
from langchain_core.tools import tool

from job import Job
from resume import Resume

def process_job() -> Job:
    ''' process job'''
    job = Job.mock()
    return job

def process_resume() ->Resume:
    ''' process resume'''
    resume = Resume.mock()
    return resume

@tool
def get_job(field: Optional[Literal['title','company','location','salary','description', 'responsibilities']]):
    '''get the job data '''
    job = process_job()
    return getattr(job,field, None)
