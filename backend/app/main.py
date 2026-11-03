import datetime as dt

from fastapi import FastAPI, HTTPException

from app import planner
from app.models import DayUpdate, Plan, PlanRequest, TaskUpdate
from app.problems import PROBLEMS, Problem, ProblemSummary
from app.store import InMemoryStore


def create_app(llm=None, store=None, today_fn=dt.date.today) -> FastAPI:
    app = FastAPI(title="OnTarget API")
    store = store if store is not None else InMemoryStore()

    @app.post("/plans", response_model=Plan, status_code=201)
    def create_plan(req: PlanRequest):
        today = today_fn()
        if req.interview_date <= today:
            raise HTTPException(status_code=422, detail="interview_date must be in the future")
        plan = planner.create_plan(req.company, req.interview_date, today, llm)
        store.save(plan)
        return plan

    @app.get("/plans/{plan_id}", response_model=Plan)
    def get_plan(plan_id: str):
        return _load(plan_id)

    @app.patch("/plans/{plan_id}/tasks/{task_id}", response_model=Plan)
    def update_task(plan_id: str, task_id: str, body: TaskUpdate):
        plan = _load(plan_id)
        for day in plan.days:
            for task in day.tasks:
                if task.id == task_id:
                    task.done = body.done
                    store.save(plan)
                    return plan
        raise HTTPException(status_code=404, detail="Task not found")

    @app.patch("/plans/{plan_id}/days/{day_number}", response_model=Plan)
    def update_day(plan_id: str, day_number: int, body: DayUpdate):
        plan = _load(plan_id)
        for day in plan.days:
            if day.number == day_number:
                day.skipped = body.skipped
                store.save(plan)
                return plan
        raise HTTPException(status_code=404, detail="Day not found")

    def _load(plan_id: str) -> Plan:
        plan = store.get(plan_id)
        if plan is None:
            raise HTTPException(status_code=404, detail="Plan not found")
        return plan

    @app.get("/problems", response_model=list[ProblemSummary])
    def list_problems():
        return list(PROBLEMS.values())

    @app.get("/problems/{problem_id}", response_model=Problem)
    def get_problem(problem_id: str):
        problem = PROBLEMS.get(problem_id)
        if problem is None:
            raise HTTPException(status_code=404, detail="Problem not found")
        return problem

    return app
