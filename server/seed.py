
from app import app
from models import db, User, Note

with app.app_context():

    print("Clearing old data...")

    # start by deleting notes
    Note.query.delete()
    User.query.delete()
    db.session.commit()
    print("Old data cleared.")

    # ── Create Users ──
    print("Seeding users...")

    alice = User(username="alice")
    alice.password = "password123"   

    bob = User(username="bob")
    bob.password = "securepass456"

    charlie = User(username="charlie")
    charlie.password = "charliepass"

    db.session.add_all([alice, bob, charlie])
    db.session.commit()
    print(f"  Created {User.query.count()} users.")

    # Create Notes
    print("Seeding notes...")

    # Alice's notes
    note1 = Note(
        title="Morning Routine",
        content="Wake up at 6am, stretch, drink water, then code for 2 hours.",
        user_id=alice.id
    )
    note2 = Note(
        title="Flask Tips",
        content="Always use @before_request to check login state. Use session.clear() on logout.",
        user_id=alice.id
    )
    note3 = Note(
        title="Study Plan",
        content="Week 1: Models. Week 2: Routes. Week 3: Auth. Week 4: Deploy.",
        user_id=alice.id
    )

    # Bob's notes
    note4 = Note(
        title="Workout Log",
        content="Monday: Push day. Tuesday: Pull day. Wednesday: Rest.",
        user_id=bob.id
    )
    note5 = Note(
        title="Shopping List",
        content="Eggs, milk, bread, chicken, rice, vegetables.",
        user_id=bob.id
    )

    # Charlie's notes
    note6 = Note(
        title="Book Recommendations",
        content="Clean Code by Robert Martin. The Pragmatic Programmer. You Don't Know JS.",
        user_id=charlie.id
    )

    db.session.add_all([note1, note2, note3, note4, note5, note6])
    db.session.commit()
    print(f"  Created {Note.query.count()} notes.")

    # Summary
    print("\nSeeding complete! Summary:")
    print(f"  Users: {User.query.count()}")
    print(f"  Notes: {Note.query.count()}")
    print("\nSample — Alice's notes:")
    for note in alice.notes:
        print(f"  - [{note.id}] {note.title}")