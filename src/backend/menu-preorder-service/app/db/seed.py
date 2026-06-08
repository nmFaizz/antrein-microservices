import uuid
from sqlmodel import Session, SQLModel, select
from app.db.database import engine
from app.menu.models import Menu, MenuCategory
from app.preorder.models import Preorder, PreorderItem

# ==========================================
# DATA DUMMY MENU
# ==========================================
DUMMY_MENUS = [
    {
        "name": "Nasi Goreng Spesial",
        "description": "Nasi goreng pedas gurih dengan telur mata sapi, bakso, dan sosis.",
        "price": 18000.0,
        "category": MenuCategory.MAKANAN,
        "is_available": True,
    },
    {
        "name": "Mie Goreng Jawa",
        "description": "Mie goreng tradisional khas Jawa dengan kol, sayur hijau, dan suwiran ayam.",
        "price": 15000.0,
        "category": MenuCategory.MAKANAN,
        "is_available": True,
    },
    {
        "name": "Ayam Geprek Sambal Korek",
        "description": "Ayam goreng tepung renyah digeprek dengan sambal bawang korek pedas mantap.",
        "price": 20000.0,
        "category": MenuCategory.MAKANAN,
        "is_available": True,
    },
    {
        "name": "Es Teh Manis",
        "description": "Es teh manis segar beraroma melati.",
        "price": 5000.0,
        "category": MenuCategory.MINUMAN,
        "is_available": True,
    },
    {
        "name": "Kopi Susu Gula Aren",
        "description": "Es kopi espresso robusta dicampur susu segar dan gula aren murni.",
        "price": 12000.0,
        "category": MenuCategory.MINUMAN,
        "is_available": True,
    },
]

def seed_db():
    print("=== DATABASE SEEDER ===")
    print("Menginisialisasi tabel database jika belum ada...")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Cek apakah menu sudah ada datanya agar tidak duplikat
        existing_menu = session.exec(select(Menu)).first()
        if existing_menu:
            print("Database sudah memiliki data menu. Proses seeder dibatalkan.")
            return

        print("Memasukkan data menu dummy...")
        db_menus = []
        for menu_data in DUMMY_MENUS:
            menu_item = Menu(**menu_data)
            session.add(menu_item)
            db_menus.append(menu_item)
        
        session.commit()
        
        # Refresh untuk mengambil ID (UUID) yang digenerate database
        for menu_item in db_menus:
            session.refresh(menu_item)
        print(f"Berhasil menambahkan {len(db_menus)} menu.")

        # 2. Buat data Preorder dummy untuk keperluan testing
        print("Memasukkan data preorder dummy...")
        user_uuid = uuid.uuid4()
        
        # Instansiasi Preorder Induk
        dummy_preorder = Preorder(
            user_id=user_uuid,
            total_price=0.0,  # Akan dihitung di bawah
            status="pending",
            notes="Es teh manisnya satu jangan terlalu manis."
        )
        
        # Instansiasi Detail Item Pesanan (PreorderItem)
        item_1 = PreorderItem(
            menu_item_id=db_menus[0].id,  # Nasi Goreng Spesial
            quantity=1,
            subtotal=db_menus[0].price
        )
        item_2 = PreorderItem(
            menu_item_id=db_menus[3].id,  # Es Teh Manis
            quantity=2,
            subtotal=db_menus[3].price * 2
        )
        
        # Gabungkan item ke preorder induk
        dummy_preorder.items = [item_1, item_2]
        dummy_preorder.total_price = item_1.subtotal + item_2.subtotal
        
        session.add(dummy_preorder)
        session.commit()
        print("Berhasil menambahkan data preorder dummy.")
        print("=========================")
        print("Proses Seeding Selesai!")

if __name__ == "__main__":
    seed_db()
