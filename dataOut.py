from datetime import datetime
from num2words import num2words
from dateutil.relativedelta import relativedelta


def convert_float_to_duration_text_arithmetic(years_float):
    total_days = years_float * 365.25  # Total days, accounting for leap years
    years = int(total_days // 365.25)
    remaining_days = total_days % 365.25
    months = int(remaining_days // (365.25 / 12))
    days = int(remaining_days % (365.25 / 12))

    # Convert numbers to words
    years_text = num2words(years)
    months_text = num2words(months)
    days_text = num2words(days)

    # Formulate the duration text
    duration_text = f"{years_text} years and {months_text} months and {days_text} days"
    return duration_text

def create_text(data):
    """
    Creates a text summary from a data dictionary with keys:
      - education: a list of dictionaries with keys 'degree' and 'institute'
      - experience: a list of dictionaries with keys 'role', 'startDate', 'endDate'
      - skills: a list of skill strings
      
    The output text will be in the form:
      "The user has <degree> at <institute>. ...  Worked as <role> for <duration_output> years. ... With the skill set of <skill1, skill2, ...>."
    
    For each education item, a sentence is generated.
    For each experience item, the duration (in years) is computed from the start and end dates.
    """
    output_parts = []

    # Process education entries
    education_entries = data.get("education", [])
    if education_entries:
        edu_sentences = []
        for edu in education_entries:
            degree = edu.get("degree", "an unknown degree")
            institute = edu.get("institute", "an unknown institute")
            edu_sentences.append(f"{degree} at {institute}.")
        output_parts.append(" ".join(edu_sentences))

    # Process experience entries
    experience_entries = data.get("experience", [])
    if experience_entries:
        exp_sentences = []
        for exp in experience_entries:
            role = exp.get("role", "an unspecified role")
            start_date_str = exp.get("startDate")
            end_date_str = exp.get("endDate")
            # Default duration text if dates are missing or invalid
            duration_text = "an unknown duration"

            # If both dates exist, attempt to compute the duration in years
            if start_date_str and end_date_str:
                try:
                    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                    delta = end_date - start_date
                    # Convert days to years (approximate conversion)
                    duration_in_years = delta.days / 365.0
                    duration_text = convert_float_to_duration_text_arithmetic(duration_in_years)
                    # duration_text = f"{duration_in_years:.2f}"
                except Exception as e:
                    # In case of any error, leave the duration as unknown
                    duration_text = "an unknown duration"
            exp_sentences.append(f"Worked as {role} for {duration_text}.")
        output_parts.append(" ".join(exp_sentences))
    
    # Process skills
    skills = data.get("skills", [])
    if skills:
        skills_text = "Has the skill set of " + ", ".join(skills) + "."
        output_parts.append(skills_text)
    
    # Combine all parts into one output string
    text = " ".join(output_parts)
    return text
