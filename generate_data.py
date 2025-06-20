import pandas as pd
import random
from faker import Faker
from datetime import timedelta

# Initialize faker
fake = Faker()

# Set sizes
num_cases = 200
num_billable_entries = 1000
num_tasks = 500

# Cases 
cases = []
for i in range(num_cases):
    start_date = fake.date_between(start_date='-6M', end_date='-2M')
    due_date = fake.date_between(start_date='-2M', end_date='+1M')
    end_date = "" if random.random() > 0.4 else fake.date_between(start_date=due_date, end_date='+1M')
    lawyer = fake.name()
    cases.append({
        "case_id": 1000 + i,
        "client_name": fake.company(),
        "lawyer": lawyer,
        "practice_area": random.choice(["Criminal", "Family", "Corporate", "Civil", "Litigation"]),
        "status": random.choice(["In Progress", "Closed", "Delayed"]),
        "start_date": start_date,
        "due_date": due_date,
        "end_date": end_date
    })

cases_df = pd.DataFrame(cases)
cases_df.to_csv("cases.csv", index=False)


# Billable Hours 
lawyers = [case["lawyer"] for case in cases]
case_ids = [case["case_id"] for case in cases]

billable_hours = []
for i in range(num_billable_entries):
    billable_hours.append({
        "entry_id": i + 1,
        "lawyer": random.choice(lawyers),
        "case_id": random.choice(case_ids),
        "date": fake.date_between(start_date='-2M', end_date='today'),
        "hours_logged": round(random.uniform(1, 8), 1),
        "billed": random.choice(["Yes", "No"])
    })

billable_df = pd.DataFrame(billable_hours)
billable_df.to_csv("billable_hours.csv", index=False)


# Tasks
tasks = []
for i in range(num_tasks):
    tasks.append({
        "task_id": i + 1,
        "case_id": random.choice(case_ids),
        "task_description": fake.sentence(nb_words=6),
        "assigned_to": random.choice(lawyers),
        "due_date": fake.date_between(start_date='-1M', end_date='+2M'),
        "completed": random.choice(["Yes", "No"])
    })

tasks_df = pd.DataFrame(tasks)
tasks_df.to_csv("tasks.csv", index=False)

print("✅ CSV files generated successfully: cases.csv, billable_hours.csv, tasks.csv")
