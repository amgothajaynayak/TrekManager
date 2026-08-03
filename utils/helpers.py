from flask import flash

def flash_errors(form):
    """Iterates through form validation errors and flashes them."""
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in the {getattr(form, field).label.text} field - {error}", 'error')

def format_date(date_obj):
    """Returns formatted date string or empty string."""
    if date_obj:
        return date_obj.strftime('%Y-%m-%d')
    return ""
