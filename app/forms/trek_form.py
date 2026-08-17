from datetime import date

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    IntegerField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import (
    DataRequired,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)

from app.models.trek_model import Trek


class TrekForm(FlaskForm):
    """
    Form used to create and update a Trek.
    """

    # ------------------------------------------------------------------
    # Trek Details
    # ------------------------------------------------------------------

    name = StringField(
        "Trek Name",
        validators=[
            DataRequired(),
            Length(min=2, max=150),
        ],
    )

    location = StringField(
        "Location",
        validators=[
            DataRequired(),
            Length(max=150),
        ],
    )

    difficulty = SelectField(
        "Difficulty",
        choices=[
            (Trek.DIFFICULTY_EASY, "Easy"),
            (Trek.DIFFICULTY_MODERATE, "Moderate"),
            (Trek.DIFFICULTY_DIFFICULT, "Difficult"),
        ],
        validators=[
            DataRequired(),
        ],
    )

    description = TextAreaField(
        "Description",
        validators=[
            Length(max=2000),
        ],
    )

    # ------------------------------------------------------------------
    # Trek Schedule
    # ------------------------------------------------------------------

    start_date = DateField(
        "Start Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(),
        ],
    )

    end_date = DateField(
        "End Date",
        format="%Y-%m-%d",
        validators=[
            DataRequired(),
        ],
    )

    # ------------------------------------------------------------------
    # Trek Capacity
    # ------------------------------------------------------------------

    total_slots = IntegerField(
        "Total Slots",
        validators=[
            DataRequired(),
            NumberRange(min=1, max=500),
        ],
    )

    # ------------------------------------------------------------------
    # Staff Assignment
    # ------------------------------------------------------------------

    staff_id = SelectField(
        "Assign Staff",
        coerce=int,
        validators=[
            Optional(),
        ],
    )

    # ------------------------------------------------------------------
    # Submit Button
    # ------------------------------------------------------------------

    submit = SubmitField("Save Trek")

    # ------------------------------------------------------------------
    # Custom Validations
    # ------------------------------------------------------------------

    def validate_start_date(self, field):
        """
        Start date cannot be in the past.
        """
        if field.data and field.data < date.today():
            raise ValidationError(
                "Start date cannot be in the past."
            )

    def validate_end_date(self, field):
        """
        End date must be on or after the start date.
        """
        if (
            self.start_date.data
            and field.data
            and field.data < self.start_date.data
        ):
            raise ValidationError(
                "End date must be on or after the start date."
            )
