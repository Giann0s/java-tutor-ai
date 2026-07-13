from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User, Topic
from app.core.config import settings


# Αν δεν υπάρχει admin δημιουργείται ο πρώτος
def create_first_admin(db: Session):
    admin = db.query(User).filter(User.role == "admin").first()

    if not admin:
        first_admin = User(
            email=settings.admin_email,
            first_name="Admin",
            last_name="",
            hashed_password=hash_password(settings.admin_password),
            role="admin",
            is_active=True
        )

        db.add(first_admin)
        db.commit()


def create_default_topics(db: Session):
    topics = db.query(Topic).first()

    if not topics:
        default_topics = [
            Topic(
                name="Java Variables",
                description="Sting, int, float, char, boolean and variable declaration."
            ),
            Topic(
                name="Java Data Types",
                description="Primitive data types (byte, short, int, long, float, double, boolean, char) and "
                            "non-primitive types."
            ),
            Topic(
                name="Java Operators",
                description="Arithmetic, assignment, comparison, logical and bitwise operators."
            ),
            Topic(
                name="Java Math and Booleans",
                description="Using the Math class (max, min, sqrt, abs, random) and boolean expressions."
            ),
            Topic(
                name="Java if...else",
                description="Conditional statements (if, else, else if) and the ternary operator."
            ),
            Topic(
                name="Java Switch",
                description="The switch statement, case execution, and the break keyword."
            ),
            Topic(
                name="Java Loops",
                description="While loop, Do/while loop, For loop, and For-Each loop."
            ),
            Topic(
                name="Java Arrays",
                description="Declaring, accessing, changing, looping through, and multidimensional arrays."
            ),
            Topic(
                name="Java Classes and Objects",
                description="OOP basics: creating classes, objects and accessing attributes."
            ),
            Topic(
                name="Java Class Methods",
                description="Creating methods inside classes, calling methods and public vs. static methods."
            )
        ]
        db.add_all(default_topics)
        db.commit()

