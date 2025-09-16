from fastapi import FastAPI
import pandas as pd
from fastapi.responses import HTMLResponse

app = FastAPI()

# Load CSVs
courses_df = pd.read_csv("courses.csv")
enrollments_df = pd.read_csv("enrollments.csv")


@app.get("/")
def home():
    return {"message": "Welcome! Use /students, /courses, or /enrollments"}


# 1.getting all data

students_df = pd.read_csv("./students.csv", encoding="utf-8-sig")
students_df.columns = students_df.columns.str.strip()
students_df = students_df.fillna("").astype(str)


@app.get("/students")
def get_students():
    return students_df.to_dict(orient="records")


@app.get("/courses")
def get_courses():
    return courses_df.to_dict(orient="records")


@app.get("/enrollments")
def get_enrollments():
    return enrollments_df.to_dict(orient="records")


# 4. Fetch all students in tabular format


@app.get("/students_table", response_class=HTMLResponse)
def get_students_table():
    html_table = students_df.to_html(index=False)
    return f"""
    <html>
        <head>
            <title>Students Table</title>
        </head>
        <body>
            <h2>Students Data</h2>
            {html_table}
        </body>
    </html>
    """


# 8. Fetch all students enrolled in a particular course (given course_id as input).

students_df["student_id"] = students_df["student_id"].astype(str)
enrollments_df["student_id"] = enrollments_df["student_id"].astype(str)
enrollments_df["course_id"] = enrollments_df["course_id"].astype(str)


@app.get("/students_in_course")
def students_in_course(course_id: str):
    filtered = enrollments_df[enrollments_df["course_id"] == course_id]
    if filtered.empty:
        return {"message": f"No students enrolled in course {course_id}"}
    result = pd.merge(filtered, students_df, on="student_id", how="left")
    return result.to_dict(orient="records")


# 9. Write a program to display students who are not enrolled in any course.


@app.get("/students_not_enrolled")
def students_not_enrolled():
    enrolled_ids = enrollments_df["student_id"].unique()

    not_enrolled = students_df[~students_df["student_id"].isin(enrolled_ids)]

    if not_enrolled.empty:
        return {"message": "All students are enrolled in at least one course."}

    return not_enrolled.to_dict(orient="records")


# 10.Perform an INNER JOIN between students and courses using Python to show student names along with the courses they are enrolled in.

courses_df["course_id"] = courses_df["course_id"].astype(str)


@app.get("/students_courses")
def students_courses():
    try:
        students_df["student_id"] = students_df["student_id"].astype(str)
        enrollments_df["student_id"] = enrollments_df["student_id"].astype(str)
        enrollments_df["course_id"] = enrollments_df["course_id"].astype(str)
        courses_df["course_id"] = courses_df["course_id"].astype(str)

        student_enrollments = pd.merge(
            enrollments_df, students_df, on="student_id", how="inner"
        )
        student_courses = pd.merge(
            student_enrollments, courses_df, on="course_id", how="inner"
        )

        available_cols = [
            col
            for col in ["student_id", "name", "course_id", "course_name"]
            if col in student_courses.columns
        ]
        return student_courses[available_cols].to_dict(orient="records")
    except Exception as e:
        return {"error": str(e)}


# 11.Write a Python function to search for a student by name (partial matches allowed using LIKE).


@app.get("/search_student")
def search_student(name: str):
    matched_students = students_df[
        students_df["name"].str.contains(name, case=False, na=False)
    ]

    if matched_students.empty:
        return {"message": f"No students found matching '{name}'"}

    return matched_students.to_dict(orient="records")


# 13.Create a program to count how many students are enrolled per course and display results in descending order.


@app.get("/students_per_course")
def students_per_course():
    counts = enrollments_df.groupby("course_id")["student_id"].nunique().reset_index()
    counts.rename(columns={"student_id": "student_count"}, inplace=True)

    counts = pd.merge(counts, courses_df, on="course_id", how="left")

    result = counts[["course_id", "course_name", "student_count"]].sort_values(
        by="student_count", ascending=False
    )

    return result.to_dict(orient="records")


# 14.Write a Python script that accepts a course name as input and returns all enrolled students with their grades.


@app.get("/students_by_course_name")
def students_by_course_name(course_name: str):

    matched_courses = courses_df[
        courses_df["course_name"].str.contains(course_name, case=False, na=False)
    ]

    if matched_courses.empty:
        return {"message": f"No course found matching '{course_name}'"}

    course_ids = matched_courses["course_id"].tolist()

    filtered_enrollments = enrollments_df[enrollments_df["course_id"].isin(course_ids)]

    if filtered_enrollments.empty:
        return {"message": f"No students enrolled in '{course_name}'"}

    result = pd.merge(filtered_enrollments, students_df, on="student_id", how="left")

    result = result[["student_id", "name", "course_id", "grade"]]

    return result.to_dict(orient="records")
