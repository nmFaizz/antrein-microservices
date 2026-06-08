from sqlmodel import Session, SQLModel, select

from app.db.session import engine
from app.lib.security import hash_password
from app.models.user import User, UserRole

DUMMY_USERS = [
    {"username": "user1", "password": "password123", "role": UserRole.USER},
    {"username": "user2", "password": "password123", "role": UserRole.USER},
    {"username": "user3", "password": "password123", "role": UserRole.USER},
    {"username": "admin1", "password": "adminpass123", "role": UserRole.ADMIN},
    {"username": "admin2", "password": "adminpass123", "role": UserRole.ADMIN},
    {"username": "admin3", "password": "adminpass123", "role": UserRole.ADMIN},
]


def seed_db():
    print("=== DATABASE SEEDER ===")
    print("Menginisialisasi tabel database jika belum ada...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing_user = session.exec(select(User)).first()
        if existing_user:
            print("Database sudah memiliki data user. Proses seeder dibatalkan.")
            return

        print("Memasukkan data user dummy...")
        db_users = []
        for user_data in DUMMY_USERS:
            user = User(
                username=user_data["username"],
                password=hash_password(user_data["password"]),
                role=user_data["role"],
            )
            session.add(user)
            db_users.append(user)

        session.commit()
        print(f"Berhasil menambahkan {len(db_users)} user.")
        print("=========================")
        print("Proses Seeding Selesai!")


if __name__ == "__main__":
    seed_db()
